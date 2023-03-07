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
    obj = delivery()

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
            self.pageoption(sock)

    def show(self, sock):
        return_data = self.obj.showMenu()
        sock.send(return_data.encode())
        recvdata = sock.recv(4096).decode("utf-8")
        if recvdata == "Done":
            self.orderr(sock)

    def create(self, sock):
        return_data = self.obj.create_account()
        sock.send(return_data.encode())
        recvdata = sock.recv(4096).decode("utf-8")
        splitdata = recvdata.split("$")

        phonestringcheck = self.obj.stringcheck(splitdata[1])

        if phonestringcheck == 'f':
            print("String error!")
            self.create(sock)
        else:
            phoneincreate = self.obj.create_phone(splitdata[1])

            if phoneincreate == 'f':
                print("phone is out of range!")
                self.create(sock)
            else:
                mongophone = self.obj.phoneinmongo(splitdata[1])
                if mongophone == 1:
                    print("phone is already exist in mongodb!")
                    self.create(sock)
                else:
                    confirmdata = self.obj.confirmpassword(recvdata)
                    if confirmdata == 1:
                        print("correct!!!!!")
                        self.obj.store_account(recvdata)
                        print("Storage success")
                        self.pageoption(sock)

                    else:
                        print("Incorrect password")
                        self.create(sock)

    def sign_inaccount(self, sock):
        global phone_index
        phone_index = ''
        return_data = self.obj.sign_in()
        sock.send(return_data.encode())

        recv_data = sock.recv(4098).decode("utf-8")
        print("receive sign_in data :", recv_data)
        splitdata = recv_data.split('*')

        phone = splitdata[0]

        check_phone = self.obj.checking_phone(phone)
        print(check_phone)

        if check_phone == 0:
            print("wrong phone number")
            self.sign_inaccount(sock)
        else:
            checkpass = self.obj.checking_password(phone, splitdata[1])
            if checkpass == 'f':
                print("wrong password")
                self.sign_inaccount(sock)
            else:
                phone_index = phone
                self.show(sock)

    def orderr(self, sock):
        global count
        strr = "\nPress 1 to choose item\nPress 2 to cancel item\nPress 3 to order\nPress 4 to exit from order"
        sock.send(strr.encode())
        recvdata = sock.recv(4098).decode("utf-8")
        self.option(sock, recvdata)

    def option(self, sock, recvdata):
        if recvdata == '1':
            ord = "\nPress 1 for food item\nPress 2 for drink item"
            sock.send(ord.encode())

            orddata = sock.recv(4098).decode("utf-8")

            if orddata == '1':
                self.choosefooddrink(sock, "food")

            elif orddata == '2':
                self.choosefooddrink(sock, "drink")

            else:
                op = "\nInvalid option"
                sock.send(op.encode())
                self.orderr(sock)

        elif recvdata == '2':
            self.cancel(sock)

        elif recvdata == '3':
            self.order(sock)

        elif recvdata == '4':
            self.pageoption(sock)

        else:
            op = "\nInvalid option"
            sock.send(op.encode())
            self.orderr(sock)

    def pageoption(self, sock):
        op = "\nPress 1 to show menu\nPress 2 to create account\nPress 3 to sign in\nPress 4 to exit\nEnter option"
        sock.send(op.encode())
        recive = sock.recv(1024).decode("utf-8")
        self.menu_option(sock, recive)

    def listpop(self):
        for item in range(len(list_l)):
            list_l.pop(item)

    def order(self, sock):
        length = len(list_l)

        if length > 0:
            totalfee = 0

            for item in range(len(list_l)):
                totalfee += list_l[item]["price"] * list_l[item]["numberofitem"]
            countstring = str(totalfee)

            phone = "\n\nEnter your phone number"
            amount = "\nTotal fee is :: "
            addstring = amount + countstring + phone

            sock.send(addstring.encode())
            phone_data = sock.recv(4098).decode("utf-8")

            check_ph = self.obj.stringcheck(phone_data)

            if check_ph == 't':
                check_num = self.obj.create_phone(phone_data)
                if check_num == "t":
                    loca = "\nEnter your location"
                    sock.send(loca.encode())
                    location = sock.recv(1024).decode("utf-8")

                    deli_amount = 3000
                    de = "Delivery fee is 3000\n"
                    fee = totalfee + deli_amount
                    fee_str = str(fee)
                    paymethod = "\n>>>>Choose your pay method<<<<\nPress 1 for KBZpay\nPress 2 for WavePay"
                    am = "After adding delivery fee, Total fee is ::"
                    addingstr = de + am + fee_str + paymethod

                    sock.send(addingstr.encode())
                    rec_input = sock.recv(1024).decode("utf-8")
                    if rec_input == '1' or rec_input == '2':
                        order = "Order successful\nPlease wait for 15 mins......"
                        sock.send(order.encode())

                        self.listpop()
                        self.orderr(sock)

                    else:
                        order = "\nOrder Unsuccessful\n Please try to reorder....."
                        sock.send(order.encode())

                        self.listpop()
                        self.orderr(sock)

                else:
                    pp = "\nIncorrect phone number"
                    sock.send(pp.encode())
                    self.order(sock)

            else:
                pp = "\nIncorrect phone number"
                sock.send(pp.encode())
                self.order(sock)
        else:
            pri = "\nYou haven't ordered any item yet!"
            sock.send(pri.encode())
            self.orderr(sock)

    def cancel(self, sock):
        p = "\nPress 1 for cancel item\nPress 2 for change number of item\nPress 3 for complete order cancel"
        sock.send(p.encode())

        can_option = sock.recv(1024).decode("utf-8")
        if can_option == '1':
            self.cancelitem(sock)

        elif can_option == '2':
            self.changenoofitem(sock)

        elif can_option == '3':
            self.completeCancel(sock)

        else:
            op = "\nInvalid option"
            sock.send(op.encode())
            self.cancel(sock)

    def completeCancel(self, sock):
        length = len(list_l)
        if length > 0:
            pr = "\n>>>>Your order history<<<<\n"
            ltos = '\n'.join(map(str, list_l))
            p = "\nPress 1 to confirm\n Press any key to order"
            string = pr + ltos + p
            sock.send(string.encode())
            inpput = sock.recv(1024).decode("utf-8")

            if inpput == '1':
                for item in range(len(list_l)):
                    list_l.pop(item)
                pr = "\n>>>>Your order history<<<<\n"
                ltos = '\n'.join(map(str, list_l))
                stringadd = pr + ltos
                sock.send(stringadd.encode())
                self.orderr(sock)

            else:
                b = "\n<<<...Back"
                sock.send(b.encode())
                self.orderr(sock)
        else:
            pri = "\nYou haven't ordered any item yet!"
            sock.send(pri.encode())
            self.orderr(sock)

    def changenoofitem(self, sock):
        length = len(list_l)
        count = 0
        if length > 0:
            name = "\n>>>>>>For change number of item<<<<<"
            pr = "\n>>>>Your order history<<<<\n"
            p = "\nEnter item name"
            ltos = '\n'.join(map(str, list_l))
            string = pr + ltos + name + p

            sock.send(string.encode())

            rec_name = sock.recv(1024).decode("utf-8")

            for item in range(len(list_l)):
                if list_l[item]["item"] == rec_name:
                    count = +1
                    break

            if count > 0:
                num = "\nEnter number of item to change ::"
                sock.send(num.encode())
                num_item = sock.recv(1024).decode("utf-8")

                noofitem = int(num_item)
                print(list_l)

                for item in range(len(list_l)):

                    if list_l[item]["item"] == rec_name:
                        list_l[item]["numberofitem"] = noofitem
                        print(list_l[item]["numberofitem"])
                        break
                print(list_l)
                self.orderr(sock)
            else:
                op = "\nNot found order like that"
                sock.send(op.encode())
                self.cancel(sock)

        else:
            pri = "\nYou haven't ordered any item yet!"
            sock.send(pri.encode())
            self.orderr(sock)

    def cancelitem(self, sock):
        length = len(list_l)
        if length > 0:
            count = 0
            pr = "\n>>>>Your order history<<<<\n"
            ltos = '\n'.join(map(str, list_l))
            p = "\nEnter cancel item name"
            twos = pr + ltos + p
            sock.send(twos.encode())
            rr = sock.recv(4096).decode("utf-8")

            for item in range(len(list_l)):
                if list_l[item]["item"] == rr:
                    list_l.pop(item)
                    count = +1
                    break
            if count > 0:
                can = "\nitem cancel success\n >>>>Now your order is<<<<\n"
                ltost = '\n'.join(map(str, list_l))
                senddata = can + ltost
                sock.send(senddata.encode())
                self.orderr(sock)
            else:
                op = "\nNot found order like that"
                sock.send(op.encode())
                self.cancel(sock)

        else:
            pri = "\nYou haven't ordered any item yet!"
            sock.send(pri.encode())
            self.orderr(sock)

    def choosefooddrink(self, sock, fd):
        global pricee
        list1 = []
        food = self.collection.find().distinct(fd)
        for item in food:
            for i in item:
                list1.append(i)
        st = '\n'.join(map(str, list1))
        f = "\n>>>>> item <<<<<\n"

        cfood = "\n\nPlease choose item"
        senddata = f + st + cfood
        sock.send(senddata.encode())
        rec = sock.recv(4098).decode("utf-8")
        check =self.obj.checkmenu(rec, fd)
        if check == "f":
            pr = "\nInvalid order item"
            sock.send(pr.encode())
            self.orderr(sock)

        else:

            sock.send(check.encode())
            receiver = sock.recv(4098).decode("utf-8")

            cshop = self.obj.checkshopname(rec, receiver, fd)
            if cshop == 't':
                send = "\nEnter number of item"
                sock.send(send.encode())
                numberdata = sock.recv(4096).decode("utf-8")
                try:
                    numitem = int(numberdata)
                    if numitem > 0:
                        op = "Done"
                        sock.send(op.encode())

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
                    else:
                        p = "\nInvalid , number of item must greater than 0"
                        sock.send(p.encode())
                        self.orderr(sock)

                except Exception as error:
                    p = "Invalid string ..... Enter 1,2,3,..."
                    sock.send(p.encode())
                    self.orderr(sock)

            else:
                op = "Invalid shop name"
                sock.send(op.encode())
                self.orderr(sock)


if __name__ == '__main__':
    Myserver = TCP_server()
    Myserver.main()
