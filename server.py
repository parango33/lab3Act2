import socket
import sys
import os 
import hashlib
import time
from datetime import datetime
# Crear socket tcp/ip
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Crear socket UDP
sock_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


num_conexiones = int(input('Ingrese la cantidad de conexiones que quiere atender'))

while (num_conexiones>25 and num_conexiones <= 0):
    num_conexiones = int(input('Ingrese un número válido de conexiones'))


#Creación del Log
#log = open('./'+datetime.today().strftime('%Y-%m-%d-%H:%M:%S')+".txt", "w")

#conectar socket_UDP al puerto
server_address_udp = ('localhost', 3000)
sock_UDP.bind(server_address_udp)
print("UDP server up and listening")

# conectar socket al puerto
server_address_tcp = ('localhost', 8888)
print(sys.stderr, 'starting up on %s port %s' % server_address_tcp)
sock.bind(server_address_tcp)



#archivo a transmitir
filename = input('Ingrese el nombre del archivo a enviar')
while filename not in ['100mb.txt','250mb.txt']:
    filename = input('Ingrese un nombre correcto del archivo a enviar')

tamano_archivo = os.path.getsize(filename)

log = open("./logs/servidor-"+' '+datetime.today().strftime('%Y-%m-%d-%H-%M-%S')+"log.txt", "w")
log.write('Fecha del archivo: '+datetime.today().strftime('%Y-%m-%d-%H-%M-%S')+'\n')  
log.write('El nombre del archivo es: '+filename+'\n')  

archivo = open(filename, 'rb')
buf = archivo.read(1024)
md5 = hashlib.md5() 

while(buf):
    #Saca el hash del archivo
    md5.update(buf)
    buf = archivo.read(1024)

  
# Listen for incoming connections
sock.listen(25)

for i in range(num_conexiones):
    
    #Leemos la primera linea del archivo 
    f = open(filename,'rb')
    l = f.read(1024)
    
    # Espera por una conexion
    print (sys.stderr, 'waiting for a connection')
    connection, client_address = sock.accept()
    start = time.time()
    log.write('Direccion del cliente: '+str(client_address)+'\n')  
    try:
        print (sys.stderr, 'connection from', client_address)
        
        data = connection.recv(32) 
            
        connection.sendall(b'ok')
        
        connection.recv(32)
        connection.sendall(bytes(filename, 'utf-8'))
        
        data = connection.recv(32)
        #server_address = ('localhost', 8888)
        print(data.decode('utf-8'))
        # Recibir datos y retransmitirlos
       
        if(data.decode('utf-8')== "listo"):
            
            connection.sendall(bytes(md5.hexdigest(), 'utf-8'))
            #Enviamos linea por linea el archivo
            recibido = connection.recv(32)
            if(recibido.decode('utf-8') == 'Hash recibido'):
                while (l):
                    print(l)
                    sock_UDP.sendto(l, server_address_udp)
                    l= f.read(1024)
            
                connection.send(l)
            #Enviamos el hashÑ
                #confirmacionArchivo = connection.recv(32)
                #print(confirmacionArchivo.decode('utf-8'))
                #if(confirmacionArchivo.decode('utf-8')== "Entrega del archivo exitosa"):
                print('Conexión terminada exitosamente')
                log.write('Entrega del archivo: se envio el archivo '+'\n')  
                end = time.time()
                #else:
                 #   print('Conexión terminada con error')
            
        log.write('Tiempo transferencia con cliente: '+str(end-start)+'\n')  
            
    finally:
        # cerrar coneccion
        connection.close()
