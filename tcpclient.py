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



        if "$" in recvFromServer:
            self.create(recvFromServer)

        elif "*" in recvFromServer:
            self.login(recvFromServer)

        elif "burger" in recvFromServer:
            self.showmenu(recvFromServer)

        else:
            print(recvFromServer)

        self.client.close()

    def showmenu(self, recvFromServer):
        obj = delivery()
        print(">>>>>>>>>>>>This is our menu<<<<<<<<<<<<\n", recvFromServer)
        data = "Done"
        self.client.send(data.encode())
        self.chooseoption()



    def create(self, recvFromServer):
        obj = delivery()
        fdata = obj.splitdata("$", recvFromServer)
        self.client.send(fdata)
        recwrongdata = self.client.recv(4096).decode("utf-8")
        print("return data is", recwrongdata)

        if recvFromServer == recwrongdata:
            self.create(recwrongdata)
        else:
            self.login(recwrongdata)

    def login(self, recvFromServer):
        obj = delivery()
        fdata = obj.splitdata("*", recvFromServer)
        self.client.send(fdata.encode())
        wrongdata = self.client.recv(4096).decode("utf-8")

        if recvFromServer == wrongdata:
            self.login(wrongdata)
        else:
            print("receive from server data", wrongdata)

    def chooseoption(self):
        recvFromServer = self.client.recv(4096).decode("utf-8")
        data = input(recvFromServer)
        self.client.send(data.encode())
        recv = self.client.recv(4096).decode("utf-8")
        if "food" in recv:
            self.choose_order(recv)

        elif "cancel" in recv:
            self.cancelitem(recv)

        elif "amount" in recv:
            paymethod = input(recv)
            self.client.send(paymethod.encode())

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
