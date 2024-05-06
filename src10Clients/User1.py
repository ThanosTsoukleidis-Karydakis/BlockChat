from node import Node
import requests
from flask import Flask, jsonify, request, render_template,make_response, url_for,after_this_request
from flask_cors import CORS
import base64
from block import Block
from blockchain import Blockchain
from transaction import Transaction
import copy
import binascii
import json
import multiprocessing
import threading
import collections
import time


lock=threading.RLock()

from node import Node

app = Flask(__name__)
CORS(app)
#app2 = Flask(__name__)

messages={}

manager = multiprocessing.Manager()
existingNodes = manager.list([])
transSent=True
state=[]
done=True
# inverse transactions of the current block
inverseTransactions = manager.list([])

broadcast_mined_block=manager.Value('i',False)
broadcast_mined_block_isRead=manager.Value('i',False)
validator = manager.Value('i', 42)
myUpdate=False
transQueue=collections.deque()
madeBroadcast=False
minedBlockHandled=False
startingTime=0
madeTransactionCounter=0

registerPhase = [True]

coinsSent = manager.dict({})
coinsSent["5001"]=True
coinsSent["5002"]=True
coinsSent["5003"]=True
coinsSent["5004"]=True

coinsSent["5005"]=True
coinsSent["5006"]=True
coinsSent["5007"]=True
coinsSent["5008"]=True
coinsSent["5009"]=True

totalNodes = 9

myNode=Node(5000,"127.0.0.1")
myNode.id=0
myNode.nonce=0




myBlockChain=Blockchain()


#myBlock=Block(time.time(),binascii.hexlify((myNode.chain.blocks[len(myNode.chain.blocks)-1].myHash())).decode())
genesisBlock=Block(time.time(),1)

genesisTransaction = Transaction(myNode.wallet[1], myNode.wallet[1], "coins", 1000*(totalNodes+1),0,'')
genesisTransaction.sign_transaction(myNode.wallet[0])
genesisBlock.add_transaction(genesisTransaction)

myBlockChain.add_block(genesisBlock)
myNode.chain=myBlockChain

myNode.handleGenesisTransaction(genesisTransaction)


myNode.ring=[{"publickey": myNode.wallet[1], "id":0, "ip":myNode.ip, "port":myNode.port, "balance":myNode.BCC, "stake":0}]
myBlock=Block(time.time(),binascii.hexlify((myNode.chain.blocks[len(myNode.chain.blocks)-1].myHash())).decode())


def send_coins():
     global myBlock
     global inverseTransactions
     global validator
     global state
     global broadcast_mined_block
     global transQueue
     global registerPhase
     while registerPhase[0]==True:
          for node in existingNodes:
               if coinsSent[str(node["port"])]==False:
                    coinsSent[str(node["port"])]=True
                    sendCoinsTrans = myNode.create_transaction(node["pubKey"].encode(),"coins",1000)
                    myNode.nonces['0']=sendCoinsTrans.nonce+1
                    sendCoinsTrans.sign_transaction(myNode.wallet[0])
                    if(len(myBlock.listofTransactions)+1<myBlock.capacity):
                        myNode.add_transaction_to_block(myBlock,sendCoinsTrans)
     
                        inverseTransactions.append(sendCoinsTrans.inverse())
                    else:
                         myNode.add_transaction_to_block(myBlock,sendCoinsTrans)
             
                         
                         validator.value= myNode.mine_block(myBlock)
                         print('VALIDATOR', validator)
                         if validator.value==0:   
                            #state={'ring':copy.deepcopy(myNode.ring), 'BCC':copy.deepcopy(myNode.BCC)}

                            myBlockChain.blocks.append(myBlock)
                            myNode.chain=myBlockChain
                            
                            broadcast_mined_block=True
                            if broadcast_mined_block_isRead==True:
                                broadcast_mined_block_isRead=False
                                myBlock=Block(time.time(), binascii.hexlify((myNode.chain.blocks[len(myNode.chain.blocks)-1].myHash())).decode())
                         else:

                              myBlock=Block(time.time(), "")
                        
                         inverseTransactions = manager.list([])

                    myNode.update_status(sendCoinsTrans,True)
                    data2 = sendCoinsTrans.to_dict()
                    data2["noFee"]=True
                    headers = {'Content-Type': 'application/json'}
                    chainData={"chain": myBlockChain.to_list(), 'coinsBlock': myBlock.to_list(), 'genesisTimestamp':genesisBlock.timestamp}

                    sendChainTransResponse = requests.post('http://'+node["ip"]+':'+str(node["port"])+'/takeChain', data=json.dumps(chainData), headers=headers)
                   
                    for node in existingNodes:
                        sendCoinsTransResponse = requests.post('http://'+node["ip"]+":"+str(node["port"])+'/sendtransaction', data=json.dumps(data2), headers=headers)


                    if (len(existingNodes) == totalNodes)  :
                        headers = {'Content-Type': 'application/json'}
                        for node in existingNodes:
                            last=existingNodes[len(existingNodes)-1]
                            if True:
                                data={"existingNodes":list(existingNodes)}
                                res = requests.post('http://'+node["ip"]+':'+str(node['port'])+'/takeBlockChatInfo', data=json.dumps(data), headers=headers).json()


t = threading.Thread(target=send_coins)
t.start()





def broadcastMinedBlock():
     global broadcast_mined_block
     global broadcast_mined_block_isRead
     global myBlock
     global validator
     global state
     global transQueue
     global madeBroadcast
     
     while True:
        blockToSend = myBlock
        broadcast_mined_block_isRead=True
        time.sleep(0.0)
        if broadcast_mined_block==True:
            broadcast_mined_block=False
            for node in myNode.ring:
                            if node['port']!=myNode.port:
                                headers = {'Content-Type': 'application/json'}
                                data={"minedBlock": blockToSend.to_list(), "timestamp": blockToSend.timestamp}
                                res = requests.post('http://'+node["ip"]+':'+str(node["port"])+'/takeMinedBlock', data=json.dumps(data), headers=headers).json()
            
            for trans in blockToSend.listofTransactions:
                    if(trans.nonce not in [i for i in range(totalNodes+1)]):
                        blockToSend.change_fee(trans)
            
            myNode.BCC=myNode.BCC+blockToSend.fee
            
            for node in myNode.ring:
                if(node["port"]==myNode.port):
                    node["balance"]=node["balance"]+blockToSend.fee

            state={'ring':copy.deepcopy(myNode.ring), 'BCC':copy.deepcopy(myNode.BCC), 'nonces':copy.deepcopy(myNode.nonces)}
            validator.value=42
            print("MY BLOCKCHAIN : ", len(myBlockChain.to_list()))
            print("RING AFTER MINING", myNode.ring)
            print("MY BCC", myNode.BCC)
            madeBroadcast=True


broadcastMinedBlockThread = threading.Thread(target=broadcastMinedBlock)
broadcastMinedBlockThread.start()


    

@app.route('/sendtransaction', methods=['POST'])
def sendtransaction():
    with lock:
        global done
        global broadcast_mined_block
        global broadcast_mined_block_isRead
        global validator
        global myBlock
        global state
        global myUpdate
        global madeBroadcast
        global minedBlockHandled
        global startingTime
        if done==True:
            done=False
            data = request.json
            transaction = Transaction(data['sender_address'].encode(), data['receiver_address'].encode(), data['type_of_transaction'], data['content'],data['nonce'],data['signature'])
           
            valid= myNode.validate_transaction(transaction.message, transaction.amount, data['signature'], data['type_of_transaction'],data['sender_address'], data['nonce'])
            if(valid):
                myNode.update_status(transaction, data["noFee"])
                if(len(myBlock.listofTransactions)+1<myBlock.capacity):
                    myNode.add_transaction_to_block(myBlock,transaction)
                    #myNode.nonce=transaction.nonce
                                    
                    inverseTransactions.append(transaction.inverse())
                else:
                    myNode.add_transaction_to_block(myBlock,transaction) 
                    #myNode.nonce=transaction.nonce
            
                    
                    validator.value = myNode.mine_block(myBlock)
                    print('VALIDATOR', validator)            
                    if validator.value==0:   
                        myBlockChain.blocks.append(myBlock)
                        
                        myNode.chain=myBlockChain
                        myBlock=Block(time.time(), binascii.hexlify((myNode.chain.blocks[len(myNode.chain.blocks)-1].myHash())).decode())
                        
                        broadcast_mined_block=True
                        while(broadcast_mined_block_isRead==False):
                            time.sleep(0.0)     

                        broadcast_mined_block_isRead=False

                        while(madeBroadcast==False):
                             time.sleep(0)

                        madeBroadcast=False


                    else:
                        myUpdate=True

                        while(minedBlockHandled==False):
                             time.sleep(0)
                        minedBlockHandled=False

                done=True
                print('TOTAL TIME : ',time.time()-startingTime)
                return {'message':'OK'}
            else:
                done=True
                print('TOTAL TIME : ',time.time()-startingTime)
                #print("Not valid!")
                return {"message":"error in validating"}

@app.route('/getPublicKey', methods=['GET'])
def getPubKey():
    return myNode.wallet[1]


@app.route('/register', methods=['POST'])
def register():
    global registerPhase
    global state
    data = request.json
    data["balance"]=0
    data["stake"]=0
    data["id"]=len(existingNodes)+1
    dport=data["port"]
    existingNodes.append(data)

    myNode.ring.append({"publickey": data["pubKey"].encode(), "id":len(existingNodes), "ip":data["ip"], "port":data["port"], "balance":0, "stake":0})
    if(len(existingNodes)==totalNodes):
        ringInit=[]
        ring=copy.deepcopy(myNode.ring)
        for node in ring:
            if(node['id']!=0):
                ringInit.append(node)
                ringInit[len(ringInit)-1]['balance']=0
            else:
                ringInit.append(node)
                ringInit[len(ringInit)-1]['balance']=(totalNodes+1)*1000
        state={'ring': ringInit, 'BCC': (totalNodes+1)*1000, 'nonces':copy.deepcopy(myNode.nonces)}

    
    if (len(existingNodes) == totalNodes)  :
                coinsSent[str(dport)]=False
                registerPhase[0]=False

    coinsSent[str(dport)]=False
    return {"port":myNode.port,"pubKey": myNode.wallet[1].decode(), "id": len(existingNodes), "OK":"OK"}



@app.route('/makeTransaction', methods=['POST'])
def makeTrans():
        global broadcast_mined_block
        global broadcast_mined_block_isRead
        global myBlock
        global validator
        global state
        global transSent
        global madeTransactionCounter
        global startingTime

        if(madeTransactionCounter==0):
             startingTime=time.time()
             madeTransactionCounter=madeTransactionCounter+1

        input=request.json
        transSent=False
        key='0'.encode()
        port=""

        for node in myNode.ring:
             if(node["id"]==input["id"]):
                  key=node["publickey"]

        trans = myNode.create_transaction(key,input["type"],input["content"])
        trans.sign_transaction(myNode.wallet[0])

        data = trans.to_dict()
        data["noFee"]=input["noFee"]

        headers = {'Content-Type': 'application/json'}
        for node in myNode.ring:
            response = requests.post('http://'+node["ip"]+':'+str(node["port"]+1000)+'/proxy', data=json.dumps(data), headers=headers)

        transSent=True
        return {"message":"transaction broadcasted to proxies"}

@app.route('/takeMinedBlock', methods=['POST'])
def takeMinedBlock():
    global validator
    global state
    global transSent
    global myUpdate
    global minedBlockHandled
    global myBlock

    while(transSent==False or myUpdate==False):
         time.sleep(0)

    myUpdate=False

    data = request.json
    minedBlockList = data["minedBlock"]
    minedBlock = Block(data["timestamp"],binascii.hexlify((myNode.chain.blocks[len(myNode.chain.blocks)-1].myHash())).decode())
    myNode.ring=state['ring']
    myNode.BCC=state['BCC']

    for transList in minedBlockList:
        trans = Transaction(transList['sender_address'].encode(),transList['receiver_address'].encode(),transList['type_of_transaction'],transList['content'],transList['nonce'],transList['signature'])
        minedBlock.add_transaction(trans)
        senderId=""
        for node in myNode.ring:
             if node['publickey'].decode()==transList['sender_address']:
                  senderId=str(node['id'])
        if(trans.nonce not in [i for i in range(totalNodes+1)]):
            minedBlock.change_fee(trans)
            myNode.update_status(trans, False)

        elif(trans.nonce in [i for i in range(totalNodes+1)]):
             myNode.update_status(trans, True)
        
    while(validator.value==42):
        time.sleep(0)
    validated = myNode.validate_block(minedBlock, str(request.remote_addr), validator.value)
    if(validated):
        for node in myNode.ring:
            if node["id"]==validator.value:
                node["balance"]=node["balance"]+minedBlock.fee
                state={'ring':copy.deepcopy(myNode.ring), 'BCC':copy.deepcopy(myNode.BCC),'nonces':copy.deepcopy(myNode.nonces)}
        myBlockChain.add_block(minedBlock)
        myNode.chain=myBlockChain
        myBlock=Block(time.time(), binascii.hexlify(minedBlock.myHash()).decode())
        print("MY BLOCKCHAIN : ", len(myBlockChain.to_list()))
        print("RING AFTER MINING", myNode.ring)
        print("MY BCC", myNode.BCC)
        minedBlockHandled=True
        return {"message":"mined block accepted"}
    else: 
        myBlock=Block(time.time(), binascii.hexlify((myNode.chain.blocks[len(myNode.chain.blocks)-1].myHash())).decode())
        minedBlockHandled=True
        return {"message":"mined block not accepted"}

# @app.route('/proxy', methods=['POST'])
# def proxy():
#     global transQueue
#     data = request.json
#     transQueue.appendleft(data)
#     return {'message':'transaction added'}

if __name__ == '__main__':
     app.run(host=myNode.ip, port=myNode.port, debug=False)
     broadcastMinedBlockThread.join()
