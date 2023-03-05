import socket
from deliverypj import delivery


class Client:
    def __init__(self, client_sms):
        self.target_host = 'localhost'
        self.target_port = 9999
        self.ClientMessage = bytes(client_sms, 'utf-8')

    def runClient(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.target_host, self.target_port))

        self.client.send(self.ClientMessage)

        recvFromServer = self.client.recv(4096).decode("utf-8")
        self.select_option(recvFromServer)

    def page_option(self, recv):

        in_rec = input(recv)
        self.client.send(in_rec.encode())
        recv_FromServer = self.client.recv(4096).decode("utf-8")
        self.select_option(recv_FromServer)

    def select_option(self, recvFromServer):

        if "$" in recvFromServer:
            self.create(recvFromServer)

        elif "*" in recvFromServer:
            self.login(recvFromServer)

        elif "burger" in recvFromServer:
            self.showmenu(recvFromServer)

        else:
            print(recvFromServer)

        self.client.close()

    def chooseoption(self):
        recvFromServer = self.client.recv(4096).decode("utf-8")
        data = input(recvFromServer)
        self.client.send(data.encode())
        recv = self.client.recv(4096).decode("utf-8")
        if "food" in recv:
            self.choose_order(recv)

        elif "cancel" in recv:
            self.cancelitem(recv)

        elif "location" in recv:
            self.order(recv)

        elif "show" in recv:
            self.page_option(recv)

    def showmenu(self, recvFromServer):
        print(">>>>>>>>>>>>This is our menu<<<<<<<<<<<<\n", recvFromServer)
        data = "Done"
        self.client.send(data.encode())
        self.chooseoption()



    def create(self, recvFromServer):
        obj = delivery()
        fdata = obj.splitdata("$", recvFromServer)
        self.client.send(fdata.encode())
        recwrongdata = self.client.recv(4096).decode("utf-8")
        print("return data is", recwrongdata)

        if recvFromServer == recwrongdata:
            self.create(recwrongdata)
        else:
            self.page_option(recwrongdata)

    def order(self, recv):
        paymethod = input(recv)
        self.client.send(paymethod.encode())
        fee_rec = self.client.recv(4096).decode("utf-8")
        in_fee = input(fee_rec)
        self.client.send(in_fee.encode())
        pay_rec = self.client.recv(4096).decode("utf-8")
        if "success" in pay_rec:
            print(pay_rec)
            self.chooseoption()
        else:
            print(pay_rec)
            self.chooseoption()

    def login(self, recvFromServer):
        obj = delivery()
        fdata = obj.splitdata("*", recvFromServer)
        print(fdata)
        self.client.send(fdata.encode())
        wrongdata = self.client.recv(4096).decode("utf-8")

        if recvFromServer == wrongdata:
            self.login(wrongdata)
        else:
            self.showmenu(wrongdata)

    def cancelitem(self, recv):
        canceli = input(recv)
        self.client.send(canceli.encode())
        rece = self.client.recv(4096).decode("utf-8")
        print(rece)
        self.chooseoption()

    def choose_order(self, recv):
        foodordrink = input(recv)
        self.client.send(foodordrink.encode())
        r = self.client.recv(4096).decode("utf-8")
        re = input(r)
        self.client.send(re.encode())
        rece = self.client.recv(4096).decode("utf-8")
        receive = input(rece)
        self.client.send(receive.encode())
        rr = self.client.recv(4096).decode("utf-8")
        toinput = input(rr)
        self.client.send(toinput.encode())
        self.chooseoption()


if __name__ == "__main__":
    tcpClient = Client("Hello server")
    obj = delivery()
    sms = obj.option()
    myclient = Client(sms)
    myclient.runClient()
