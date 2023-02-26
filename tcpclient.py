import  socket
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

        self.client.close()

    def create(self, recvFromServer):

        fdata = self.splitdata("$", recvFromServer)
        print("first data is ", fdata)
        self.client.send(fdata)
        recwrongdata = self.client.recv(4096).decode("utf-8")
        print("wrong data from server is ", recwrongdata)
        print("receivefromserver ", recvFromServer)
        print("recwrongdata", recwrongdata)

        if recvFromServer == recwrongdata:

            self.create(recwrongdata)


    def splitdata(self, sign, recvFromServer):
        splitdata = recvFromServer.split(sign)
        list_l = []
        for data in splitdata:
            d = input(data)
            list_l.append(d)
        data = sign.join(map(str, list_l))
        bytedata = bytes(data, "utf-8")
        return bytedata



    def main(self):
        while True:
            obj = delivery()
            sms = obj.option()
            myclient = Client(sms)
            myclient.runClient()





if __name__=="__main__":


        tcpClient = Client("Hello server")
        tcpClient.main()
