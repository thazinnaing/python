import socket
import threading
from pymongo import MongoClient
from deliverypj import delivery


class TCP_server():

    connection = MongoClient("localhost", 27017)
    database = connection["DeliveryDB"]
    collection = database["foodcollection"]

    def __init__(self):
        self.server_ip = 'localhost'
        self.server_port = 9999

    def main(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.server_ip, self.server_port))
        server.listen(1)
        print(f'[*] Listening on {self.server_ip}:{self.server_port}')
        while True:
            client, address = server.accept()
            print(f'[*] Accepted connection from {address[0]}:{address[1]}')
            client_handler = threading.Thread(target=self.handle_client, args=(client,))
            client_handler.start()

    def handle_client(self, client_socket):
        with client_socket as sock:
            request = sock.recv(1024).decode("utf-8")
            inidata = int(request)
            obj = delivery()
            if inidata == 1:

                return_data = obj.showMenu()
                sock.send(return_data.encode())

            if inidata == 2:
                return_data = obj.create_account()
                sock.send(return_data.encode())




if __name__ == '__main__':
    Myserver = TCP_server()
    Myserver.main()
