from logseq_converter.obsidian.converter import ObsidianConverter


def test_filter_excluded_properties_from_frontmatter():
    """Test that excluded properties are not included in frontmatter."""
    converter = ObsidianConverter()
    content = """heading:: true
collapsed:: true
icon:: 📝
title:: My Page
tags:: tag1, tag2
alias:: alias1

- Block 1
"""
    result = converter._transform_properties(content)

    # Should only include tags and alias, not heading, collapsed, icon, or title
    expected = """---
tags: tag1, tag2
alias: alias1
---

- Block 1
"""
    assert result == expected


def test_filter_properties_with_exclude_from_graph_view():
    """Test that exclude-from-graph-view is filtered."""
    converter = ObsidianConverter()
    content = """exclude-from-graph-view:: true
tags:: important

- Block content
"""
    result = converter._transform_properties(content)

    expected = """---
tags: important
---

- Block content
"""
    assert result == expected


def test_remove_excluded_properties_from_body():
    """Test that excluded properties are removed from content body."""
    converter = ObsidianConverter()
    content = """---
tags: important
---

- Block 1
  heading:: Test
  collapsed:: true
- Block 2
  icon:: 📌
- Block 3
  custom:: value
"""
    result = converter._remove_excluded_properties_from_body(content)

    # Should remove heading, collapsed, and icon, but keep custom property
    expected = """---
tags: important
---

- Block 1
- Block 2
- Block 3
  custom:: value
"""
    assert result == expected


def test_full_conversion_with_property_filtering():
    """Test the complete conversion process with property filtering."""
    converter = ObsidianConverter()
    content = """heading:: Main
collapsed:: false
tags:: tag1
alias:: Test Page

- First block
  icon:: 🔥
  - Sub block
    collapsed:: true
- Second block
"""
    result = converter.convert_content(content)

    # Should have tags and alias in frontmatter, but no heading, collapsed, or icon
    assert "---" in result
    assert "tags: tag1" in result
    assert "alias: Test Page" in result
    assert "heading:" not in result
    assert "collapsed:" not in result
    assert "icon:" not in result

    # Body should not contain excluded properties
    assert "heading:: Main" not in result
    assert "collapsed::" not in result
    assert "icon::" not in result


def test_no_properties_to_filter():
    """Test that content without excluded properties remains unchanged."""
    converter = ObsidianConverter()
    content = """tags:: important
custom:: value

- Block 1
"""
    result = converter.convert_content(content)

    assert "tags: important" in result
    assert "custom: value" in result


def test_filter_properties_from_yaml_frontmatter():
    """Test that excluded properties are removed from YAML frontmatter."""
    converter = ObsidianConverter()
    content = """---
title: My Page
heading: true
collapsed: false
icon: 📝
exclude-from-graph-view: true
tags: tag1, tag2
author: John Doe
---

- Block 1
"""
    result = converter._filter_frontmatter_properties(content)

    # Should keep tags and author
    assert "tags: tag1, tag2" in result
    assert "author: John Doe" in result

    # Should remove excluded properties
    assert "title:" not in result
    assert "heading:" not in result
    assert "collapsed:" not in result
    assert "icon:" not in result
    assert "exclude-from-graph-view:" not in result


def test_filter_frontmatter_preserves_structure():
    """Test that frontmatter structure is preserved when filtering."""
    converter = ObsidianConverter()
    content = """---
tags: important
heading: Test
date: 2023-11-28
---

- Content
"""
    result = converter._filter_frontmatter_properties(content)

    expected = """---
tags: important
date: 2023-11-28
---

- Content
"""
    assert result == expected


def test_no_frontmatter_unchanged():
    """Test that content without frontmatter is unchanged."""
    converter = ObsidianConverter()
    content = """- Block 1
- Block 2
"""
    result = converter._filter_frontmatter_properties(content)
    assert result == content


def test_full_conversion_with_yaml_frontmatter():
    """Test complete conversion with YAML frontmatter filtering."""
    converter = ObsidianConverter()
    content = """---
title: Test Page
icon: 🎯
tags: important
---

- Block 1
  collapsed:: true
- Block 2
"""
    result = converter.convert_content(content)

    # Should have tags in frontmatter
    assert "---" in result
    assert "tags: important" in result

    # Should not have title or icon in frontmatter
    assert "title:" not in result
    assert "icon:" not in result

    # Should not have collapsed in body
    assert "collapsed::" not in result


def test_comprehensive_property_filtering():
    """Test all three filtering scenarios in a single conversion."""
    converter = ObsidianConverter()
    # This content has:
    # 1. YAML frontmatter with excluded properties
    # 2. key:: value properties at top level (after frontmatter)
    # 3. Inline properties in content body
    content = """---
title: Comprehensive Test
icon: 🚀
author: Test Author
tags: test
---

heading:: Main Heading
collapsed:: true
custom:: keep-this

- Block 1
  icon:: 🔥
  note:: important
- Block 2
  exclude-from-graph-view:: true
- Block 3
  metadata:: preserve
"""
    result = converter.convert_content(content)

    # Verify frontmatter has kept allowed properties
    assert "---" in result
    assert "author: Test Author" in result
    assert "tags: test" in result

    # Verify excluded properties are gone from frontmatter
    assert "title:" not in result
    assert "icon:" not in result

    # Properties after frontmatter remain as key:: value but excluded ones are removed
    assert "custom:: keep-this" in result  # Non-excluded, kept
    assert "heading::" not in result  # Excluded, removed
    assert "collapsed::" not in result  # Excluded, removed
    assert "exclude-from-graph-view::" not in result  # Excluded, removed

    # Verify non-excluded inline properties in blocks are preserved
    assert "note:: important" in result
    assert "metadata:: preserve" in result

    # Verify content blocks are preserved
    assert "- Block 1" in result
    assert "- Block 2" in result
    assert "- Block 3" in result
