from block import Block
import time

class Blockchain:
    """
    The blockchain of the noobcash


    Attributes:
        blocks (list): list that contains the validated blocks of the chain.
    """

    def __init__(self):
        self.blocks=[]
        #self.blocks=[Block(time.time(),1)]
        """Inits a Blockchain"""



    def to_list(self):
        l = []
        for block in self.blocks:
            l.append(block.to_list())
        return l



    def add_block(self, block):
        self.blocks.append(block)
        """Adds a new block in the chain."""
