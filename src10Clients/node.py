from block import Block
from transaction import Transaction
import ast
import Crypto
import Crypto.Random as Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Cipher import PKCS1_OAEP
import random
import time
import binascii
import threading

lock=threading.Lock()

from blockchain import Blockchain

import base64

class Node:
    def __init__(self,port,ip):
        self.BCC=0
        self.port=port
        self.nonce=0
        self.ip=ip
        ##set

        self.chain=Blockchain()
        #self.current_id_count
        #self.NBCs
        self.wallet=self.generate_wallet()
        self.stakes=[1,1,1,1,1,1,1,1,1,1]
        self.ring=[]
        self.id=-1
        self.nonces={'0':1, '1':1001,'2':2001, '3':3001, '4':4001, '5':5001, '6':6001, '7':7001, '8':8001, '9':9001}
        #self.ring[] here we stoer information for every node, as its id, its address [ip:port] its public key and its balance

    def create_new_block():
        return Block(time.time(),self.chain.blocks[len(self.chain.blocks)-1].myHash())

    def get_balance(self):
        return self.BCC

    def generate_wallet(self):
        random_generator = Random.new().read
        rsa_key = RSA.generate(2048, random_generator)
        return [rsa_key.exportKey(), rsa_key.publickey().exportKey()]
        #create a wallet for this node , with a public key and a private key

    def register_node_to_ring():()
    #add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
    #bootstrap node informs all other nodes and gives the request node an id and 100 NBCs

    def create_transaction(self,receiver_address,type_of_transaction,content):
        transaction=Transaction(self.wallet[1],receiver_address,type_of_transaction,content,self.nonce+1,'bourda')
        self.nonce=self.nonce+1
        return transaction

    def validate_transaction(self,message,amount,Signature, typeTrans,sender, nonce):
        messageHash = SHA.new(data=message.encode("utf8") if typeTrans=="message" else str(amount).encode("utf8"))

        sender_public_key = RSA.importKey(sender)

        bal = 0
        valid=False
        id=''
        for node in self.ring:
            if(node["publickey"].decode()==sender):
                id=str(node['id'])
                bal=node["balance"]-self.stakes[node['id']]
                if(typeTrans=="message"):
                    fee = len(message)
                    if(bal-fee>=0):
                        valid=True

                elif(typeTrans=="coins"):
                    fee = amount*3/100
                    if(bal-fee-amount>=0):
                        valid=True
                elif(typeTrans=='stake'):
                    if(node["balance"]-amount>=0):
                        valid=True     

        validNonce=(nonce==self.nonces[id])
        if(validNonce):
            self.nonces[id]=self.nonces[id]+1
        

        return PKCS1_v1_5.new(sender_public_key).verify(messageHash, base64.b64decode(Signature)) and valid and validNonce


    def handleGenesisTransaction(self,trans):
        amount=trans.amount
        self.BCC=self.BCC+amount
        return self.BCC



    def add_transaction_to_block(self,block, transaction):
        if(len(block.listofTransactions)<block.capacity):
            block.add_transaction(transaction)
        #if enough transactions mine


    def mine_block(self, block):
        def findValidator(stakes):
            random.seed(block.previousHash)
            lottery=[]
            for i in range(len(stakes)):
                for j in range(stakes[i]):
                    lottery.append(i)
            return random.choice(lottery)

        return findValidator(self.stakes)



    def broadcast_block():()




   # def valid_proof(...difficulty=MINING_DIFFICULTY):()



    def validate_block(self, block, address, validator):
        # developement mode
        if address=="127.0.0.1":
            return binascii.hexlify((self.chain.blocks[len(self.chain.blocks)-1].myHash())).decode()==block.previousHash
        # production mode
        else: 
            hashCondition=binascii.hexlify((self.chain.blocks[len(self.chain.blocks)-1].myHash())).decode()==block.previousHash
            if(hashCondition==True):
                for node in self.ring:
                    if(node["ip"]==address):
                        if(node["id"]==validator):
                            return True
            return False


    def valid_chain(self,chain):()
    #check for the longer chain across all nodes


    # whenever a transaction is received, this function will update the personal ring
    # and the node's balance if needed
    def update_status(self, transaction, noFee):
            if transaction.receiver_address.decode()=='0':
                for node in self.ring:
                    if node['publickey']==transaction.sender_address:
                        self.stakes[node['id']]=transaction.content
                return "stake transaction"
            match_addr=False
            for node in self.ring:
                if transaction.receiver_address==node["publickey"]:
                    match_addr=True
            if(match_addr==False):
                return "No match"
            if transaction.sender_address==transaction.receiver_address:
                    for node in self.ring:
                        if node["publickey"]==transaction.sender_address:
                            node["balance"]=node["balance"]+transaction.amount
                    return "Added"
            else:
                if transaction.type_of_transaction=="coins":
                    for node in self.ring:
                        if node["publickey"]==transaction.sender_address:
                            mul=1.03
                            if noFee:
                                mul=1.0
                            node["balance"]=node["balance"]-mul*transaction.amount
                        if node["publickey"]==transaction.receiver_address:
                            node["balance"]=node["balance"]+transaction.amount
                    if transaction.sender_address==self.wallet[1]:
                        mul=1.03
                        if noFee:
                            mul=1.0
                        self.BCC=self.BCC-mul*transaction.amount

                    if transaction.receiver_address==self.wallet[1]:
                        self.BCC=self.BCC+transaction.amount
                if transaction.type_of_transaction=="message":
                    for node in self.ring:
                        if node["publickey"]==transaction.sender_address:
                            node["balance"]=node["balance"]-len(transaction.message)
                    if transaction.sender_address==self.wallet[1]:
                        self.BCC=self.BCC-len(transaction.message)

                return "Added"
            

    def stake(self,amount):
         stakeTrans = self.create_transaction('0'.encode(), 'stake', amount)
         stakeTrans.sign_transaction(self.wallet[0])
         return stakeTrans


        

