import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from openai import OpenAI
from logseq_converter.utils import generate_content_filename, sanitize_filename


class LLMFilenameGenerator:
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        # Resolve provider based on user instructions and environment variables
        api_key = os.environ.get("LSC_API_KEY")
        ollama_host = os.environ.get("OLLAMA_HOST")

        # Explicit provider setting overrides auto-detection
        resolved_provider = provider or os.environ.get("LSC_LLM")

        if resolved_provider is None:
            # Auto-detection rules
            if api_key:
                resolved_provider = "openrouter"
            elif ollama_host:
                resolved_provider = "ollama"
            else:
                resolved_provider = "none"

        self.provider = resolved_provider.lower().strip() if resolved_provider else "none"

        # Resolve model, respecting overrides
        env_model = model or os.environ.get("LSC_MODEL")

        if self.provider == "openrouter":
            self.model = env_model or "google/gemini-2.5-flash-lite"
            self.base_url = "https://openrouter.ai/api/v1"
            self.api_key = api_key or "missing-key"
        elif self.provider == "ollama":
            self.model = env_model or "qwen3:4b"
            # Standardize Ollama endpoint URL
            host = ollama_host or "http://localhost:11434"
            if not host.startswith(("http://", "https://")):
                host = f"http://{host}"
            if not host.endswith("/v1") and not host.endswith("/v1/"):
                host = host.rstrip("/") + "/v1"
            self.base_url = host
            self.api_key = "ollama"  # OpenAI client needs a non-empty placeholder key
        else:
            self.model = ""
            self.base_url = ""
            self.api_key = ""

        self.client = None
        if self.provider != "none":
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=30.0,
            )

        self.cache_path = self._get_cache_path()
        self.cache = self._load_cache()

    def _get_cache_path(self) -> Path:
        # Cross-platform cache directory resolution (safe for macOS, Linux, Windows)
        if os.name == "nt":
            base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
        else:
            base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")

        return base / "logseq-converter" / "filename_cache.json"

    def _load_cache(self) -> Dict[str, str]:
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self) -> None:
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass

    def clear_cache(self) -> None:
        if self.cache_path.exists():
            try:
                self.cache_path.unlink()
            except Exception:
                pass
        self.cache = {}

    def get_content_hash(self, description: str, sub_items: List[str]) -> str:
        # Concatenate description and sub-items to generate a distinct SHA-256 checksum
        content = f"{description}\n" + "\n".join(sub_items)
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def generate_filename_llm(self, description: str, sub_items: List[str]) -> Optional[str]:
        if self.provider == "none" or not self.client:
            return None

        prompt_content = f"{description}\n" + "\n".join(sub_items)

        system_prompt = (
            "You are a utility that generates concise, descriptive, and web-safe file names for journal notes. "
            "Output ONLY the raw filename. Do NOT include any introduction, explanations, markdown formatting, "
            "quotes, or file extensions (do not add .md). Target a length of 3 to 6 words, but you may use up "
            "to a maximum of 15 words if essential to maintain descriptive precision."
        )

        user_prompt = f"Summarize the following note content into a filename:\nContent:\n{prompt_content}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                max_tokens=60,
            )
            filename = response.choices[0].message.content
            if filename:
                return filename.strip()
        except Exception as e:
            from logseq_converter.utils import log_warning

            log_warning(f"LLM generation failed: {e}")
            return None

    def post_process_filename(self, raw_filename: str, description: str) -> str:
        filename = raw_filename.strip()

        # Remove wrapping quotes
        if (filename.startswith('"') and filename.endswith('"')) or (
            filename.startswith("'") and filename.endswith("'")
        ):
            filename = filename[1:-1].strip()

        # Remove wrapping markdown code formatting
        if filename.startswith("`") and filename.endswith("`"):
            filename = filename[1:-1].strip()

        # Strip trailing extension if the model added it
        for ext in (".md", ".markdown", ".txt"):
            if filename.lower().endswith(ext):
                filename = filename[: -len(ext)].strip()

        # Length enforcement guardrails (limit to 15 words / 80 characters)
        words = filename.split()
        if len(words) > 15 or len(filename) > 80:
            filename = " ".join(words[:6])

        # Sanitize filename (removes markdown links, logseq tags, illegal characters)
        sanitized = sanitize_filename(filename)
        if not sanitized or sanitized.strip() == "":
            return sanitize_filename(generate_content_filename(description))

        return sanitized

    def resolve_filenames_batch(
        self, items: List[Tuple[str, List[str]]]  # List of (description, sub_items)
    ) -> List[str]:
        results = [None] * len(items)
        pending_indices = []

        # 1. Cache lookup using SHA-256
        for idx, (description, sub_items) in enumerate(items):
            checksum = self.get_content_hash(description, sub_items)
            if checksum in self.cache:
                results[idx] = self.cache[checksum]
            else:
                pending_indices.append(idx)

        total_pending = len(pending_indices)

        # Print initial status to stderr
        sys.stderr.write(
            f"LLM filename generation: {len(items) - total_pending} cached, {total_pending} pending...\n"
        )
        sys.stderr.flush()

        if total_pending == 0:
            return results

        # If LLM is disabled, immediately resolve pending using rule-based fallback
        if self.provider == "none":
            for idx in pending_indices:
                description, _ = items[idx]
                results[idx] = sanitize_filename(generate_content_filename(description))
            return results

        # 2. Parallel LLM execution for pending items
        completed_count = 0

        def process_item(idx: int) -> Tuple[int, str]:
            description, sub_items = items[idx]
            raw_filename = self.generate_filename_llm(description, sub_items)
            if raw_filename:
                processed = self.post_process_filename(raw_filename, description)
            else:
                processed = sanitize_filename(generate_content_filename(description))
            return idx, processed

        max_workers = min(15, total_pending)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {executor.submit(process_item, idx): idx for idx in pending_indices}

            for future in as_completed(future_to_idx):
                idx, filename = future.result()
                results[idx] = filename

                # Update the cache
                description, sub_items = items[idx]
                checksum = self.get_content_hash(description, sub_items)
                self.cache[checksum] = filename

                completed_count += 1
                percent = int((completed_count / total_pending) * 100)
                sys.stderr.write(
                    f"\rGenerating filenames: {completed_count}/{total_pending} complete ({percent}%)..."
                )
                sys.stderr.flush()

        # Save cache and clear stderr line
        self._save_cache()
        sys.stderr.write(f"\rGenerating filenames: {total_pending}/{total_pending} complete. Done.\n")
        sys.stderr.flush()

        return results

    def resolve_placeholders(self, extracted_files: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """
        Scans a list of (filename, file_content) tuples for LLM placeholders,
        resolves them in batch, and returns a new list of (filename, file_content) tuples.
        """
        placeholders_to_resolve = []  # list of (index, relative_path, file_content, checksum, fallback)

        for idx, (filename, file_content) in enumerate(extracted_files):
            basename = os.path.basename(filename)
            if "__PENDING_LLM__" in basename:
                # Format: __PENDING_LLM__{checksum}__{fallback}.md
                parts = basename.split("__")
                if len(parts) >= 4:
                    checksum = parts[2]
                    fallback_with_ext = parts[3]
                    fallback = fallback_with_ext[:-3] if fallback_with_ext.endswith(".md") else fallback_with_ext
                    placeholders_to_resolve.append((idx, filename, file_content, checksum, fallback))

        if not placeholders_to_resolve:
            return extracted_files

        # Extract description and sub-items for pending items
        batch_items = []
        for idx, filename, file_content, checksum, fallback in placeholders_to_resolve:
            description, sub_items = self._parse_item_from_content(file_content)
            batch_items.append((description, sub_items))

        # Resolve filenames in batch (checks cache first, then LLM)
        resolved_basenames = self.resolve_filenames_batch(batch_items)

        # Reconstruct the final list of files
        final_files = list(extracted_files)
        for i, (idx, filename, file_content, checksum, fallback) in enumerate(placeholders_to_resolve):
            resolved_base = resolved_basenames[i]
            # Replace placeholder in the path
            dir_name = os.path.dirname(filename)
            new_basename = f"{resolved_base}.md"
            new_filename = os.path.join(dir_name, new_basename) if dir_name else new_basename
            final_files[idx] = (new_filename, file_content)

        return final_files

    def _parse_item_from_content(self, file_content: str) -> Tuple[str, List[str]]:
        lines = file_content.split("\n")
        start_idx = 0
        # Skip frontmatter if present
        if lines and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    start_idx = i + 1
                    break

        # Extract description (first non-empty line)
        description = ""
        sub_items = []
        for i in range(start_idx, len(lines)):
            line = lines[i]
            if not description:
                if line.strip():
                    description = line.strip()
            else:
                sub_items.append(line)

        return description, sub_items

