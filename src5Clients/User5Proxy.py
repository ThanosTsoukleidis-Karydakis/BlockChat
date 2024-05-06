import requests
from flask import Flask, request
from flask_cors import CORS
import json
import threading
import collections
import time

lock=threading.Lock()

app = Flask(__name__)
CORS(app)

transQueue=collections.deque()


# push requests from the queue to the /sendtransaction endpoint in a sequential order
def pushRequest():
     global transQueue
     while True:
        if(len(transQueue)>0):
            headers = {'Content-Type': 'application/json'}
            print('TRANSACTIONS QUEUE LENGTH : ', len(transQueue))
            time.sleep(0.1)
            trans=transQueue.pop()
            print('TRANSACTION WAS PUSHED : ', time.time(), trans['content'])
            response = requests.post('http://'+'127.0.0.1'+':'+str(5004)+'/sendtransaction', data=json.dumps(trans), headers=headers)
            print('STATUS CODE: ',response.status_code)

t = threading.Thread(target=pushRequest)
t.start()



# receive transactions and add them to the queue. Lock is needed!
@app.route('/proxy', methods=['POST'])
def proxy():
    global transQueue
    with lock:
        data = request.json
        transQueue.appendleft(data)
        return {'message':'transaction added'}


if __name__ == '__main__':
     app.run(host='127.0.0.1', port=6004, debug=False)

