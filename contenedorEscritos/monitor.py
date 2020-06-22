
"""
"""

import socket
import multiprocessing
import subprocess
import datetime
import os
import requests

CHAT_ID = os.environ.get('BOT_CHATID')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

def mandar_mensaje(mensaje):        
    send_text = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&parse_mode=Markdown&text=%s' % (BOT_TOKEN, CHAT_ID, mensaje)
    response = requests.get(send_text)
    return response.json()

class Monitor():
    def __init__(self, port=9030):        
        self.port = port
        self.lock = multiprocessing.Lock()
        
        
    def run(self):
        """
        crear socket de servicio
        """
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mySocket.bind(('', int(self.port)))  # binds to any available interface
        print('listenning on port: %s' % self.port)
        mySocket.listen(5)
        while True:
            conn, addr = mySocket.accept()
            attendThread = WorkThread(conn, addr) # se crea un hilo de atención por cliente
            attendThread.start()

            
class WorkThread(multiprocessing.Process):  # it is actually a subprocess
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        multiprocessing.Process.__init__(self)

    def run(self):
        data = ''
        while not data.endswith('$$$'): # read message
            chunck = self.conn.recv(1024).decode()
            data += chunck
            if not chunck: #finished
                break
        if not data:
            raise RuntimeError("No se transmitieron datos")
        data = data[:-3] # quitar $$$
        mensaje = '%s: %s' % (datetime.datetime.now(), data)
        mandar_mensaje(mensaje)
        print(mensaje)

if __name__ == '__main__':
    dem = Monitor()
    dem.run()

