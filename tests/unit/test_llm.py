from logseq_converter.llm import LLMFilenameGenerator, OllamaLLMClient, OpenRouterLLMClient


def test_provider_resolution():
    # Test fallback with no params
    generator = LLMFilenameGenerator()
    assert generator.provider == "none"

    # Test auto-detection: api_key set
    generator = LLMFilenameGenerator(api_key="sk-or-12345")
    assert generator.provider == "openrouter"
    assert isinstance(generator.client, OpenRouterLLMClient)
    assert generator.client.model == "google/gemini-2.5-flash-lite"

    # Test auto-detection: ollama_host set
    generator = LLMFilenameGenerator(ollama_host="http://192.168.1.10:11434")
    assert generator.provider == "ollama"
    assert isinstance(generator.client, OllamaLLMClient)
    assert generator.client.model == "qwen3:4b"

    # Test explicit override provider
    generator = LLMFilenameGenerator(provider="none", api_key="sk-or-12345")
    assert generator.provider == "none"

    # Test explicit model override
    generator = LLMFilenameGenerator(provider="ollama", model="mistral")
    assert generator.provider == "ollama"
    assert generator.client.model == "mistral"


def test_hashing_and_caching(tmp_path, monkeypatch):
    # Redirect cache path to tmp folder for isolation
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    generator = LLMFilenameGenerator()
    assert generator.cache_path.name == "filename_cache.json"

    description = "Learned how to test LLM code"
    sub_items = ["- detail 1", "- detail 2"]

    # Compute checksum
    hash_val = generator.get_content_hash(description, sub_items)
    assert len(hash_val) == 64  # SHA-256 hex length

    # Cache operations
    assert hash_val not in generator.cache
    generator.cache[hash_val] = "Testing LLM Code"
    generator._save_cache()

    # Create new generator instance to test loading from cache
    generator2 = LLMFilenameGenerator()
    assert generator2.cache.get(hash_val) == "Testing LLM Code"

    # Clear cache
    generator2.clear_cache()
    assert not generator2.cache_path.exists()
    assert len(generator2.cache) == 0


def test_post_process_filename():
    generator = LLMFilenameGenerator()

    # Test stripping markdown and quotes
    assert generator.post_process_filename(' "My Cool File" ', "desc") == "My Cool File"
    assert generator.post_process_filename("`Code Filename`", "desc") == "Code Filename"
    assert generator.post_process_filename("Filename.md", "desc") == "Filename"

    # Test sanitization
    assert generator.post_process_filename("Invalid/Name?", "desc") == "InvalidName"

    # Test length guardrails (limit is 15 words)
    long_name = " ".join(["Word"] * 20)
    processed_long = generator.post_process_filename(long_name, "desc")
    assert len(processed_long.split()) == 6


def test_resolve_placeholders(tmp_path, monkeypatch):
    # Redirect cache path to tmp folder for isolation
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    generator = LLMFilenameGenerator(provider="none")

    description = "Setting up FastAPI project"
    sub_items = ["- Add uvicorn", "- Write main.py"]
    checksum = generator.get_content_hash(description, sub_items)

    # Simulated converter output with placeholder
    extracted_files = [
        ("Links/Google.md", "Url link"),
        (
            f"Learnings/__PENDING_LLM__{checksum}__FastAPI Setup.md",
            f"---\ndate: 2025-11-27\n---\n\n{description}\n" + "\n".join(sub_items),
        ),
    ]

    resolved = generator.resolve_placeholders(extracted_files)

    assert len(resolved) == 2
    assert resolved[0] == ("Links/Google.md", "Url link")
    # Should resolve to the fallback name based on content under none provider
    assert resolved[1][0] == "Learnings/Setting up FastAPI project.md"
    assert resolved[1][1] == extracted_files[1][1]
