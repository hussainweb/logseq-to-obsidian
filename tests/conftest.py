import pytest


@pytest.fixture(autouse=True)
def disable_llm_for_tests(monkeypatch):
    # Enforce none mode for all tests by default
    monkeypatch.setenv("LSC_LLM", "none")
    monkeypatch.delenv("LSC_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
