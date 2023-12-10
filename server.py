import socket
import threading
import json
import sys
import os

#constaints
HEADER = 64
PORT = 8080 # server port
# get IPv4
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

class Server:
    def __init__(self) -> None:
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind(ADDR)
        
        self.__client_list = [] # used for ping | {(SERVER, PORT, HOSTNAME)}
        self.__client_file_repo = {} # dictionary used for find files of a user | (SERVER, PORT, HOSTNAME): {dictionary of filename}
        self.__file_repo = {} # dictionary used for find users that have a file | filename: {dic of clients (SERVER, PORT, HOSTNAME, FILE_PORT): lname}
        self.__client_file_repo_lock = threading.Lock() # thread lock
        self.__file_repo_lock = threading.Lock()
        self.lock = threading.Lock()
        self.server_run = False
        
    def __handle_client(self, conn, addr): # mock
        print(f"\n[NEW CONNECTION] {addr} {socket.gethostbyaddr(addr[0])[0]} connected.")
        connected = True
        while connected: # (PUBLISH len(lname) len(fname)            lname fname
            # client sendall
            header = conn.recv(HEADER).decode(FORMAT)
            if header:
                header = header.split() 
                req_type = header[0]
                if (req_type == "PUBLISH"):
                    lname_length = int(header[1])
                    fname_length = int(header[2])
                    client_file_port_length = int(header[3])
                    hostname_length = int(header[4])
                    
                    lname = conn.recv(lname_length).decode(FORMAT)
                    fname = conn.recv(fname_length).decode(FORMAT)
                    client_file_port = conn.recv(client_file_port_length).decode(FORMAT)
                    client_file_port = int(client_file_port)
                    hostname = conn.recv(hostname_length).decode(FORMAT)
                    self.__handle_client_publish(addr, fname, lname, client_file_port, hostname)
                    
                elif (req_type == "FETCH"):
                    fname_length = int(header[1])
                    fname = conn.recv(fname_length).decode(FORMAT)
                    self.__handle_client_fetch(fname, addr, conn)
                    
                elif (req_type == "CONNECT"):
                    hostname_length = int(header[1])
                    hostname = conn.recv(hostname_length).decode(FORMAT)
                    self.__handle_client_connect(addr, hostname)
                    
                elif (req_type == "DISCONNECT"):
                    msg = conn.recv(1024).decode(FORMAT)
                    if (msg == DISCONNECT_MESSAGE):
                        connected = False
                        ip_to_remove = addr[0]
                        port_to_remove = addr[1]
                        hostname = socket.gethostbyaddr(ip_to_remove)[0]

                        # Remove the specific tuple based on IP and port
                        self.__client_list = [client for client in self.__client_list if (client[0] != ip_to_remove) and (client[1] != port_to_remove)]
                    
                    print(f"{addr} {msg}")
        conn.close()
        
    def __handle_request(self):
        while True:
            conn, addr = self.__server_socket.accept()
            thread = threading.Thread(target=self.__handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTION] {threading.active_count() - 2}")
                    
    def start(self):
        print("[STARTING] Server is starting...")
        self.__server_socket.listen()
        print(f"[LISTENING] Server is listening on {SERVER}")
        # thread = threading.Thread(target=self.server_ui)
        # thread.start()
        self.server_run=True
        self.__handle_request()
        
    def stop(self):
        self.__server_socket.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
            
    def __handle_client_connect(self, addr, hostname):
        self.__client_list.append((addr[0], addr[1], hostname))
        
    def __handle_client_publish(self, addr, fname, lname, client_file_port, hostname): # add fname to __client_file_repo
        client_info = (addr[0], addr[1], hostname, client_file_port)
        
        if client_info not in self.__client_file_repo:
            self.__client_file_repo[client_info] = []
        with self.__client_file_repo_lock:
            if (lname, fname) not in self.__client_file_repo[client_info]:
                self.__client_file_repo[client_info].append((lname, fname))
            else:
                print("You already uploaded this file")
                
        if fname not in self.__file_repo:
            self.__file_repo[fname] = {}
        with self.__file_repo_lock:
            self.__file_repo[fname][client_info] = lname
    
    def __handle_client_fetch(self, fname, addr, conn):
        if fname not in self.__file_repo:
            print("Not host has this file")
        else:
            file_host_addr = self.__file_repo[fname]
            if (addr in file_host_addr):
                print("You already have this file in your repository!")
            else:
                # print(f"Host {file_host_addr} has this file: {fname}!")
                response_data = (json.dumps({str(k): v for k, v in file_host_addr.items()})).encode(FORMAT)
                response_length = len(response_data)
                
                header = f'200 OK! {response_length}'
                
                header = header.encode(FORMAT)
                header += b' ' * (HEADER - len(header))
                
                conn.sendall(header + response_data)
    
    def __discover(self, hostname):
        filtered_clients = {key: value for key, value in self.__client_file_repo.items() if key[2] == hostname}
        print(f"all files in {hostname} repository:")
        print(filtered_clients)
    
    def __ping(self, hostname):
        matching_entries = [entry for entry in self.__client_list if entry[2] == hostname]
        if len(matching_entries) > 0:
            print(matching_entries)
        else:
            print(f"No host name {hostname} is currently active")
    
    def invalid_input(self):
        raise Exception("Invalid input")
    
    # def server_ui(self):
    #     print("TEST UI")
    #     command_dic = { '1': self.__discover, '2': self.__ping}
    #     while True:
    #         try: 
    #             req = input('\n1. Discover, 2. Ping, 3. Stop: ')
    #             command = command_dic.get(req, self.invalid_input)
    #             if (req == '3'):
    #                 self.stop()
    #                 break
    #             hostname = input("Enter hostname: ")
    #             command(hostname)
    #         except Exception as e:
    #             print(f"Error: {e}")
    
# server = Server()
# server.start()
