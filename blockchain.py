from block import Block

class Blockchain:
    def __init__(self):
        self.blocks={}
        self.last_block=None
        
    def add_genesis(self, genesis):
        self.blocks[0]=[genesis]
        self.last_block=genesis

    def add_block(self, block):
        if block.index not in self.blocks:
            self.blocks[block.index]=[block]
            self.last_block=block
        else:
            self.blocks[block.index].append(block)
            if block.index == self.last_block.index and block.mine_time<self.last_block.mine_time:
                self.last_block=block
