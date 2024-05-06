from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import base64

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:
    def __init__(self,sender_address,receiver_address,type_of_transaction,content,nonce,sign):

        ##set
        self.sender_address=sender_address
        self.receiver_address=receiver_address
        self.type_of_transaction=type_of_transaction
        self.content=content
        self.amount=content if (self.type_of_transaction=="coins" or self.type_of_transaction=="stake") else -1
        self.message=content if self.type_of_transaction=="message" else ""
        self.nonce=nonce
        #self.amount
        #self.transaction_id
        #self.transaction_inputs
        #self.transaction_outputs
        self.Signature=sign

    def to_dict(self):
        return {"sender_address":self.sender_address.decode(), "receiver_address":self.receiver_address.decode(), "type_of_transaction":self.type_of_transaction, "content":self.content, "nonce":self.nonce, "signature":self.Signature}


    def sign_transaction(self,private_key):
        #return SHA.new(data=self.message.encode("utf8") if self.type_of_transaction=="message" else self.amount.encode("utf8")).hexdigest()
        priv_key = RSA.importKey(private_key)
        h = SHA.new(data=self.message.encode("utf8") if self.type_of_transaction=="message" else str(self.amount).encode("utf8"))
        signature = PKCS1_v1_5.new(priv_key).sign(h)
        result = base64.b64encode(signature).decode()
        self.Signature=result
        return result
        #sign transaction with private key (self.message if self.type_of_transaction=="message" else self.amount)
    

    def inverse(self):
        return Transaction(self.receiver_address,self.sender_address,self.type_of_transaction, self.content, self.nonce, self.Signature)