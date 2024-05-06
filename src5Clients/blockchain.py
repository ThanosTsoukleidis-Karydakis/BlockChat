from block import Block

class Blockchain:

    def __init__(self):
        self.blocks=[]

    # convert the blockchain to a list that contains its blocks (in list format too)
    def to_list(self):
        l = []
        for block in self.blocks:
            l.append(block.to_list())
        return l


    # add a block into the blockchain
    def add_block(self, block):
        self.blocks.append(block)
 
