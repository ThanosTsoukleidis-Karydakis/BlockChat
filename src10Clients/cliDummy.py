import requests
import json


data = {"type": "message", "content": 'GeiaaGeiaa', "id":1, "noFee": False} 

headers = {'Content-Type': 'application/json'}
response = requests.post('http://localhost:5002/makeTransaction', data=json.dumps(data), headers=headers)
print(response.text)