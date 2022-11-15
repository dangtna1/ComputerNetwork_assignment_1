import socket
import json
import threading

from base import Peer
from config import *
class Server(Peer):
    """ Server implementation of P2P chat system. """
    def __init__(self, serverhost='localhost', serverport=30000):
        super(Server, self).__init__(serverhost, serverport)
        handlers = {
            REGISTER: self.register,
            LISTPEER: self.listpeer,
            EXIT_NETWORK: self.exit_network,
        }
        for message_type, func in handlers.items():
            self.add_handler(message_type, func)

    def add_handler(self, message_type, func):
        self.handlers[message_type] = func

    def exit_network(self, msgdata):
        peername = msgdata['peername']
        if peername in self.peerlist:
            del self.peerlist[peername]

    def register(self, msgdata):
        peername = msgdata['peername']
        host = msgdata['host']
        port = msgdata['port']
        if peername in self.peerlist: 
            self.socket_send((host, port), msgtype=REGISTER_ERROR, msgdata={})
        else:
            self.peerlist[peername] = (host, port)
            self.socket_send(self.peerlist[peername], msgtype=REGISTER_SUCCESS, msgdata={})

    def listpeer(self, msgdata):  
        peername = msgdata['peername']
        if peername in self.peerlist:
            data = {'peerlist': self.peerlist}
            self.socket_send(self.peerlist[peername], msgtype=LISTPEER, msgdata=data)

    def classifier(self, msg):
        type_ = msg['msgtype']
        data_ = msg['msgdata']
        self.handlers[type_](data_)

    def run(self):
        t = threading.Thread(target=self.recv)
        t.setDaemon(True)
        t.start()
        
        while True:
            cmd = input().strip()


if __name__ == '__main__':
    server = Server()
    print(server.socket)
    server.run()
