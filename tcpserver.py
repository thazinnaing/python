import socket
import threading
from pymongo import MongoClient
from deliverypj import delivery


class TCP_server:
    connection = MongoClient("localhost", 27017)
    database = connection["DeliveryDB"]
    collection = database["foodcollection"]
    collection1 = database["usercollection"]
    global list_l
    list_l = []



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
            self.menu_option(sock, request)

    def menu_option(self, sock, request):
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
        recvdata = sock.recv(4096).decode("utf-8")
        if recvdata == "Done":
            self.orderr(sock)


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
                        self.pageoption(sock)

                    else:
                        print("Incorrect password")
                        self.create(sock)

    def sign_inaccount(self, sock):
        global phone_index
        phone_index = ''
        obj = delivery()
        return_data = obj.sign_in()
        sock.send(return_data.encode())

        recv_data = sock.recv(4098).decode("utf-8")
        print("receive sign_in data :", recv_data)
        splitdata = recv_data.split('*')

        phone = splitdata[0]

        check_phone = obj.checking_phone(phone)
        print(check_phone)

        if check_phone == 0:
            print("wrong phone number")
            self.sign_inaccount(sock)
        else:
            checkpass = obj.checking_password(phone, splitdata[1])
            if checkpass == 'f':
                print("wrong password")
                self.sign_inaccount(sock)
            else:
                phone_index = phone
                self.show(sock)

    def orderr(self, sock):
        global count
        strr = "Press 1 to choose item\nPress 2 to cancel item\nPress 3 to order\nPress 4 to exit"
        sock.send(strr.encode())
        recvdata = sock.recv(4098).decode("utf-8")
        self.option(sock, recvdata)


    def option(self, sock, recvdata):
        if recvdata == '1':
            ord = "Press 1 for food item\nPress 2 for drink item"
            sock.send(ord.encode())

            orddata = sock.recv(4098).decode("utf-8")

            if orddata == '1':
                self.choosefooddrink(sock, "food")

            else:
                self.choosefooddrink(sock, "drink")

        elif recvdata == '2':
            self.cancel(sock)

        elif recvdata == '3':
            self.order(sock)

        elif recvdata == '4':
            self.pageoption(sock)

    def pageoption(self, sock):
        op = "Press 1 to show menu\nPress 2 to create account\nPress 3 to sign in\nPress 4 to exit\nEnter option"
        sock.send(op.encode())
        recive = sock.recv(1024).decode("utf-8")
        self.menu_option(sock, recive)


    def listpop(self):
        for item in range(len(list_l)):
            list_l.pop(item)

    def order(self, sock):
        count = 0
        amount = "Total fee is :: "

        for item in range(len(list_l)):
            count += list_l[item]["price"] * list_l[item]["numberofitem"]
        countstring = str(count)
        location = "\nEnter your location"
        addstring = amount + countstring + location
        sock.send(addstring.encode())
        location_data = sock.recv(4098).decode("utf-8")
        deli_amount = 3000
        de = "Delivery fee is 3000\n"
        fee = count + deli_amount
        fee_str = str(fee)
        paymethod = "\n>>>>Choose your pay method<<<<\nPress 1 for KBZpay\nPress 2 for WavePay"
        am = "After adding delivery fee, Total fee is ::"
        addingstr = de + am + fee_str + paymethod
        sock.send(addingstr.encode())
        rec_input = sock.recv(1024).decode("utf-8")
        if rec_input == '1' or rec_input == '2':
            order = "Order successful\nPlease wait for 15 mins......"
            sock.send(order.encode())
            user_index = self.collection1.find_one({"phone number": phone_index})
            print(user_index)

            self.listpop()
            self.orderr(sock)


        else:
            order = "Order Unsuccessful\n Please try to reorder....."
            sock.send(order.encode())

            self.listpop()
            self.orderr(sock)

    def cancel(self, sock):
        pr = ">>>>Your order history<<<<\n"
        ltos = '\n'.join(map(str, list_l))
        p = "\nEnter cancel item name"
        twos = pr + ltos + p
        sock.send(twos.encode())
        rr = sock.recv(4096).decode("utf-8")
        for item in range(len(list_l)):
            if list_l[item]["item"] == rr:
                list_l.pop(item)
                break

        can = "item cancel success\n >>>>Now your order is<<<<\n"
        ltost = '\n'.join(map(str, list_l))
        senddata = can + ltost
        sock.send(senddata.encode())
        self.orderr(sock)

    def choosefooddrink(self, sock, fd):
        global pricee
        obj = delivery()
        fooddata = self.collection.find().distinct(fd)
        food = '\n'.join((map(str, fooddata)))
        cfood = "\nPlease choose item"
        senddata = food + cfood
        sock.send(senddata.encode())
        rec = sock.recv(4098).decode("utf-8")
        check = obj.checkmenu(rec, fd)
        if check == "f":
            pr = "Invalid order item"
            sock.send(pr.encode())
            self.orderr(sock)

        else:

            sock.send(check.encode())
            receiver = sock.recv(4098).decode("utf-8")
            send = "Enter number of item"
            sock.send(send.encode())
            numberdata = sock.recv(4096).decode("utf-8")
            numitem = int(numberdata)
            fooddata = self.collection.find_one({"shop name": receiver})
            f = fooddata.get(fd)
            for i in f:
                if i == rec:
                    p = f.get(i)
                    pricee = int(p)

            appenddata = {"shop name": receiver, "item": rec, "price": pricee, "numberofitem": numitem}
            list_l.append(appenddata)
            print(list_l)

            self.orderr(sock)


if __name__ == '__main__':
    Myserver = TCP_server()
    Myserver.main()
