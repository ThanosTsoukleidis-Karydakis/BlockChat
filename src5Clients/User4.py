from node import Node
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
import time
from block import Block
from blockchain import Blockchain
from transaction import Transaction
from node import Node
import binascii
import json
import multiprocessing
import collections
import threading
import copy 

app = Flask(__name__)
CORS(app)

lock=threading.RLock()

totalNodes = 4
messages={}

# Initialize a new node
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

# make a request for joining the BlockChat
data={"pubKey": myNode.wallet[1].decode(), "port":myNode.port, "ip":myNode.ip}
headers = {'Content-Type': 'application/json'}
response = requests.post('http://127.0.0.1:5000/register', data=json.dumps(data), headers=headers).json()

# Initialization of the state
myNode.ring=[{"publickey": myNode.wallet[1], "id":response["id"], "ip":myNode.ip, "port":myNode.port, "balance":0, "stake":0}, {"publickey": response["pubKey"].encode(), "id":0, "ip":"127.0.0.1", "port":response["port"], "balance":0, "stake":0}]
myNode.id=response["id"]

# Initialize the genesis block that you will receive from the bootstrap node
genesisBlock=Block(1,1)

# Initizalize the second block of the chain
myBlock=Block(time.time(),"")



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
            state={'ring':copy.deepcopy(myNode.ring), 'BCC':copy.deepcopy(myNode.BCC),'nonces':copy.deepcopy(myNode.nonces)}
            validator.value=42
            print("MY BLOCKCHAIN's LENGTH : ", len(myBlockChain.to_list()))
            print("RING/STATE AFTER MINING", myNode.ring)
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

 


# this endpoint receives (from the proxy) and handles new transactions  
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
        if done==True:
            done=False
            data = request.json
            transaction = Transaction(data['sender_address'].encode(), data['receiver_address'].encode(), data['type_of_transaction'], data['content'],data['nonce'],data['signature'])
            # validate the transaction (if this is not a coin transaction)
            valid= myNode.validate_transaction(transaction.message, transaction.amount, data['signature'], data['type_of_transaction'],data['sender_address'], data['nonce'])
            # for coins transactions
            if data["noFee"]:
                valid=True
            if(valid):
                # don't update status for stake transactions
                if(transaction.type_of_transaction!='stake'):
                    update_status = myNode.update_status(transaction, data["noFee"])
                    if(update_status=="No match"):
                        coinTransactions.append(transaction)
                # check if the current block is going to get full
                if(len(myBlock.listofTransactions)+1<myBlock.capacity):
                    myNode.add_transaction_to_block(myBlock,transaction)
                    inverseTransactions.append(transaction.inverse())
                else:
                    myNode.add_transaction_to_block(myBlock,transaction)           
                    validator.value = myNode.mine_block(myBlock)
                    myBlock.validator=validator.value
                    print('VALIDATOR: ', validator.value)
                    # If I am the validator
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
                return {"message":"OK"}
            else:
                done=True
                return {"message":"Error in validating"}



@app.route('/getPublicKey', methods=['GET'])
def getPubKey():
    return myNode.wallet[1]


# take the current chain from the bootstrap node
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
    # save (in a buffer) the coins transactions that happened before joining the BlockChat
    for block in data['coinsBlock']:
        if block['receiver_address']!=myNode.wallet[1].decode():
            trans = Transaction(block['sender_address'].encode(), block['receiver_address'].encode(), block['type_of_transaction'], block['content'],block['nonce'],block['signature'])
            valid = myNode.validate_transaction(trans.message,trans.amount,trans.Signature, trans.type_of_transaction,block['sender_address'],block['nonce'])
            if(valid):
                coinTransactions.append(trans)
                myBlock.add_transaction(trans)
        else:
            print('This is the coins transaction created for me')
    return jsonify({'message': 'Chain delivered'})



# receive and handle the info provided by the bootstrap node at the end of bootstraping
@app.route('/takeBlockChatInfo', methods=['POST'])
def blockChatInfo():
    global state
    data = request.json
    # update state, add the other nodes inside
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
    # CHECKPOINT : save the initial state
    state={'ring': ringInit, 'BCC': 0,'nonces':copy.deepcopy(myNode.nonces)}

    # wait for all the initial coins transactions to be delivered
    while(len(coinTransactions)!=3):
        print('coinTransactions LENGTH', len(coinTransactions))
    # update the state according to the initial coins transactions that are saved into the buffer
    for trans in coinTransactions:
        myNode.update_status(trans,True)
    return jsonify({'message': 'User registered successfully'})



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
        key='0'.encode()   # default value for the stake transactions
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
            # if node['port']!=myNode.port:
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

    while(transSent==False or myUpdate==False):
        time.sleep(0)

    receivedStakeTrans=[]

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
        print("MY BLOCKCHAIN's LENGTH : ", len(myBlockChain.to_list()))
        print("RING/STATE AFTER MINING", myNode.ring)
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
    app.run(port=myNode.port, debug=False)
    broadcastMinedBlockThread.join()
    # pushReqThread.join()

