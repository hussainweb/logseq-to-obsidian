# Property Filtering Demo

This document demonstrates how the LogSeq to Obsidian converter filters out unwanted properties.

## Excluded Properties

The following LogSeq properties are automatically filtered out during conversion:

- `heading::`
- `collapsed::`
- `icon::`
- `title::`
- `exclude-from-graph-view::`

## Example 1: Frontmatter Properties

### LogSeq Input:
```markdown
heading:: true
collapsed:: false
icon:: 📝
title:: My Important Page
tags:: important, work
author:: John Doe

- First block
- Second block
```

### Obsidian Output:
```markdown
---
tags: important, work
author: John Doe
---

- First block
- Second block
```

**Result**: Only `tags` and `author` are kept in the frontmatter. All excluded properties are removed.

## Example 2: Properties in YAML Frontmatter

### LogSeq Input:
```markdown
---
title: My Important Page
heading: true
collapsed: false
icon: 📝
exclude-from-graph-view: true
tags: important, work
author: John Doe
---

- First block
- Second block
```

### Obsidian Output:
```markdown
---
tags: important, work
author: John Doe
---

- First block
- Second block
```

**Result**: When LogSeq files already have YAML frontmatter, excluded properties (`title`, `heading`, `collapsed`, `icon`, `exclude-from-graph-view`) are filtered out, keeping only the useful properties.

## Example 3: Properties in Content Body

### LogSeq Input:
```markdown
tags:: notes

- Block 1
  heading:: Sub Heading
  collapsed:: true
- Block 2
  icon:: 🎯
  custom:: value
- Block 3
```

### Obsidian Output:
```markdown
---
tags: notes
---

- Block 1
- Block 2
  custom:: value
- Block 3
```

**Result**: Excluded properties like `heading::`, `collapsed::`, and `icon::` are removed from the content body, but `custom::` is preserved since it's not in the exclusion list.

## Why Filter These Properties?

These properties are LogSeq-specific UI/presentation metadata that:
1. Don't have equivalent meaning in Obsidian
2. Clutter the Obsidian vault with unnecessary metadata
3. Can cause confusion when reading notes in Obsidian

By filtering them out, we ensure a cleaner conversion that focuses on the actual content and meaningful metadata.

## How Filtering Works

The converter filters properties in three scenarios:

1. **Top-level `key:: value` properties**: Converted to YAML frontmatter, but excluded properties are skipped
2. **Existing YAML frontmatter**: Excluded properties are removed from pre-existing frontmatter in LogSeq files
3. **Inline properties in content body**: Lines containing only excluded properties are removed entirely
