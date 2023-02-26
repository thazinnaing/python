import socket
import threading
from pymongo import MongoClient
from deliverypj import delivery


class TCP_server():
    connection = MongoClient("localhost", 27017)
    database = connection["DeliveryDB"]
    collection = database["usercollection"]

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
            print("receive data from client: ", request)


            if request == '1':
                self.show(sock)

            elif request == '2':
                self.create(sock)


    def show(self, sock):

        obj = delivery()
        return_data = obj.showMenu()
        sock.send(return_data.encode())


    def create(self, sock):

        obj = delivery()
        return_data = obj.create_account()
        sock.send(return_data.encode())
        recvdata = sock.recv(4096).decode("utf-8")
        print("receive string: ", recvdata)

        confirmdata = obj.confirmpassword(recvdata)
        if confirmdata == 1:
            obj.store_account(recvdata)
        else:
            print("Incorrect password")
            self.create(sock)


if __name__ == '__main__':
    Myserver = TCP_server()
    Myserver.main()
