# P2P_Chat

A chat application for a simple P2P network.


## Example

    serverport: 40000
    Your name: Hawk
    
    command list:
        register                          
        listpeer                            
        exit network                        
        request [peername]        
        chat message [peername] [message]   
        list connected peer                
        help                               
        disconnect [connected peer]                      
        exit                                
    
    >> register
    
    Register Successful.
    
    >> listpeer
    
    display all peers:
    peername: dawn---localhost:4000
    peername: hawk---localhost:40000
    
    >> chat request dawn
    
    chat accept: dawn --- localhost:4000
    
    >> chat message dawn Hello, dawn.
    
    >> disconnect dawn
    
    >> exit


Server:

![](example/server.png)

ClientA:

![](example/clientA.png)

ClientB:

![](example/clientB.png)