from logseq_converter.obsidian.converter import ObsidianConverter


def test_extract_sections():
    converter = ObsidianConverter()
    content = """- Journal Entry 1
- Achievements
  - Won a prize
    - It was great
  - Ate a cake
- Highlights
  - Saw a bird
- Other stuff
"""
    original_filename = "2025_11_27.md"
    
    modified_content, extracted_files = converter.extract_sections(
        content, original_filename
    )
    
    # Verify modified content (sections removed)
    assert "- Journal Entry 1" in modified_content
    assert "- Other stuff" in modified_content
    assert "- Achievements" not in modified_content
    assert "- Highlights" not in modified_content
    
    # Verify extracted files
    filenames = [f[0] for f in extracted_files]
    assert "Achievements/2025-11-27 - Won a prize.md" in filenames
    assert "Achievements/2025-11-27 - Ate a cake.md" in filenames
    assert "Highlights/2025-11-27 - Saw a bird.md" in filenames
    
    # Verify content of extracted file
    for name, content in extracted_files:
        if "Won a prize" in name:
            assert "- Won a prize" in content
            assert "- It was great" in content

def test_remove_logbook():
    converter = ObsidianConverter()
    content = """- Task 1
  :LOGBOOK:
  CLOCK: [2025-11-27 Thu 10:00]--[2025-11-27 Thu 11:00] =>  01:00
  :END:
- Task 2
"""
    result = converter.remove_logbook(content)
    assert ":LOGBOOK:" not in result
    assert "CLOCK:" not in result
    assert ":END:" not in result
    assert "- Task 1" in result
    assert "- Task 2" in result
