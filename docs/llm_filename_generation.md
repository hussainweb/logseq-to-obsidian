# LLM-Based Filename Generation

The converter supports using a lightweight/cheap LLM (such as Qwen on Ollama or Gemini 2.5 Flash Lite on OpenRouter) to automatically generate descriptive, web-safe filenames for files extracted from Logseq journals (such as `#learnings`, `#achievements`, and `#highlights`). 

This replaces the default rule-based behavior (which simply takes the first few words of the entry) with semantic summarization.

---

## 1. How It Works

Instead of running LLM queries sequentially (which would block the converter for several minutes), the LLM integration uses a deferred, concurrent execution model:

1. **Extraction**: During the journal parsing loop, section content is extracted. If LLM mode is active, the converter generates a placeholder name containing a SHA-256 hash of the content (e.g., `__PENDING_LLM__<hash>__<fallback_name>.md`).
2. **Caching**: The SHA-256 hash of the extracted note's text is looked up in a global, cross-platform cache file (`filename_cache.json`).
   * **Cache Hit**: The cached filename is applied instantly.
   * **Cache Miss**: The item is queued for LLM resolution.
3. **Parallel Execution**: All queued cache misses are resolved concurrently using a thread pool of 10-15 workers. An in-place progress counter is output to the console.
4. **Collision & Writing**: Once all names are resolved, the cache is saved. Path naming collisions are resolved sequentially (appending `_1`, `_2`, etc., if multiple notes map to the same name), and the files are written.

---

## 2. Configuration & Environment Variables

LLM filename generation is enabled and configured entirely via environment variables, keeping the command-line interface clean.

### Environment Variables
*   `LSC_LLM`: Configures the LLM provider. Valid options are:
    *   `none`: (Default if auto-detection fails) Disables LLM filename generation.
    *   `ollama`: Resolves base URL from `OLLAMA_HOST` and defaults model to `gemma4:e4b`.
    *   `openrouter`: Resolves base URL to `https://openrouter.ai/api/v1` and defaults model to `google/gemini-2.5-flash-lite`.
*   `LSC_API_KEY`: The API key (required for OpenRouter; ignored for Ollama).
*   `LSC_MODEL`: Overrides the default model choice (e.g., `llama3.2` or `meta-llama/llama-3.2-3b-instruct`).
*   `OLLAMA_HOST`: The Ollama endpoint address (optional; defaults to `http://localhost:11434` if unset).

### Auto-Detection Rules
If `LSC_LLM` is not set explicitly, the provider is resolved dynamically using the following precedence:
1. If `LSC_API_KEY` is present $\rightarrow$ Defaults to `openrouter`.
2. Otherwise, if `OLLAMA_HOST` is present $\rightarrow$ Defaults to `ollama`.
3. Otherwise $\rightarrow$ Defaults to `none` (LLM disabled).

---

## 3. Caching and Invalidating

To minimize API latency and token cost, resolved filenames are cached in a user-level directory safe from destination directory purges:
*   **Linux / macOS**: `~/.cache/logseq-converter/filename_cache.json` (respects `XDG_CACHE_HOME` if set).
*   **Windows**: `%LOCALAPPDATA%\logseq-converter\filename_cache.json` (falls back to `~/AppData/Local` if unset).

### Invalidating the Cache
If you want to force the LLM to re-evaluate and rename all your notes, you can invalidate the cache in two ways:
1. Run the converter with the `--clear-llm-cache` command-line flag:
   ```bash
   uv run python -m logseq_converter.cli obsidian ~/notes ~/obsidian --clear-llm-cache
   ```
2. Manually delete the `filename_cache.json` file in your system's cache directory.

---

## 4. Prompt Constraints & Guardrails

The LLM is prompted with a strict system constraint:
* Target a length of 3 to 6 words (max 15 words if essential for precision).
* Output ONLY the raw filename without markdown formatting, quotes, or extensions.

### Client-Side Guardrails
In case a model fails to follow instructions (e.g. outputs conversational text), the code applies post-processing:
1. Strips wrapping quotes, markdown code tick marks, and trailing extensions (e.g. `.md`).
2. Runs the result through `sanitize_filename` to remove any unsafe characters.
3. If the resolved name is still longer than 15 words or 80 characters, it truncates it to the first 6 words.
4. If the resolved name is empty after sanitization, it falls back to the traditional rule-based filename generator.
