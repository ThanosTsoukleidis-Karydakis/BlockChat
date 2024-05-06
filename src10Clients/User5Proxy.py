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
#app2 = Flask(__name__)


transQueue=collections.deque()


def pushRequest():
     global transQueue
     while True:
        if(len(transQueue)>0):
 
            headers = {'Content-Type': 'application/json'}
            
            print('TRANS QUEUE', len(transQueue))
            time.sleep(0.05)
            trans=transQueue.pop()
            print('SENT TRANSACTION : ', time.time(), trans['content'])
                
            response = requests.post('http://'+'127.0.0.1'+':'+str(5004)+'/sendtransaction', data=json.dumps(trans), headers=headers)
            print(response.status_code)



t = threading.Thread(target=pushRequest)
t.start()


@app.route('/proxy', methods=['POST'])
def proxy():
    global transQueue
    with lock:
        data = request.json
        transQueue.appendleft(data)
        #print('\n\n\n\nTRANS APPENDED\n\n\n', transQueue)
        return {'message':'transaction added'}


if __name__ == '__main__':
     app.run(host='127.0.0.1', port=6004, debug=False)

