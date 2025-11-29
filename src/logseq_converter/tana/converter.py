from logseq_converter.logseq.models import Block
from logseq_converter.tana.models import TanaNode


class TanaConverter:
    def convert_block(self, block: Block) -> TanaNode:
        """
        Converts a LogSeq Block to a TanaNode.
        Recursively converts children.
        """
        children = None
        if block.children:
            children = [self.convert_block(child) for child in block.children]

        # TODO: Handle tags and properties if needed, for now just basic content

        return TanaNode(name=block.content, children=children)
