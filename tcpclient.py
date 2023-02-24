import  socket
from deliverypj import delivery

class Client:
    def __init__(self, client_sms):
        self.target_host = 'localhost'
        self.target_port = 9999
        self.ClientMessage = bytes(client_sms, 'utf-8')

    def runClient(self):
        client = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
        client.connect((self.target_host, self.target_port))

        client.send(self.ClientMessage)

        recvFromServer = client.recv(4096).decode("utf-8")
        print(f'Back received from server: {recvFromServer}')
        client.close()



    def main(self):
        while True:
            obj = delivery()
            sms = obj.option()
            myclient = Client(sms)
            myclient.runClient()





if __name__=="__main__":


        tcpClient = Client("Hello server")
        tcpClient.main()
