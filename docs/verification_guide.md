# Verification & Manual Testing Guide

This guide provides steps to manually verify the behavior of the LogSeq Converter CLI commands, ensuring the correctness of the conversion pipeline across different target platforms.

---

## 🧪 Step 1: Create a Sandbox Copy of your LogSeq Vault

To perform manual verification safely without risking your live production notes, create a temporary copy of your existing LogSeq graph directory.

1. Copy your LogSeq vault to a temporary location (e.g., `~/logseq-bak`):
   ```bash
   cp -R ~/logseq ~/logseq-bak
   ```

   *Note: Adjust `~/logseq` if your actual LogSeq graph directory is stored at a different path.*

---

## 🎯 Step 2: Verify Obsidian Conversion

Run the `obsidian` subcommand against the sandbox path:
```bash
uv run python -m logseq_converter.cli obsidian ~/logseq-bak ~/obsidian-vault-test
```

### Verification Checklist:
- [ ] **Daily Folder**: A directory named `Daily/` should exist, containing daily journal notes formatted as `YYYY-MM-DD.md`.
- [ ] **Namespace Nesting**: Pages using LogSeq namespaces (e.g., `A___B.md`) should be converted into nested folders and files (e.g., `A/B.md`).
- [ ] **Clean Daily Note**: Opening a converted journal note should:
  - Have any custom properties/blocks stripped or converted correctly based on your settings.
  - Not contain raw `:LOGBOOK:` or block properties.
- [ ] **Extracted Folders**: If your vault contains extracted tag sections (e.g., links, learnings, highlights as defined in your configuration), check that corresponding subdirectories (like `Links/`, `Learnings/`, `Highlights/`) are created with extracted standalone markdown files.
- [ ] **Clean Page Note**: Opening a converted page should:
  - Contain clean YAML frontmatter with tags, aliases, and properties mapped to frontmatter.
  - Have standard markdown links instead of LogSeq-specific block brackets where appropriate.
  - Contain converted block references (e.g., `[[Daily/YYYY-MM-DD#^anchor]]` or matching section anchors).

---

## 🔮 Step 3: Verify Tana Export

Run the `tana` subcommand:
```bash
uv run python -m logseq_converter.cli tana ~/logseq-bak ~/tana-import-test.json --force
```

### Verification Checklist:
- [ ] **JSON Document**: Check that `~/tana-import-test.json` is successfully created.
- [ ] **Tana Structure**: Open the JSON file and verify:
  - It contains a valid JSON object structure conforming to Tana Intermediate Format.
  - Page nodes contain child nodes matching your original LogSeq bullet points.

---

## 🔮 Step 4: Verify Tolaria Conversion

Run the `tolaria` subcommand:
```bash
uv run python -m logseq_converter.cli tolaria ~/logseq-bak ~/tolaria-vault-test
```

### Verification Checklist:
- [ ] **Journal Path**: Check that daily journals are placed under `journal/` (e.g., `journal/YYYY-MM-DD.md`).
- [ ] **Frontmatter Type**: Opening a converted journal note shows `type: journal` in YAML frontmatter.
- [ ] **Clean Block IDs**: Verify that `id:: uuid` strings are completely removed.

---

## 🔮 Step 5: Verify Blinko Sync (Dry Run)

Run the `blinko` subcommand in dry-run mode:
```bash
export BLINKO_TOKEN="mock-token"
uv run python -m logseq_converter.cli blinko ~/logseq-bak https://example.com/api --dry-run
```

### Verification Checklist:
- [ ] **No Networking**: Verify that the command executes without throwing authentication/connection errors since `--dry-run` bypasses direct network calls.
- [ ] **Logs**: Verify console output indicates notes are being processed for export.

