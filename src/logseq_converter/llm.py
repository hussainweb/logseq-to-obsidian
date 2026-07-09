import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from openai import OpenAI

from logseq_converter.utils import generate_content_filename, sanitize_filename


class LLMClient:
    @property
    def provider(self) -> str:
        raise NotImplementedError()

    @property
    def max_workers(self) -> int:
        raise NotImplementedError()

    def resolve_batch(self, items: list[tuple[str, list[str]]], on_resolve=None) -> list[str]:
        raise NotImplementedError()


class RuleBasedFilenameClient(LLMClient):
    @property
    def provider(self) -> str:
        return "none"

    @property
    def max_workers(self) -> int:
        return 1

    def resolve_batch(self, items: list[tuple[str, list[str]]], on_resolve=None) -> list[str]:
        # Fast, local, rule-based generation fallback
        results = []
        for idx, (desc, _) in enumerate(items):
            filename = sanitize_filename(generate_content_filename(desc))
            results.append(filename)
            if on_resolve:
                on_resolve(idx, filename)
        return results


class BaseLLMClient(LLMClient):
    def __init__(self, model: str, client: OpenAI):
        self.model = model
        self.client = client

    @property
    def max_workers(self) -> int:
        raise NotImplementedError()

    def generate_filename_llm(self, description: str, sub_items: list[str]) -> Optional[str]:
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
                temperature=0.3,
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
        # Strip wrapping quotes, spaces, and backticks (custom character trim)
        filename = raw_filename.strip(" '\"`\t\n\r")

        # Strip trailing extension if the model added it
        for ext in (".md", ".markdown", ".txt"):
            if filename.lower().endswith(ext):
                filename = filename[: -len(ext)].strip(" '\"`\t\n\r")

        # Length enforcement guardrails (limit to 15 words / 80 characters)
        words = filename.split()
        if len(words) > 15 or len(filename) > 80:
            filename = " ".join(words[:6])

        # Sanitize filename
        sanitized = sanitize_filename(filename)
        if not sanitized or sanitized.strip() == "":
            return sanitize_filename(generate_content_filename(description))

        return sanitized

    def resolve_batch(self, items: list[tuple[str, list[str]]], on_resolve=None) -> list[str]:
        total_pending = len(items)
        completed_count = 0
        results = [None] * total_pending

        def process_item(idx: int) -> tuple[int, str]:
            description, sub_items = items[idx]
            raw_filename = self.generate_filename_llm(description, sub_items)
            if raw_filename:
                processed = self.post_process_filename(raw_filename, description)
            else:
                processed = sanitize_filename(generate_content_filename(description))
            return idx, processed

        max_workers = min(self.max_workers, total_pending)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {executor.submit(process_item, idx): idx for idx in range(total_pending)}

            for future in as_completed(future_to_idx):
                idx, filename = future.result()
                results[idx] = filename
                
                if on_resolve:
                    on_resolve(idx, filename)

                completed_count += 1
                percent = int((completed_count / total_pending) * 100)
                sys.stderr.write(
                    f"\rGenerating filenames: {completed_count}/{total_pending} complete ({percent}%)..."
                )
                sys.stderr.flush()

        return results


class OpenRouterLLMClient(BaseLLMClient):
    @property
    def provider(self) -> str:
        return "openrouter"

    @property
    def max_workers(self) -> int:
        return 15

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        if not api_key:
            raise ValueError("OpenRouter requires LSC_API_KEY")
        model_name = model or "google/gemini-2.5-flash-lite"
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            timeout=30.0,
        )
        super().__init__(model_name, client)


class OllamaLLMClient(BaseLLMClient):
    @property
    def provider(self) -> str:
        return "ollama"

    @property
    def max_workers(self) -> int:
        return 1

    def __init__(self, ollama_host: Optional[str] = None, model: Optional[str] = None):
        model_name = model or "gemma4:e4b"
        host = ollama_host or "http://localhost:11434"
        
        # Standardize host with protocol
        if not host.startswith(("http://", "https://")):
            host = f"http://{host}"
            
        # Parse protocol and host part
        proto = "https://" if host.startswith("https://") else "http://"
        host_part = host[len(proto):]
        
        # Default Ollama port to 11434 if no port is explicitly specified
        if ":" not in host_part:
            host_part = f"{host_part.rstrip('/')}:11434"
            
        # Reconstruct base URL
        host = f"{proto}{host_part}"
        if not host.endswith("/v1") and not host.endswith("/v1/"):
            host = host.rstrip("/") + "/v1"
            
        client = OpenAI(
            base_url=host,
            api_key="ollama",
            timeout=180.0,  # 3-minute timeout for slow local machines
        )
        super().__init__(model_name, client)


def create_llm_client(env: dict[str, str]) -> LLMClient:
    """
    Factory to resolve the provider and instantiate the correct LLMClient.
    """
    provider = env.get("LSC_LLM")
    api_key = env.get("LSC_API_KEY")
    ollama_host = env.get("OLLAMA_HOST")
    model = env.get("LSC_MODEL")

    if not provider:
        if api_key:
            provider = "openrouter"
        elif ollama_host:
            provider = "ollama"
        else:
            provider = "none"

    provider = provider.lower().strip()

    if provider == "openrouter":
        return OpenRouterLLMClient(api_key=api_key, model=model)
    elif provider == "ollama":
        return OllamaLLMClient(ollama_host=ollama_host, model=model)

    return RuleBasedFilenameClient()


class LLMFilenameGenerator:
    def __init__(self, env: dict[str, str]):
        self.env = env
        self.client = create_llm_client(self.env)
        self.cache_path = self._get_cache_path()
        self.cache = self._load_cache()

    @property
    def provider(self) -> str:
        return self.client.provider

    def _get_cache_path(self) -> Path:
        if os.name == "nt":
            base = Path(self.env.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
        else:
            base = Path(self.env.get("XDG_CACHE_HOME") or Path.home() / ".cache")

        return base / "logseq-converter" / "filename_cache.json"

    def _load_cache(self) -> dict[str, str]:
        if not self.cache_path.exists():
            return {}
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_cache(self) -> None:
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass

    def clear_cache(self) -> None:
        if not self.cache_path.exists():
            self.cache = {}
            return
        try:
            self.cache_path.unlink()
        except Exception:
            pass
        self.cache = {}

    def get_content_hash(self, description: str, sub_items: list[str]) -> str:
        content = f"{description}\n" + "\n".join(sub_items)
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def resolve_filenames_batch(
        self, items: list[tuple[str, list[str]]]  # List of (description, sub_items)
    ) -> list[str]:
        results = [None] * len(items)
        pending_indices = []

        for idx, (description, sub_items) in enumerate(items):
            checksum = self.get_content_hash(description, sub_items)
            if checksum in self.cache:
                results[idx] = self.cache[checksum]
            else:
                pending_indices.append(idx)

        total_pending = len(pending_indices)

        sys.stderr.write(
            f"LLM filename generation: {len(items) - total_pending} cached, {total_pending} pending...\n"
        )
        sys.stderr.flush()

        if total_pending == 0:
            return results

        # Define a callback to save cache progressively
        def on_resolve(pending_idx: int, filename: str):
            idx = pending_indices[pending_idx]
            description, sub_items = items[idx]
            checksum = self.get_content_hash(description, sub_items)
            self.cache[checksum] = filename

            # Periodically write to disk (every 5 items resolved)
            on_resolve.counter += 1
            if on_resolve.counter % 5 == 0:
                self._save_cache()

        on_resolve.counter = 0

        # Delegate batch resolution to the client
        pending_items = [items[idx] for idx in pending_indices]
        resolved_pending = self.client.resolve_batch(pending_items, on_resolve=on_resolve)

        # Reconstruct results and save to cache
        for i, idx in enumerate(pending_indices):
            filename = resolved_pending[i]
            results[idx] = filename

            description, sub_items = items[idx]
            checksum = self.get_content_hash(description, sub_items)
            self.cache[checksum] = filename

        # Only print the finished message if we resolved items via an API-based client (which prints progress)
        if not isinstance(self.client, RuleBasedFilenameClient):
            sys.stderr.write(f"\rGenerating filenames: {total_pending}/{total_pending} complete. Done.\n")
            sys.stderr.flush()

        self._save_cache()
        return results

    def resolve_placeholders(self, extracted_files: list[tuple[str, str]]) -> list[tuple[str, str]]:
        placeholders_to_resolve = []

        for idx, (filename, file_content) in enumerate(extracted_files):
            basename = os.path.basename(filename)
            if "__PENDING_LLM__" in basename:
                parts = basename.split("__")
                if len(parts) >= 4:
                    checksum = parts[2]
                    fallback_with_ext = parts[3]
                    fallback = fallback_with_ext[:-3] if fallback_with_ext.endswith(".md") else fallback_with_ext
                    placeholders_to_resolve.append((idx, filename, file_content, checksum, fallback))

        if not placeholders_to_resolve:
            return extracted_files

        batch_items = []
        for _, _, file_content, _, _ in placeholders_to_resolve:
            description, sub_items = self._parse_item_from_content(file_content)
            batch_items.append((description, sub_items))

        resolved_basenames = self.resolve_filenames_batch(batch_items)

        final_files = list(extracted_files)
        for i, (idx, filename, file_content, _, _) in enumerate(placeholders_to_resolve):
            resolved_base = resolved_basenames[i]
            dir_name = os.path.dirname(filename)
            new_basename = f"{resolved_base}.md"
            new_filename = os.path.join(dir_name, new_basename) if dir_name else new_basename
            final_files[idx] = (new_filename, file_content)

        return final_files

    def _parse_item_from_content(self, file_content: str) -> tuple[str, list[str]]:
        lines = file_content.split("\n")
        start_idx = 0
        if lines and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    start_idx = i + 1
                    break

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
