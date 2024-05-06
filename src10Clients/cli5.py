import re

def removeNonAsciiChars(inputString):
    cleaned_string = re.sub(r'[^\x00-\x7F]+', '', inputString)
    return cleaned_string


import requests
import json
import time
counter=0
# Open the file
with open('../inputs/input/trans4.txt', 'r') as file:
    # Read the file line by line
    for line in file:
        if counter<101:
            # Extract id and message from the line
            line_id, line_message = line.strip().split(' ', 1)[0][2:], line.strip().split(' ', 1)[1]


            data = {"type": "message", "content": (line_message), "id": int(line_id), "noFee": False}
            #data = {"type": "message", "content": "YES!!!!......??????''dm58!!.", "id": int(line_id), "noFee": False}
            
            # Set the headers
            headers = {'Content-Type': 'application/json'}
        
            
            # Make the POST request
            response = requests.post('http://localhost:5004/makeTransaction', data=json.dumps(data), headers=headers)
            counter=counter+1
            # Print the response
            print(counter, response.text)