# Verification & Manual Testing Guide

This guide provides steps to manually verify the behavior of the LogSeq Converter CLI commands, ensuring the correctness of the conversion pipeline across different target platforms.

---

## 🧪 Step 1: Create a Mock LogSeq Graph

To perform verification without risking production notes, create a mock LogSeq graph structure.

1. Create the mock directories:
   ```bash
   mkdir -p mock-graph/journals
   mkdir -p mock-graph/pages
   mkdir -p mock-graph/assets
   ```

2. Add a sample daily journal file in `mock-graph/journals/2026_06_25.md`:
   ```markdown
   title:: June 25th, 2026
   collapsed:: false

   - This is a regular journal entry.
   - We did some work on block references:
     - Here is a block we want to refer to.
       id:: 12345678-abcd-1234-abcd-1234567890ab
   - #links
     - [LogSeq](https://logseq.com) ([GitHub](https://github.com/logseq/logseq))
       - Outliner notes app
     - [Obsidian](https://obsidian.md)
       - Markdown editor
   - #learnings
     - Learned that Python 3.14 is extremely fast.
       - It uses the new optimizer.
   - #highlights
     - Successfully deployed the converter.
   - :LOGBOOK:
     CLOCK: [2026-06-25 Thu 09:00]--[2026-06-25 Thu 10:00] =>  01:00
     :END:
     - Clean task line.
   ```

3. Add a sample namespace page in `mock-graph/pages/Software___Python.md`:
   ```markdown
   tags:: software, programming
   author:: John Doe
   heading:: true
   icon:: 🐍

   - Introduction to Python.
   - Related to [[25 Jun 2026]] and [[Software/Python/Libraries]].
   - Check the reference: ((12345678-abcd-1234-abcd-1234567890ab)).
   ```

---

## 🎯 Step 2: Verify Obsidian Conversion

Run the `obsidian` subcommand:
```bash
uv run python -m logseq_converter.cli obsidian mock-graph mock-obsidian-vault
```

### Verification Checklist:
- [ ] **Daily Folder**: A directory named `Daily/` should exist, containing `Daily/2026-06-25.md`.
- [ ] **Namespace Nesting**: A directory named `Software/` should exist, containing `Software/Python.md`.
- [ ] **Clean Daily Note**: Opening `Daily/2026-06-25.md` should:
  - Not contain `#links`, `#learnings`, `#highlights`, or `:LOGBOOK:` sections.
  - Contain a block anchor `^123456` at the end of the referenced block.
- [ ] **Extracted Folders**: Subdirectories `Links/`, `Learnings/`, and `Highlights/` should exist:
  - `Links/LogSeq.md` should contain `url: https://logseq.com`, `github_url: https://github.com/logseq/logseq`, and `date: 2026-06-25` in its YAML frontmatter.
  - `Learnings/Learned that Python 3.14.md` should contain `date: 2026-06-25` in frontmatter and the child bullet point about the new optimizer in the body.
- [ ] **Clean Page Note**: Opening `Software/Python.md` should:
  - Contain YAML frontmatter with `tags` and `author`.
  - **Not** contain `heading::`, `icon::`, or other excluded properties.
  - Contain a converted block reference pointing to `[[Daily/2026-06-25#^123456]]` (or matching page/anchor).
  - Contain converted date link pointing to `[[Daily/2026-06-25]]`.

---

## 🔮 Step 3: Verify Tana Export

Run the `tana` subcommand:
```bash
uv run python -m logseq_converter.cli tana mock-graph mock-tana-import.json --force
```

### Verification Checklist:
- [ ] **JSON Document**: Check that `mock-tana-import.json` is successfully created.
- [ ] **Tana Structure**: Open the JSON file and verify:
  - It contains a valid JSON object structure conforming to Tana Intermediate Format.
  - Page nodes contain child nodes matching the bullet points.
  - The node representing the page `Software/Python` contains supertags matching the tags list.

---

## 🔮 Step 4: Verify Tolaria Conversion

Run the `tolaria` subcommand:
```bash
uv run python -m logseq_converter.cli tolaria mock-graph mock-tolaria-vault
```

### Verification Checklist:
- [ ] **Journal Path**: Check that daily journals are placed under `journal/` (e.g., `journal/2026-06-25.md`).
- [ ] **Frontmatter type**: Opening `journal/2026-06-25.md` shows `type: journal` in YAML frontmatter.
- [ ] **Clean Block IDs**: Verify that `id:: uuid` strings are completely removed.

---

## 🔮 Step 5: Verify Blinko Sync (Dry Run)

Run the `blinko` subcommand in dry-run mode:
```bash
export BLINKO_TOKEN="mock-token"
uv run python -m logseq_converter.cli blinko mock-graph https://example.com/api --dry-run
```

### Verification Checklist:
- [ ] **No Networking**: Verify that the command executes without throwing authentication/connection errors since `--dry-run` bypasses direct network calls.
- [ ] **Logs**: Verify console output indicates notes are being processed for export.
