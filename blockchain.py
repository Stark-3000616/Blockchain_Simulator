from block import Block

#Structure of blockchain in each peer
class Blockchain:
    def __init__(self):
        self.blocks={}
        self.last_block=None
        self.blocks[0]=[]
    
    #Function to add gebesis block to the blockchain    
    def add_genesis(self, genesis):
        self.blocks[0]=[genesis]
        self.last_block=genesis

    #Function to add a block to the blockchain and determine longest chain
    def add_block(self, block):
        if block.index not in self.blocks:
            self.blocks[block.index]=[block]
            self.last_block=block
        else:
            self.blocks[block.index].append(block)
            #To manage forking on the basis of mine time
            if block.index == self.last_block.index and block.mine_time<self.last_block.mine_time:
                self.last_block=block
    

