import socket
import threading
from pymongo import MongoClient
from deliverypj import delivery


class TCP_server:
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

            elif request == '3':
                self.sign_inaccount(sock)

            elif request == '4':
                return_data = "exit"
                sock.send(return_data.encode())
                pass

            else:
                return_data = "Invalid option"
                sock.send(return_data.encode())

    def show(self, sock):

        obj = delivery()
        return_data = obj.showMenu()
        sock.send(return_data.encode())

    def create(self, sock):

        obj = delivery()
        return_data = obj.create_account()
        sock.send(return_data.encode())
        recvdata = sock.recv(4096).decode("utf-8")
        splitdata = recvdata.split("$")

        phonestringcheck = obj.stringcheck(splitdata[1])

        if phonestringcheck == 'f':
            print("String error!")
            self.create(sock)
        else:
            phoneincreate = obj.create_phone(splitdata[1])

            if phoneincreate == 'f':
                print("phone is out of range!")
                self.create(sock)
            else:
                mongophone = obj.phoneinmongo(splitdata[1])
                if mongophone == 1:
                    print("phone is already exist in mongodb!")
                    self.create(sock)
                else:
                    confirmdata = obj.confirmpassword(recvdata)
                    if confirmdata == 1:
                        print("correct!!!!!")
                        obj.store_account(recvdata)
                        print("Storage success")
                        self.sign_inaccount(sock)

                    else:
                        print("Incorrect password")
                        self.create(sock)

    def sign_inaccount(self, sock):
        obj = delivery()
        return_data = obj.sign_in()
        sock.send(return_data.encode())

        recvdata = sock.recv(4098).decode("utf-8")
        print("receive sign_in data :", recvdata)
        splitdata = recvdata.split('*')
        print(splitdata)
        print(splitdata[0])
        checkphone = obj.checking_phone(splitdata[0])
        print(checkphone)
        if checkphone == 0:
            print("wrong phone number")
            self.sign_inaccount(sock)
        else:
            checkpass = obj.checking_password(splitdata[0], splitdata[1])
            if checkpass == 'f':
                print("wrong password")
                self.sign_inaccount(sock)


if __name__ == '__main__':
    Myserver = TCP_server()
    Myserver.main()
