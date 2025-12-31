from logseq_converter.tana.models import (
    TanaIntermediateFile,
    TanaIntermediateNode,
    TanaIntermediateSummary,
)


def test_tana_intermediate_node_defaults():
    node = TanaIntermediateNode(uid="123", name="Test Node", createdAt=1000, editedAt=2000)
    assert node.uid == "123"
    assert node.name == "Test Node"
    assert node.createdAt == 1000
    assert node.editedAt == 2000
    assert node.type == "node"
    assert node.children == []
    assert node.refs == []
    assert node.supertags == []
    assert node.flags == []


def test_tana_intermediate_file_structure():
    summary = TanaIntermediateSummary(
        leafNodes=0, topLevelNodes=0, totalNodes=0, calendarNodes=0, fields=0, brokenRefs=0
    )
    node = TanaIntermediateNode(uid="1", name="Root", createdAt=0, editedAt=0)

    tana_file = TanaIntermediateFile(summary=summary, nodes=[node])

    assert tana_file.version == "TanaIntermediateFile V0.1"
    assert len(tana_file.nodes) == 1
    assert tana_file.nodes[0] == node
    assert tana_file.homeNodeIds == []
    assert tana_file.attributes == []
    assert tana_file.supertags == []


def test_tana_intermediate_node_nesting():
    child = TanaIntermediateNode(uid="2", name="Child", createdAt=0, editedAt=0)
    parent = TanaIntermediateNode(uid="1", name="Parent", createdAt=0, editedAt=0, children=[child])

    assert len(parent.children) == 1
    assert parent.children[0] == child
