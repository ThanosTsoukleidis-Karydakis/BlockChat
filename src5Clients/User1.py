from node import Node
import requests
from flask import Flask, request
from flask_cors import CORS
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
from node import Node

lock=threading.RLock()

app = Flask(__name__)
CORS(app)

messages={}

manager = multiprocessing.Manager()
existingNodes = manager.list([])
transSent=True
state=[]
done=True
# inverse transactions of the current block

broadcast_mined_block=manager.Value('i',False)
broadcast_mined_block_isRead=manager.Value('i',False)
validator = manager.Value('i', 42)
myUpdate=False
transQueue=collections.deque()
madeBroadcast=False
minedBlockHandled=False
registerPhase = [True]

coinsSent = manager.dict({})
coinsSent["5001"]=True
coinsSent["5002"]=True
coinsSent["5003"]=True
coinsSent["5004"]=True
totalNodes = 4

# Initialization of the bootstrap node
myNode=Node(5000,"127.0.0.1")
myNode.id=0
myNode.nonce=0
myBlockChain=Blockchain()

#create and handle genesis transaction
genesisBlock=Block(time.time(),1)
genesisTransaction = Transaction(myNode.wallet[1], myNode.wallet[1], "coins", 1000*(totalNodes+1),0,'')
genesisTransaction.sign_transaction(myNode.wallet[0])
genesisBlock.add_transaction(genesisTransaction)
myBlockChain.add_block(genesisBlock)
myNode.chain=myBlockChain
myNode.handleGenesisTransaction(genesisTransaction)

# Initialization of the state
myNode.ring=[{"publickey": myNode.wallet[1], "id":0, "ip":myNode.ip, "port":myNode.port, "balance":myNode.BCC, "stake":0}]

# Initialization of the 2nd block of the blockchain
myBlock=Block(time.time(),binascii.hexlify((myNode.chain.blocks[len(myNode.chain.blocks)-1].myHash())).decode())

# this function is executed by a new thread during the bootstraping. If a new node is registered, the bootstrap node sends the current blockchain and 1000 coins. 
# If this node was the last expected one, this thread broadcasts info about all the nodes.  
def send_coins():
     global myBlock
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
                    # checks if the block is full during the bootstraping
                    if(len(myBlock.listofTransactions)+1<myBlock.capacity):
                        myNode.add_transaction_to_block(myBlock,sendCoinsTrans)
                    else:
                         myNode.add_transaction_to_block(myBlock,sendCoinsTrans)
                         validator.value= myNode.mine_block(myBlock)
                         if validator.value==0:   
                            myBlockChain.blocks.append(myBlock)
                            myNode.chain=myBlockChain
                            broadcast_mined_block=True
                            if broadcast_mined_block_isRead==True:
                                broadcast_mined_block_isRead=False
                                myBlock=Block(time.time(), binascii.hexlify((myNode.chain.blocks[len(myNode.chain.blocks)-1].myHash())).decode())
                         else:
                              myBlock=Block(time.time(), "")

                    # send the chain and 1000 coins to the new node
                    myNode.update_status(sendCoinsTrans,True)
                    data2 = sendCoinsTrans.to_dict()
                    data2["noFee"]=True
                    headers = {'Content-Type': 'application/json'}
                    chainData={"chain": myBlockChain.to_list(), 'coinsBlock': myBlock.to_list(), 'genesisTimestamp':genesisBlock.timestamp}

                    sendChainTransResponse = requests.post('http://'+node["ip"]+':'+str(node["port"])+'/takeChain', data=json.dumps(chainData), headers=headers)
                 
                    for node in existingNodes:
                        sendCoinsTransResponse = requests.post('http://'+node["ip"]+":"+str(node["port"])+'/sendtransaction', data=json.dumps(data2), headers=headers)

                    # if this node was the last one, broadcast info about the nodes
                    if (len(existingNodes) == totalNodes)  :
                        headers = {'Content-Type': 'application/json'}
                        for node in existingNodes:
                            last=existingNodes[len(existingNodes)-1]
                            if True:
                                data={"existingNodes":list(existingNodes)}
                                res = requests.post('http://'+node["ip"]+':'+str(node['port'])+'/takeBlockChatInfo', data=json.dumps(data), headers=headers).json()

t = threading.Thread(target=send_coins)
t.start()




# this function is executed by a new thread. If this node is the validator, this thread broadcasts this block
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

            # revalidate any stake transaction into this block (read the report)
            for trans in blockToSend.listofTransactions:
                if(trans.type_of_transaction=='stake'):
                    valid=None
                    for node in myNode.ring:
                        if node['publickey']==trans.sender_address:
                            valid=(node['balance']-trans.content>=0)
                    if(valid):
                        myNode.update_status(trans, True)
            
            # compute the fee of the mined block and update my state
            for trans in blockToSend.listofTransactions:
                    if(trans.nonce not in [1,2,3,4]):
                        blockToSend.change_fee(trans)
            myNode.BCC=myNode.BCC+blockToSend.fee
            for node in myNode.ring:
                if(node["port"]==myNode.port):
                    node["balance"]=node["balance"]+blockToSend.fee
            
            # Checkpoint : save the current state, maybe you will need this for a rollback
            state={'ring':copy.deepcopy(myNode.ring), 'BCC':copy.deepcopy(myNode.BCC), 'nonces':copy.deepcopy(myNode.nonces)}
            
            validator.value=42
            print("MY BLOCKCHAIN's LENGTH: ", len(myBlockChain.to_list()))
            print("RING/STATE AFTER MINING", myNode.ring)
            print("MY BCC", myNode.BCC)
            madeBroadcast=True

broadcastMinedBlockThread = threading.Thread(target=broadcastMinedBlock)
broadcastMinedBlockThread.start()


    
# this endpoint receives (from the proxy) and handles new transactions  
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
        if done==True:
            done=False
            data = request.json
            transaction = Transaction(data['sender_address'].encode(), data['receiver_address'].encode(), data['type_of_transaction'], data['content'],data['nonce'],data['signature'])
            # validate the transaction
            valid= myNode.validate_transaction(transaction.message, transaction.amount, data['signature'], data['type_of_transaction'],data['sender_address'], data['nonce'])
            if(valid):
                # don't update status for stake transactions
                if(transaction.type_of_transaction!='stake'):
                    myNode.update_status(transaction, data["noFee"])
                # check if the current block is going to get full
                if(len(myBlock.listofTransactions)+1<myBlock.capacity):
                    myNode.add_transaction_to_block(myBlock,transaction)              
                else:
                    myNode.add_transaction_to_block(myBlock,transaction) 
                    validator.value = myNode.mine_block(myBlock)
                    myBlock.validator=validator.value
                    print('VALIDATOR: ', validator.value)    
                    # if I am the validator        
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
                return {'message':'OK'}
            else:
                done=True
                return {"message":"error in validating"}



@app.route('/getPublicKey', methods=['GET'])
def getPubKey():
    return myNode.wallet[1]



# handle requests for joining the BlockChat
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
        # CHECKPOINT : save current state
        state={'ring': ringInit, 'BCC': (totalNodes+1)*1000, 'nonces':copy.deepcopy(myNode.nonces)}


    if (len(existingNodes) == totalNodes)  :
                coinsSent[str(dport)]=False
                registerPhase[0]=False
    coinsSent[str(dport)]=False
    #return the bootstrap's publickey to every new node
    return {"port":myNode.port,"pubKey": myNode.wallet[1].decode(), "id": len(existingNodes), "OK":"OK"}


# handle a new made transaction
@app.route('/makeTransaction', methods=['POST'])
def makeTrans():
        global broadcast_mined_block
        global broadcast_mined_block_isRead
        global myBlock
        global validator
        global state
        global transSent
        input=request.json
        transSent=False
        key='0'.encode() # default value for the stake transactions
        port=""
        # find the publickey that matches with the given id
        for node in myNode.ring:
             if(node["id"]==input["id"]):
                  key=node["publickey"]
        trans = myNode.create_transaction(key,input["type"],input["content"])
        trans.sign_transaction(myNode.wallet[0])
        data = trans.to_dict()
        data["noFee"]=input["noFee"]
        headers = {'Content-Type': 'application/json'}
        # broadcast transaction to all proxies
        for node in myNode.ring:
            response = requests.post('http://'+node["ip"]+':'+str(node["port"]+1000)+'/proxy', data=json.dumps(data), headers=headers)

        transSent=True
        return {"message":"transaction broadcasted to proxies"}

# Handle the new block that was sent by the validator
@app.route('/takeMinedBlock', methods=['POST'])
def takeMinedBlock():
    global validator
    global state
    global transSent
    global myUpdate
    global minedBlockHandled
    global myBlock

    receivedStakeTrans=[]

    while(transSent==False or myUpdate==False):
         time.sleep(0)

    myUpdate=False

    # reconstruct the block from its fields and rerun the transactions of this block
    data = request.json
    minedBlockList = data["minedBlock"]
    minedBlock = Block(data["timestamp"],binascii.hexlify((myNode.chain.blocks[len(myNode.chain.blocks)-1].myHash())).decode())
    # return to the previous state (rollback)
    myNode.ring=state['ring']
    myNode.BCC=state['BCC']
    for transList in minedBlockList:
        trans = Transaction(transList['sender_address'].encode(),transList['receiver_address'].encode(),transList['type_of_transaction'],transList['content'],transList['nonce'],transList['signature'])
        minedBlock.add_transaction(trans)
        senderId=""
        for node in myNode.ring:
             if node['publickey'].decode()==transList['sender_address']:
                  senderId=str(node['id'])
        if(trans.nonce not in [1,2,3,4]):
            if(trans.type_of_transaction=='stake'):
                receivedStakeTrans.append(trans)
            else:
                minedBlock.change_fee(trans)
                print('THIS IS YOUR UPDATE STATUS')
                myNode.update_status(trans, False)
        elif(trans.nonce in [1,2,3,4]):
             myNode.update_status(trans, True)

    # revalidate the stake transactions of this block (read the report to understand why)
    for trans in receivedStakeTrans:
        valid=None
        for node in myNode.ring:
            if node['publickey']==trans.sender_address:
                valid=(node['balance']-trans.content>=0)
        print('IS THIS STAKE TRANSACTION STILL VALID ? ', valid)
        if(valid):
            myNode.update_status(trans,True)


    while(validator.value==42):
        time.sleep(0)


    minedBlock.validator=validator.value
    # validate the received block and add this to your chain
    validated = myNode.validate_block(minedBlock, str(request.remote_addr), validator.value)
    if(validated):
        for node in myNode.ring:
            if node["id"]==validator.value:
                node["balance"]=node["balance"]+minedBlock.fee
                state={'ring':copy.deepcopy(myNode.ring), 'BCC':copy.deepcopy(myNode.BCC),'nonces':copy.deepcopy(myNode.nonces)}
        myBlockChain.add_block(minedBlock)
        myNode.chain=myBlockChain
        myBlock=Block(time.time(), binascii.hexlify(minedBlock.myHash()).decode())
        print("MY BLOCKCHAIN's LENGTH: ", len(myBlockChain.to_list()))
        print("RING/STATE AFTER MINING", myNode.ring)
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
#     print('\n\n\n\nTRANS APPENDED\n\n\n', transQueue)
#     return {'message':'transaction added'}


# retrieve the node's balance
@app.route('/getBalance', methods=['GET'])
def getBalance():
    return {'balance':myNode.BCC}


# get the last validated block of the chain and its validator
@app.route('/getLastBlock', methods=['GET'])
def view_block():
    return {'lastBlock':myNode.chain.blocks[len(myNode.chain.blocks)-1].to_list(), 'validator': myNode.chain.blocks[len(myNode.chain.blocks)-1].validator}


# get outgoing coins transactions
@app.route('/getOutgoingMoneyTransfers', methods=['GET'])
def getOutgoingMoneyTransfers():
    outgoingTrans=[]
    for blockList in myBlockChain.to_list():
         for trans in blockList:
              if trans['type_of_transaction']=='coins':
                if trans['sender_address']==myNode.wallet[1].decode():
                    outgoingTrans.append(trans)
    return {'outGoingTransactions':outgoingTrans}

# get ingoing coins transactions
@app.route('/getIngoingMoneyTransfers', methods=['GET'])
def getIngoingMoneyTransfers():
    ingoingTrans=[]
    for blockList in myBlockChain.to_list():
         for trans in blockList:
              if trans['type_of_transaction']=='coins':
                if trans['receiver_address']==myNode.wallet[1].decode():
                    ingoingTrans.append(trans)
    return {'inGoingTransactions':ingoingTrans}


# get outgoing message transactions
@app.route('/getOutgoingMessages', methods=['GET'])
def getOutgoingMessages():
    outgoingTrans=[]
    for blockList in myBlockChain.to_list():
         for trans in blockList:
              if trans['type_of_transaction']=='message':
                if trans['sender_address']==myNode.wallet[1].decode():
                    outgoingTrans.append(trans)
    return {'outGoingTransactions':outgoingTrans}


# get ingoing message transactions
@app.route('/getIngoingMessages', methods=['GET'])
def getIngoingMessages():
    ingoingTrans=[]
    for blockList in myBlockChain.to_list():
         for trans in blockList:
              if trans['type_of_transaction']=='message':
                if trans['receiver_address']==myNode.wallet[1].decode():
                    ingoingTrans.append(trans)
    return {'inGoingTransactions':ingoingTrans}


# retrieve my stake
@app.route('/getStake', methods=['GET'])
def getStake():
    return {'stake':myNode.stakes[myNode.id]}

# check how many transaction left in order for a new block to get full
@app.route('/getRemainingTransactions', methods=['GET'])
def getRemainingTransactions():
    return {'number':myBlock.capacity-len(myBlock.listofTransactions)}


# get the blocks that this node has validated and their position into the chain
@app.route('/getMyMinedBlocks', methods=['GET'])
def getMyMinedBlocks():
    myMinedBlocks=[]
    counter=0
    for block in myBlockChain.blocks:
         if(counter!=0): 
            if(block.validator==myNode.id):
                myMinedBlocks.append([counter,block.fee])
         counter=counter+1
    return {'myMinedBlocks':myMinedBlocks}

               
if __name__ == '__main__':
     app.run(host=myNode.ip, port=myNode.port, debug=False)
     broadcastMinedBlockThread.join()

