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
        print(f'Back received from server: {recvFromServer}')

        if "$" in recvFromServer:
            self.create(recvFromServer)

        elif "*" in recvFromServer:
            self.login(recvFromServer)

        self.client.close()

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
        self.client.send(fdata)
        wrongdata = self.client.recv(4096).decode("utf-8")

        if recvFromServer == wrongdata:
            self.login(wrongdata)


if __name__ == "__main__":
    tcpClient = Client("Hello server")
    obj = delivery()
    sms = obj.option()
    myclient = Client(sms)
    myclient.runClient()
