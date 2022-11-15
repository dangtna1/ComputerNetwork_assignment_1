""" Client implementation of P2P chat system. """

import os
import socket
import sys
import json
import threading
import time
import atexit  

from math import ceil
from base import Peer
from config import *

class Client(Peer):
    """ CLient implementation of P2P chat system.

    Args:
        - peername:     str                 Peer's name
        - serverhost:   str                 IP
        - serverport:   int                 The port occupied by the TCP socket receiving the message.
        - server_info:  tuple or list       IP and socket port of the server in the P2P network.
    
    Attributes:
        - peerlist:                 dict        All connected peer: {Peer's name: (Peer's ip, Peer's socket port)}
        - handlers:                 dict        {Received message type: The method of processing recvived messages}
        - static_input_mapping:     dict        {Command line arguments that have benn fixed: The method of processing arguments}    
        - dynamic_input_mapping:    dict        {Variable command line arguments: The method of processing arguments}
        - agree:                    variable    three values signal: None: waiting for input; True: accept chat request; False: Refuse chat request.
    """
    def __init__(self, peername=None, serverhost='localhost', serverport=40000, server_info=('localhost', 30000)):
        super(Client, self).__init__(serverhost, serverport)
        self.server_info = server_info  
        self.name = peername if peername is not None else ':'.join((serverhost, serverport))
        self.connectable_peer = {}
        # example name: 192.168.0.1:30000
        handlers = {
            CHAT_MESSAGE: self.recv_message,
            CHAT_ACCEPT: self.chat_accept,
            CHAT_REFUSE: self.chat_refuse,
            REQUEST: self.request,
            REGISTER_SUCCESS: self.register_success,
            REGISTER_ERROR: self.register_error,
            LISTPEER: self.display_all_peers,
            DISCONNECT: self.disconnect,
            FILE_TRANSFER: self.file_transfer, 
            FILE_TRANSFER_REQUEST: self.recv_file_transfer_request,
            FILE_TRANSFER_ACCEPT: self.recv_file_transfer_accept,
            FILE_TRANSFER_REFUSE: self.recv_file_transfer_refuse,
        }
        for message_type, func in handlers.items():
            self.add_handler(message_type, func)

        self.static_input_mapping = {
            'register': self.send_register,
            'listpeer': self.send_listpeer,
            'exit network': self.send_exit_network,

            'list connected peer': self.list_connected_peer,

            'yes': self.accept_request,
            'no': self.refuse_request,

            'help': self.input_prompt,
            
            'exit': self.system_exit,
        }
        self.dynamic_input_mapping = {  
            'request': self.input_request, 
            'chat message': self.input_chat_message,
            'disconnect': self.input_disconnect,
            'sendfile': self.input_sendfile,
        }
        self.agree = None  
        self.message_format = '{peername}: {message}'
        self.input_prompt_format = '    {cmd:<35} {prompt}'
        self.file_data = {}

    def file_transfer(self, msgdata):
        peername = msgdata['peername']
        filename = msgdata['filename']
        filenum = int(msgdata['filenum'])
        curnum = int(msgdata['curnum'])
        filedata = msgdata['filedata']
        
        key = peername + '_' + filename
        if self.file_data.get(key) is None:
            self.file_data[key] = [None] * filenum
        self.file_data[key][curnum] = filedata
        print(self.file_data[key])
        print(self.file_data.get(key) is None)

        flag = True
        for i in self.file_data[key]:
            if i is None:
                flag = False
                break
        if flag is True:
            with open(key, 'at', encoding='utf-8') as f:
                for i in self.file_data[key]:
                    f.write(i)

    def recv_file_transfer_request(self, msgdata):  
        pass

    def recv_file_transfer_accept(self, msgdata):
        pass
    
    def recv_file_transfer_refuse(self, msgdata):
        pass
    
    def disconnect(self, msgdata):
        """ Processing received messages from peer:
            Disconnect from the peer. """
        peername = msgdata['peername']
        if peername in self.peerlist:
            print('Disconnected from {}'.format(peername))
            del self.peerlist[peername]

    def register_success(self, msgdata):
        """ Processing received message from server:
            Successful registration on the server. """
        self.send_listpeer()  # Update connectable peer table
        print('Register Successful.')
    
    def register_error(self, msgdata):
        """ Processing received message from server:
            Registration failed on the server. """
        print('Register Error.')
    
    def display_all_peers(self, msgdata):
        """ Processing received message from server:
            Output information about all peers that have been registered on the server. """
        self.connectable_peer = {key:tuple(value) for key, value in msgdata['peerlist'].items()}
        print('display all peers:')
        # print(msgdata['peerlist'])
        for peername, peer_info in msgdata['peerlist'].items():
            print('peername: ' + peername + '---' + peer_info[0] + ':' + str(peer_info[1]))

    def recv_message(self, msgdata):
        """ Processing received chat message from peer."""
        peername = msgdata['peername']
        if peername in self.peerlist:
            print(self.message_format.format(peername=peername, message=msgdata['message']))
            # return self.message_format.format(peername=peername, message=msgdata['message'])
    
    def chat_accept(self, msgdata):
        """ Processing received accept chat request message from peer.
            Add the peer to collection of connected peers. """
        peername = msgdata['peername']
        host = msgdata['host']
        port = msgdata['port']
        print('chat accept: {} --- {}:{}'.format(peername, host, port))
        self.peerlist[peername] = (host, port) 
    
    def chat_refuse(self, msgdata):
        """ Processing received refuse chat request message from peer. """
        print('CHAT REFUSE!')
    
    def request(self, msgdata):
        """ Processing received chat request message from peer. """
        peername = msgdata['peername']
        host, port = msgdata['host'], msgdata['port']
        print('request: {} --- {}:{}'.format(peername, host, port))
        print('Please enter "yes" or "no":')
        while self.agree is None:  
            time.sleep(0.1)
        if self.agree is True:
            self.agree = None
            data = {
                'peername': self.name,
                'host': self.serverhost,
                'port': self.serverport
            }
            self.socket_send((host, port), msgtype=CHAT_ACCEPT, msgdata=data)
            self.peerlist[peername] = (host, port)
        elif self.agree is False:
            self.agree = None
            self.socket_send((host, port), msgtype=CHAT_REFUSE, msgdata={})
    
    def send_register(self):
        """ Send a request to server to register peer's information. """
        data = {
            'peername': self.name,
            'host': self.serverhost,
            'port': self.serverport
        }
        self.socket_send(self.server_info, msgtype=REGISTER, msgdata=data)

    def send_listpeer(self):
        """ Send a request to server to get all peers information. """
        data = {'peername': self.name}
        self.socket_send(self.server_info, msgtype=LISTPEER, msgdata=data)    
    
    def send_exit_network(self):
        """ Send a request to server to quit P2P network. """
        data = {'peername': self.name}
        self.socket_send(self.server_info, msgtype=EXIT_NETWORK, msgdata=data)
    
    def send_request(self, peername):  
        """ Send a chat request to peer. """
        if peername not in self.peerlist:
            try:
                server_info = self.connectable_peer[peername]
            except KeyError: 
                
                print('This peer ({}) is not registered.'.format(peername))
            else:
                data = {
                    'peername': self.name,
                    'host': self.serverhost,
                    'port': self.serverport
                }
                self.socket_send(server_info, msgtype=REQUEST, msgdata=data)
        else:
            print('You have already connected to {}.'.format(peername))
    
    def send_chat_message(self, peername, message):
        """ Send a chat message to peer. """
        try:
            peer_info = self.peerlist[peername]
        except KeyError:
            print('chat message: Peer does not exist.')
        else:
            data = {
                'peername': self.name,
                'message': message
            }
            self.socket_send(peer_info, msgtype=CHAT_MESSAGE, msgdata=data)
    
    def send_file(self, peername, filename):
        try:
            peer_info = self.peerlist[peername]
        except KeyError:
            print("send file: Peer does not exist.")
        else:
            read_per = 128
            tmp_text = []
            with open(filename, 'rt', encoding='utf-8') as f:
                while True:
                    text_data = f.read(read_per)
                    if not text_data:
                        break
                    tmp_text.append(text_data)
            tran_num = len(tmp_text)
            for index, item in enumerate(tmp_text):
                data = {
                    'peername': self.name,
                    'filename': filename,
                    'filenum': tran_num,
                    'curnum': index,
                    'filedata': item
                }
                self.socket_send(peer_info, msgtype=FILE_TRANSFER, msgdata=data)

    def send_disconnect(self, peername):
        """ Send a disconnect request to peer. """
        try:
            peer_info = self.peerlist[peername]
        except KeyError:
            print('disconnect: Peer does not exist.')
        else:
            data = {'peername': self.name}
            self.socket_send(peer_info, msgtype=DISCONNECT, msgdata=data)
        

    def list_connected_peer(self):
        """ Output all connected peers information. """
        for peername, peer_info in self.peerlist.items():
            print('peername: ' + peername + '---' + peer_info[0] + ':' + str(peer_info[1]))
    
    def classifier(self, msg):
        """ Scheduling methods. """
        type_ = msg['msgtype']
        data_ = msg['msgdata']
        self.handlers[type_](data_)

    def recv(self):
        """ TCP socket that receives information. """
        while True:
            conn, addr = self.socket.accept()          
            buf = conn.recv(2048)
            msg = json.loads(buf.decode('utf-8'))
            self.classifier(msg)

    def input_request(self, cmd):
        try:
            peername = cmd.split(' ', maxsplit=2)[-1]
        except IndexError:
            print('chat request: Arguments Error.')
        else:
            self.send_request(peername)
    
    def input_chat_message(self, cmd):
        try:
            peername, message = cmd.split(' ', maxsplit=3)[-2:]  
        except IndexError:
            print('chat message: Arguments Error.')
        else:
            self.send_chat_message(peername, message)
    
    def input_disconnect(self, cmd):
        try:
            peername = cmd.split(' ', maxsplit=1)[-1]
        except IndexError:
            print('disconnect: Arguments Error.')
        else:
            self.send_disconnect(peername)
            if peername in self.peerlist:
                del self.peerlist[peername]

    def input_sendfile(self, cmd):
        try:
            peername, filename = cmd.split(' ', maxsplit=3)[-2:]
        except IndexError:
            print('Error: sendfile.')
        else:
            self.send_file(peername, filename)

    def accept_request(self):
        self.agree = True
    
    def refuse_request(self):
        self.agree = False
    
    def system_exit(self):  
        for peername in self.peerlist: 
            try:
                self.send_disconnect(peername)
            except ConnectionRefusedError:
                pass
            except:
                pass
        try:
            self.send_exit_network()  
        except ConnectionRefusedError:
            pass
        except:
            pass
        sys.exit()  
    def input_prompt(self):
        print('command list:')
        print(self.input_prompt_format.format(cmd='register', prompt='đăng ký'))
        print(self.input_prompt_format.format(cmd='listpeer', prompt='liệt kê bạn bè'))
        print(self.input_prompt_format.format(cmd='exit network', prompt='thoát kết nối mạng'))
        print(self.input_prompt_format.format(cmd='request [peername]', prompt='yêu cầu kết bạn'))
        print(self.input_prompt_format.format(cmd='chat message [peername] [message]', prompt='nhắn tin cho [bạn bè cụ thể] [tin nhắn]'))
        print(self.input_prompt_format.format(cmd='list connected peer', prompt='liệt kê những người đang kết nối mạng'))
        print(self.input_prompt_format.format(cmd='help', prompt='hỗ trợ'))
        print(self.input_prompt_format.format(cmd='disconnect [connected peer name]', prompt='hủy kết nối với [bạn bè cụ thể]'))
        print(self.input_prompt_format.format(cmd='exit', prompt='thoát'))

    def run(self):
        atexit.register(client.system_exit)  
        
        t = threading.Thread(target=self.recv)  
        t.setDaemon(True)
        t.start()
        
        self.input_prompt()
        while True:
            cmd = input().strip()
            if cmd in self.static_input_mapping:
                self.static_input_mapping[cmd]()
            else:
                flag = False
                for keyword in self.dynamic_input_mapping:
                    if cmd.startswith(keyword):
                        flag = True
                        self.dynamic_input_mapping[keyword](cmd)
                        break
                if flag is False:
                    print('Error! Please enter correct command.')
                    self.input_prompt()

if __name__ == '__main__':
    serverport = int(input('serverport: '))
    peername = input('Your name: ')
    client = Client(peername=peername, serverport=serverport)
    client.run()
