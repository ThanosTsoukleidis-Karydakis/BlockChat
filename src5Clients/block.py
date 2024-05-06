from transaction import Transaction
import hashlib
import codecs
from Crypto.Hash import SHA
from binascii import hexlify


class Block:
    def __init__(self, ts, prevHash):
        self.previousHash=prevHash
        self.timestamp=ts
        self.hash=0
        self.listofTransactions=[]
        self.capacity=5
        self.fee=0  # total fee results from the block's transactions
        self.validator=-1


    # computation of the block's hash value (double SHA 256)
    def myHash(self):
        def littleEndian(string):
            splited = [str(string)[i:i + 2] for i in range(0, len(str(string)), 2)]
            splited.reverse()
            return "".join(splited)


        prevHashLE=littleEndian(self.previousHash)
        timestampLE=littleEndian(str(self.timestamp).split(".")[0])

        contentsLE=[]
        for i in range(len(self.listofTransactions)):
            print(str(self.listofTransactions[i].content))
            contentsLE.append(littleEndian(hexlify(((str(self.listofTransactions[i].content))).encode()).decode()))
        
        concatResult=prevHashLE+timestampLE
        for i in range(len(contentsLE)):
            concatResult+=contentsLE[i]
        

        if len(concatResult) % 2 != 0:
            concatResult += "0"
        concatResultHEX=codecs.decode(concatResult, 'hex') 

        hash1 = hashlib.sha256(concatResultHEX).digest()
        hash2 = hashlib.sha256(hash1).digest()
        self.hash = hash2
        return hash2
        

    # add a transaction to the block
    def add_transaction(self,transaction):
        self.listofTransactions.append(transaction)

    # convert a block to a list that contains its transactions (as dicts)
    def to_list(self):
        l = []
        for trans in self.listofTransactions:
            l.append(trans.to_dict())
        return l


    # change the fee of a block according to a new transaction
    def change_fee(self, trans):
        if trans.type_of_transaction=='coins':
            self.fee=self.fee+0.03*trans.amount
        else:
            self.fee=self.fee+len(trans.message)