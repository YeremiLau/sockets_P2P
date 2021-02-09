# peer.py (modelo P2P)

import sys
import socket
import select
import pickle
import string
import signal

# socket para el server
sockserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# socket para aceptar conexiones
sockpeers = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def error():
    sockpeers.close()
    sockserver.close() # cierro socket del server
    sys.exit(-1)

def signal_handler(signal, frame):
    sockpeers.close()
    sockserver.close() # cierro socket del server
    sys.exit(0)

def main():
    if len(sys.argv) != 4:
    	print("ERROR: Numero de argumentos incorrecto.\n")
	print("Uso: python peer.py [IP_server] [Port_server] [Port_peer]\n")
    	error()
    IPserver = sys.argv[1]
    portServer = int(sys.argv[2])
    portCliente = int(sys.argv[3])
    
    # Asociacion del socket para los peers
    sockpeers.bind(('', portCliente))
    # Cola de escucha hasta 10 conex
    sockpeers.listen(10)
    print('Socket enlazado correctamente')

    # Asociacion y conex del socket para el server
    sockserver.connect((IPserver,portServer))
    sockserver.send(str(portCliente))
    dato = sockserver.recv(4096)

    lista = pickle.loads(dato) # restaurar datos pickle de la lista
    peers = len(lista)/2
    print("Numero de peers: %s" %peers)

    i = 0
    j = 0

    lista_peers = []
    lista_socket = [sys.stdin]  # aniadimos la entrada estandar
        
    print("Introduce un nick: ")
    nick = sys.stdin.readline()
    
    sys.stdout.write('> ' )
    sys.stdout.flush()
    while i<peers: # hacemos connect con los peers que nos manda el server
        lista_peers.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        lista_peers[i].connect((lista[j], lista[j+1])) # recibimos addr j y puerto cliente j+1
        i=i+1
    	j=j+2
        
    lista_socket.append(sockpeers)
    lista_socket = lista_socket + lista_peers # aniadimos la lista de peers

    while 1:
        signal.signal(signal.SIGINT, signal_handler)
	ready_to_read,ready_to_write,in_error = select.select(lista_socket,[],[])
	for sock in ready_to_read:  # si listo para leer
	    if sock == sockpeers:					
		sockfd, addr = sockpeers.accept()   # aceptamos la peticion
		lista_socket.append(sockfd)
			
	    elif sock == sys.stdin :    # si escribimos
	        mensaje = sys.stdin.readline()	# guarda el mensaje
	    	if mensaje == "exit\n":     # si el usuario teclea para salir
		    del lista_socket[0]     # delete peer de la lista
		    for k in lista_socket:
                        k.close()    # elimino las conexiones de los peers
                    error()
				
		for peersock in lista_socket: 	# enviamos al resto de usuarios
                    if peersock != sockpeers and peersock != sys.stdin: # excepto a nosotros
			try:
                            peersock.send("\r"+nick+": "+mensaje)
			except:	    # si falla se elimina
			    peersock.close()
			    lista_socket.remove(peersock)

		sys.stdout.write('> ' )
	        sys.stdout.flush()
								
	    # recibimos mensajes de otros usuarios
	    else:
	        mensaje = sock.recv(4096)
                sys.stdout.write(mensaje)    # Se escribe el mensaje en la pantalla
                # Se escribe el dato y ahora puedo volver a escribir
		sys.stdout.write('> ' )    
		sys.stdout.flush()  
    error()

if __name__ == "__main__":
	main()
