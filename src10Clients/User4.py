from node import Node
import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import time
from block import Block
from blockchain import Blockchain
from transaction import Transaction
#import wallet
import base64
from node import Node
import binascii
import json
import multiprocessing
import collections
import threading
app = Flask(__name__)
CORS(app)

import copy 

lock=threading.RLock()

totalNodes = 9
messages={}

myNode=Node(5003,"127.0.0.1")
myNode.nonce=3000

myBlockChain=Blockchain()

myNode.chain=myBlockChain

manager = multiprocessing.Manager()
coinTransactions = manager.list([])
inverseTransactions = manager.list([])
broadcast_mined_block=manager.Value('i',False)
broadcast_mined_block_isRead=manager.Value('i',False)
validator = manager.Value('i',42)
myUpdate=False
transSent=True
done=True
state=[]
transQueue=collections.deque()
madeBroadcast=False
minedBlockHandled=False
madeTransactionCounter=0
startingTime=0

data={"pubKey": myNode.wallet[1].decode(), "port":myNode.port, "ip":myNode.ip}
headers = {'Content-Type': 'application/json'}
response = requests.post('http://127.0.0.1:5000/register', data=json.dumps(data), headers=headers).json()



myNode.ring=[{"publickey": myNode.wallet[1], "id":response["id"], "ip":myNode.ip, "port":myNode.port, "balance":0, "stake":0}, {"publickey": response["pubKey"].encode(), "id":0, "ip":"127.0.0.1", "port":response["port"], "balance":0, "stake":0}]
myNode.id=response["id"]

genesisBlock=Block(1,1)

myBlock=Block(time.time(),"")


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

            state={'ring':copy.deepcopy(myNode.ring), 'BCC':copy.deepcopy(myNode.BCC),'nonces':copy.deepcopy(myNode.nonces)}
            validator.value=42
            print("MY BLOCKCHAIN : ", len(myBlockChain.to_list()))
            print("RING AFTER MINING", myNode.ring)
            print("MY BCC", myNode.BCC)
            madeBroadcast=True


broadcastMinedBlockThread = threading.Thread(target=broadcastMinedBlock)
broadcastMinedBlockThread.start()


# def pushRequest():
#         global transQueue
#         while True:
#             headers = {'Content-Type': 'application/json'}
#             if(len(transQueue)>0):
#                 time.sleep(0.5)
#                 response = requests.post('http://'+myNode.ip+':'+str(myNode.port)+'/sendtransaction', data=json.dumps(transQueue.pop()), headers=headers)

# pushReqThread=threading.Thread()
# pushReqThread.start()

 

@app.route('/sendtransaction', methods=['POST'])
def sendtransaction():
    with lock:
        global myUpdate
        global broadcast_mined_block
        global broadcast_mined_block_isRead
        global myBlock
        global validator
        global state
        global done
        global madeBroadcast
        global minedBlockHandled
        global startingTime

        if done==True:
            done=False
            data = request.json
            transaction = Transaction(data['sender_address'].encode(), data['receiver_address'].encode(), data['type_of_transaction'], data['content'],data['nonce'],data['signature'])



            valid= myNode.validate_transaction(transaction.message, transaction.amount, data['signature'], data['type_of_transaction'],data['sender_address'], data['nonce'])
            if data["noFee"]:
                valid=True
            if(valid):

                update_status = myNode.update_status(transaction, data["noFee"])
                
                if(update_status=="No match"):
                    coinTransactions.append(transaction)
                if(len(myBlock.listofTransactions)+1<myBlock.capacity):
                    myNode.add_transaction_to_block(myBlock,transaction)
                    
                    inverseTransactions.append(transaction.inverse())
                else:
                    myNode.add_transaction_to_block(myBlock,transaction)
                    
                    validator.value = myNode.mine_block(myBlock)
                    print('VALIDATOR', validator)
                                
                    if validator.value==response["id"]:   
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
                return {"message":"OK"}
            else:
                #print("Not valid!")
                done=True
                print('TOTAL TIME : ',time.time()-startingTime)
                return {"message":"Error in validating"}



@app.route('/getPublicKey', methods=['GET'])
def getPubKey():
    return myNode.wallet[1]

@app.route('/takeChain', methods=['POST'])
def takeChain():
    data = request.json

    for block in data['chain']:
        takenGenesisBlock = block[0]
        genesisTrans = Transaction(takenGenesisBlock['sender_address'].encode(), takenGenesisBlock['receiver_address'].encode(), takenGenesisBlock['type_of_transaction'], takenGenesisBlock['content'],takenGenesisBlock['nonce'],takenGenesisBlock['signature'])
        myNode.update_status(genesisTrans,True)
        genesisBlock.timestamp=data['genesisTimestamp']
        genesisBlock.add_transaction(genesisTrans)
        myBlockChain.add_block(genesisBlock)
        myNode.chain=myBlockChain
        myBlock.previousHash=binascii.hexlify((myNode.chain.blocks[len(myNode.chain.blocks)-1].myHash())).decode()
    for block in data['coinsBlock']:
        if block['receiver_address']!=myNode.wallet[1].decode():

            trans = Transaction(block['sender_address'].encode(), block['receiver_address'].encode(), block['type_of_transaction'], block['content'],block['nonce'],block['signature'])
            valid = myNode.validate_transaction(trans.message,trans.amount,trans.Signature, trans.type_of_transaction,block['sender_address'],block['nonce'])
            if(valid):
                coinTransactions.append(trans)
                myBlock.add_transaction(trans)
        else:
            print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
    
    return jsonify({'message': 'Chain delivered'})


@app.route('/takeBlockChatInfo', methods=['POST'])
def blockChatInfo():
    global state
    data = request.json
    for node in data["existingNodes"]:
        if node["port"]!=myNode.port:
          myNode.ring.append({"publickey":node["pubKey"].encode(), "id":node["id"],"ip":node["ip"],"port":node["port"],"balance":node["balance"], "stake":node["stake"]})
    
    ringInit=[]
    ring=copy.deepcopy(myNode.ring)
    for node in ring:
        if(node['id']!=0):
            ringInit.append(node)
            ringInit[len(ringInit)-1]['balance']=0
        else:
            ringInit.append(node)
            ringInit[len(ringInit)-1]['balance']=(totalNodes+1)*1000
    state={'ring': ringInit, 'BCC': 0,'nonces':copy.deepcopy(myNode.nonces)}

    while(len(coinTransactions)!=totalNodes-1):
        print('LENGTH', len(coinTransactions))
    for trans in coinTransactions:
        myNode.update_status(trans,True)

    return jsonify({'message': 'User registered successfully'})


@app.route('/makeTransaction', methods=['POST'])
def makeTrans():
        global broadcast_mined_block
        global broadcast_mined_block_isRead
        global myBlock
        global validator
        global state
        global transSent
        global startingTime
        global madeTransactionCounter

        if(madeTransactionCounter==0):
            startingTime=time.time()
            madeTransactionCounter=1

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
            # if node['port']!=myNode.port:
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
        # myNode.nonces[senderId]=trans.nonce+1
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
        validator.value=42
        minedBlockHandled=True
        return {"message":"mined block accepted"}
    else: 
        myBlock=Block(time.time(),binascii.hexlify((myNode.chain.blocks[len(myNode.chain.blocks)-1].myHash())).decode())
        validator.value=42
        minedBlockHandled=True
        return {"message":"mined block not accepted"}
    

# @app.route('/proxy', methods=['POST'])
# def proxy():
#     global transQueue
#     data = request.json
#     transQueue.appendleft(data)
#     return {'message':'transaction added'}




if __name__ == '__main__':
    app.run(port=myNode.port, debug=False)
    broadcastMinedBlockThread.join()
    # pushReqThread.join()
