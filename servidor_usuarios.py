# servidor_usuarios.py (modelo P2P)

import sys
import socket
import select
import pickle
import signal

# Creacion del socket TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def error():
    sock.close()
    sys.exit(-1)

def signal_handler(signal, frame):
    sock.close()
    sys.exit(0)

def main():
    # CONTROL DE ARGUMENTOS
    if len(sys.argv) != 2:
        print("ERROR: Numero de argumentos incorrecto.")
	print("Uso: python servidor_usuarios.py [Port_server]")
        error()
    portServer = int(sys.argv[1])
    addr = ('', portServer)
    print("Iniciando server %s --> puerto: %s" %addr)
    
    # Enlace del socket y puerto
    sock.bind(addr)
    # Escucha del socket (Hasta 10 conex)
    sock.listen(10)
    print("Socket enlazado correctamente\n")
    listaSocks = []
    listaSocks.append(sock)
    datos = []

    print("##### LOG SERVER P2P #####")
    while 1:
        signal.signal(signal.SIGINT, signal_handler)
        ready_to_read,ready_to_write,in_error = select.select(listaSocks,[],[],0)
        
        for socket in ready_to_read:
            if socket == sock:
                sockfd, address = sock.accept()
                portCliente = sockfd.recv(4096)
                listaSocks.append(sockfd)
                lista = [address[0], int(portCliente)] 
                data = pickle.dumps(datos)
                sockfd.send(data)
                datos = datos + lista
                print("CLIENTE (IP: %s PORT: %s) CONECTADO" %address)
                print("Lista de peers: %s" %datos)
    error()


if __name__ == "__main__":
	main()
