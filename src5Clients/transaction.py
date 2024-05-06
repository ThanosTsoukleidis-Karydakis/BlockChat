from collections import OrderedDict
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import base64

class Transaction:
    def __init__(self,sender_address,receiver_address,type_of_transaction,content,nonce,sign):
        self.sender_address=sender_address
        self.receiver_address=receiver_address
        self.type_of_transaction=type_of_transaction
        self.content=content
        self.amount=content if (self.type_of_transaction=="coins" or self.type_of_transaction=="stake") else -1
        self.message=content if self.type_of_transaction=="message" else ""
        self.nonce=nonce
        self.Signature=sign

    # convert transaction to dict format
    def to_dict(self):
        return {"sender_address":self.sender_address.decode(), "receiver_address":self.receiver_address.decode(), "type_of_transaction":self.type_of_transaction, "content":self.content, "nonce":self.nonce, "signature":self.Signature}


    #sign transaction with private key, i.e. sign (RSA) the hashed (SHA) message with the private key
    def sign_transaction(self,private_key):
        priv_key = RSA.importKey(private_key)
        h = SHA.new(data=self.message.encode("utf8") if self.type_of_transaction=="message" else str(self.amount).encode("utf8"))
        signature = PKCS1_v1_5.new(priv_key).sign(h)
        result = base64.b64encode(signature).decode()
        self.Signature=result
        return result
        
    
    # compute the inverse transaction
    def inverse(self):
        return Transaction(self.receiver_address,self.sender_address,self.type_of_transaction, self.content, self.nonce, self.Signature)