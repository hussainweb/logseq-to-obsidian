from logseq_converter.logseq.models import Block
from logseq_converter.tana.converter import TanaConverter
from logseq_converter.tana.models import TanaNode


def test_convert_block_to_node():
    block = Block(content="Test Content")
    converter = TanaConverter()
    node = converter.convert_block(block)

    assert isinstance(node, TanaNode)
    assert node.name == "Test Content"


def test_convert_block_with_children():
    child = Block(content="Child")
    parent = Block(content="Parent", children=[child])

    converter = TanaConverter()
    node = converter.convert_block(parent)

    assert len(node.children) == 1
    assert node.children[0].name == "Child"
