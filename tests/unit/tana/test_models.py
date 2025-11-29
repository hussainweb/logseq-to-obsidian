import pytest
from pydantic import ValidationError

from logseq_converter.tana.models import TanaAPIPayload, TanaField, TanaNode, TanaSupertagRef


def test_tana_node_creation():
    node = TanaNode(name="Test Node")
    assert node.name == "Test Node"
    assert node.description is None
    assert node.supertags is None
    assert node.children is None


def test_tana_node_with_supertags():
    tag = TanaSupertagRef(id="tag123")
    node = TanaNode(name="Tagged Node", supertags=[tag])
    assert node.supertags[0].id == "tag123"


def test_tana_node_recursive_children():
    child = TanaNode(name="Child Node")
    parent = TanaNode(name="Parent Node", children=[child])
    assert parent.children[0].name == "Child Node"


def test_tana_field_structure():
    field_value = TanaNode(name="Field Value")
    field = TanaField(attributeId="attr123", children=[field_value])
    assert field.type == "field"
    assert field.attributeId == "attr123"
    assert field.children[0].name == "Field Value"


def test_tana_api_payload_validation():
    nodes = [TanaNode(name=f"Node {i}") for i in range(101)]
    with pytest.raises(ValidationError):
        TanaAPIPayload(targetNodeId="INBOX", nodes=nodes)

    valid_nodes = [TanaNode(name="Node 1")]
    payload = TanaAPIPayload(targetNodeId="INBOX", nodes=valid_nodes)
    assert payload.targetNodeId == "INBOX"
    assert len(payload.nodes) == 1
