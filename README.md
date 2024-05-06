# BlockChat
The objective of this semester project was the creation of BlockChat: a blockchain-based platform through which  
participants are able to exchange messages and coins (known as BlockChat coins - BCC).  
Apart from the BlockChat implementation, we have also created a simple frontend application,  
through which each user can make coin transactions or send messages to other participants   
in the blockchain, as well as manage his stake and see how many blocks he has mined (a Proof-of-Stake  
algorithm is used for mining of new blocks).  
For the Backend we have used Python Flask, and for the Frontend React JS.  

## Collaborators  
- [Athanasios Tsoukleidis-Karydakis](https://github.com/ThanosTsoukleidis-Karydakis)  (el19009)
- [Dimitrios-David Gerokonstantis](https://github.com/DimitrisDavidGerokonstantis)  (el19209)
- [Ioannis Karavgoustis](https://github.com/GiannisKaravgoustis) (el19847)

In this repository, the following folders are included:  

- **src5Clients:** Contains the BlockChat code for 5 clients in our blockchain. It also contains detailed code comments.  

- **src10Clients:** Extension of the 5 clients implementation for 10 clients (more client files and chanegs in some parameters).
It doesn't contain code comments, but the implementation is virtually the same to the one for 5 clients.  

Note: The code runs perfectly on Linux systems, but requires some modifications to run on Windows. All threads need  
to be defined in a new main function that is then being called to start a particular client. In addition, shared  
variables defined through managers need to be defined simply as global variables. 
Example for User1.py: 

```
def main():
    t = threading.Thread(target=send_coins)
    t.start()
    broadcastMinedBlockThread = threading.Thread(target=broadcastMinedBlock)
    broadcastMinedBlockThread.start()
    app.run(host=myNode.ip, port=myNode.port, debug=False)
    broadcastMinedBlockThread.join()


if name == '__main__':
    main()
```

Inside the src folders, one can find the cli folder that implements a cli as specified in the report. The cli  
is only implemented for the first user: it can easily be implemented for other users by changing the ports in  
the requests being made by the various cli commands. In order for the cli to work, one needs to follow the  
instructions in the report. Using run.py file, all users can be started immediately and the cli#.py files  
read inputs from the given trans#.txt files that are used to conduct the performance measurements presented  
in our report.  


- **report:** Contains the report of our project, alongside the corresponding Latex code.

- **frontend:** Contains the frontend of the application implemented with React.js. It is connected to the backend
of the first user (similarly with the cli) and can be used for another user by changing the ports used by the axios
requests. The frontend endpoints have only been added to the src5Clients use case. In the folder's README.md, the
various screens of the application are presented.     

## Backend layout (Component Diagram - Activity Diagram):  
Below, one can view the Component Diagram that describes how we have implemented each client and the  
communication between the different clients (more information in our report).  

![image](https://github.com/ThanosTsoukleidis-Karydakis/BlockChat/assets/106911775/9378fba9-34ec-4937-949a-79cbbfb4226c)  

Furthermore, the Activity Diagram presented below depicts fully all the available actions a user can make, alongside  
everything that happens "behind the scenes".  

![image](https://github.com/ThanosTsoukleidis-Karydakis/BlockChat/assets/106911775/e1d12cc9-c631-4f2a-9a14-d7ff493bf172)
