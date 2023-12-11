import socket
import json
import threading
import ast
import sys
import os


HEADER = 64
PORT = 8080 # target port
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = '192.168.172.19'
ADDR = (SERVER, PORT)

class Client:
    def __init__(self):
        is_connected = False
        self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.FILE_PORT = None
        self.__upload_online = True
        self.choose_file_to_fetch=None
   
    def start(self):
        try:
            self.__client_socket.connect(ADDR)
        except:
            print("Cannot connect to server")
            sys.exit(0)
        self.is_connected = True
        
        self.__send_connect_info()
        
        upload_thread = threading.Thread(target=self.__init_host)
        upload_thread.start()
        
        while self.FILE_PORT is None:
            # wait until upload port is initialized
            pass
        print('Listening on the upload port %s' % self.FILE_PORT)
        
    def stop(self):
        try:
            msg = DISCONNECT_MESSAGE
            message = msg.encode(FORMAT)
            msg_length = len(message)
            header = f'DISCONNECT {msg_length}'
            header = header.encode(FORMAT)
            header += b' ' * (HEADER - len(header))
            self.__client_socket.sendall(header + message)
            self.is_connected = False
            self.__upload_online = False
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        except:
            pass
        
    def __send_connect_info(self):
        hostname_data = socket.gethostname().encode(FORMAT)
        header = 'CONNECT'
        header += f' {len(hostname_data)}'
        header = header.encode(FORMAT)
        header += b' ' * (HEADER - len(header))
        self.__client_socket.sendall(header + hostname_data)
        
    def publish(self, lname, fname):
        lname_data = lname.encode(FORMAT)
        fname_data = fname.encode(FORMAT)
        file_port_data = str(self.FILE_PORT).encode(FORMAT)
        hostname_data = socket.gethostname().encode(FORMAT)
        header = 'PUBLISH'
        header += f' {len(lname)} {len(fname)} {len(file_port_data)} {len(hostname_data)}'
        header = header.encode(FORMAT)
        header += b' ' * (HEADER - len(header))
        self.__client_socket.sendall(header + lname_data + fname_data + file_port_data + hostname_data)
        self.__receive_publish_response()
        
    def fetch(self, fname):
        fname_data = fname.encode(FORMAT)
        header = 'FETCH'
        header += f" {len(fname)}"
        header = header.encode(FORMAT)
        header += b' ' * (HEADER - len(header))
        self.__client_socket.sendall(header + fname_data)
        self.__receive_fetch_response(fname)
        
    def __receive_publish_response(self):
        response_header = self.__client_socket.recv(HEADER).decode(FORMAT)
        response_header = response_header.split()
        if response_header:
            status_code = response_header[0]
            response_length = int(response_header[2])
            response_data = self.__client_socket.recv(response_length).decode(FORMAT)
            print(response_data)
    
    def __receive_fetch_response(self, fname):
        response_header = self.__client_socket.recv(HEADER).decode(FORMAT)
        response_header = response_header.split()
        if response_header:
            status_code = response_header[0]
            if (status_code == '200'):
                response_length = int(response_header[2])
                response_data_json = self.__client_socket.recv(response_length).decode(FORMAT)
                response_data = json.loads(response_data_json)
                response_data = {tuple(ast.literal_eval(k)): v for k, v in response_data.items()}
                keys_list = list(response_data.keys())
                if(self.choose_file_to_fetch and self.choose_file_to_fetch.strip()):
                    host = keys_list[int(self.choose_file_to_fetch)] #keys_list[index]
                    lname = response_data[host]
                    self.send_download_request(lname, host[0], host[3], fname)
                    self.choose_file_to_fetch=''
                else:
                    for index, element in enumerate(response_data.items()):
                        key, value = element
                        print(f"{index}. Host: {key}, Value: {value}\n")
            elif (status_code == '404'):
                response_length = int(response_header[2])
                response_data = self.__client_socket.recv(response_length).decode(FORMAT)
                print(response_data)
            elif (status_code == '204'):
                response_length = int(response_header[2])
                response_data = self.__client_socket.recv(response_length).decode(FORMAT)
                print(response_data)
    
    def __init_host(self):
        self.__file_host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__file_host_socket.bind(('', 0))
        self.FILE_PORT = self.__file_host_socket.getsockname()[1]
        self.__file_host_socket.listen(5)
        while self.__upload_online:
            conn, addr = self.__file_host_socket.accept() # conn : connection between file host and client
            thread = threading.Thread(target=self.__handle_request, args=(conn, addr))
            thread.start()
        self.__file_host_socket.close()
    
    def __handle_request(self, conn, addr):
        print(f"[REQUEST] A CLIENT HAS SENT A REQUEST")
        connected = True
        while connected:
            header = conn.recv(HEADER).decode(FORMAT)
            if header:
                header = header.split() 
                req_type = header[0]
                if (req_type == "DOWNLOAD"):
                    lname_length = int(header[1])
                    lname = conn.recv(lname_length).decode(FORMAT)
                    self.__handle_send_file(conn, lname)

    def __handle_send_file(self, conn, lname):
        try:
            filesize = os.path.getsize(f'files/{lname}')
            header = f"FILE {filesize}"
            header = header.encode(FORMAT)
            header += b' ' * (HEADER - len(header))
            print('Sending...')
            conn.sendall(header)
            path = 'files'
            path += f'/{lname}'
            with open(path, 'rb') as file:
                while True:
                    to_send = file.read(1024)
                    if not to_send:
                        break
                    conn.sendall(to_send)
                conn.sendall(b'</EOF>')
                
            print("File sent complete!")
        
        except FileNotFoundError:
            raise Exception(f'File not found: {lname}')
        except Exception:
            raise Exception('Uploading Failed')
    
    def send_download_request(self, lname, host_addr, host_port, fname):
        self.file_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_client_socket.connect((host_addr, host_port))
        lname_data = lname.encode(FORMAT)
        header = 'DOWNLOAD'
        header += f' {len(lname)}'
        header = header.encode(FORMAT)
        header += b' ' * (HEADER - len(header))
        self.file_client_socket.sendall(header + lname_data)
        self.__handle_write_file(self.file_client_socket, fname)
    
    def __handle_write_file(self, conn, fname):
        header = conn.recv(HEADER).decode(FORMAT)
        header = header.split()
        if header[0] == "FILE":
            filesize = int(header[1])
            print("I received the file!!")
            folder = "download"
            if not os.path.exists(folder):
                os.makedirs(folder)
            path = f"download/{fname}"
            file_bytes = b''
            try:
                with open(path, 'wb') as file:
                    done = False
                    while not done:
                        if file_bytes[-6:] == b'</EOF>':
                            done = True  # End of file
                        else:
                            chunk = conn.recv(1024)  # Receive 1 KB chunks
                            file_bytes += chunk
                    file.write(file_bytes[:-6])
                    file.close()
                
            except Exception:
                print("Downloading Failed")
                raise Exception('Downloading Failed')
            print('Downloading Completed.')
            
            
    
        

# client = Client()
# client.start()

# while client.is_connected:
#     action = input("Enter action (publish/fetch/disconnect): ").lower()

#     if action == "publish":
#         lname = input("Enter local name: ")
#         fname = input("Enter file name: ")
#         client.publish(lname, fname)

#     elif action == "fetch":
#         fname = input("Enter file name to fetch: ")
#         client.fetch(fname)

#     elif action == "disconnect":
#         client.stop()
#         break

#     else:
#         print("Invalid action. Please enter 'publish', 'fetch', or 'disconnect'.")