import shortuuid

class Transaction:
    def __init__(self, peer_id1, peer_id2, amount):
        self.txn_id=shortuuid.uuid()
        self.sender=peer_id1
        self.receiver=peer_id2
        self.amount=amount
        self.statement=f"{self.txn_id}:{self.sender} pays {self.receiver} {amount} coins"

class Coinbase:
    def __init__(self, peer_id):
        self.txn_id=shortuuid.uuid()
        self.miner=peer_id
        self.statement=f"{self.txn_id}:{self.miner} mines 50 coins"