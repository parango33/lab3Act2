import socket
import sys
import hashlib
import os
import threading
from datetime import datetime
import time

num_clientes = int(input('Ingrese la cantidad de clientes que quiere crear'))
while (num_clientes>25 and num_clientes <= 0):
    num_clientes = int(input('Ingrese un número válido de clientes'))


#Creación del Log


class Ejecucion:    
    def __init__(self):
        self.lock = threading.Lock()
    def cliente_funct(self, nombre):
        self.lock.acquire()
        
        log = open("./logs/"+nombre+' '+datetime.today().strftime('%Y-%m-%d-%H-%M-%S')+"log.txt", "w")
        self.lock.release()
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Conectar socket al puerto donde se esta escuchando
        server_address = ('192.168.182.128', 8888)
        print(sys.stderr, 'connecting to %s port %s' % server_address)
        sock.connect(server_address)
        file = open("./archivosRecibidos/"+nombre+"-prueba-"+str(num_clientes)+".txt", "w")
       
        
        try:
            
            # Enviar datos
            message = b'Iniciar conexion...'
            print (sys.stderr, 'enviando "%s"' % message)
            sock.sendall(message)
        
            # buscar la respuesta

            confirmacion = sock.recv(32)
            print(confirmacion.decode('utf-8'))
            #hash a comparar
            md5 = hashlib.md5()
            if(confirmacion.decode('utf-8') == "ok"):
                sock.sendall(b'Cual es el nombre del archivo?')
                nA = sock.recv(32)
                nombreArchivo = nA.decode('utf-8') 
                log.write('El nombre del archivo es: '+nombreArchivo+'\n')
                
                sock.sendall(b'listo')
                self.lock.acquire()
                hash = sock.recv(32)
                print(hash.decode('utf-8'))
                sock.sendall(b'Hash recibido')
                self.lock.release()
                
                
                num_paquetes=0
                start = time.time()

                while (True):
                       
                    data = sock.recv(1024)
                    
                    if data:
                        try:
                            file.write(data.decode('utf-8') + os.linesep)
                            md5.update(data)
                            num_paquetes+=1
                            
                        except:
                            print("Error") 
                            sock.sendall(b'Hubo un error al recibir el archivo')
                            break
                        
                    else:
                        print (sys.stderr, 'Termino de leer el archivo')
                        sock.sendall(b'Archivo recibido')
                        break
                end = time.time()
                
                tamano = os.path.getsize("./archivosRecibidos/"+nombre+"-prueba-"+str(num_clientes)+".txt")
                
                file.close()
                log.write('El tamaño del archivo es: '+str(tamano/1000000)+' MB'+'\n')
                log.write('El nombre del cliente es: '+nombre+'\n')
               
               
                print("MD5: {0}".format(md5.hexdigest()))  
                  
                
                if(hash.decode('utf-8') == md5.hexdigest()):
                    print("Archivo leido correctamente")
                    log.write('Entrega del archivo exitosa'+'\n')
                else:
                    print("hubo un error al momento de leer el archivo")
                    log.write('Entrega del archivo no exitosa'+'\n')
                log.write('Tiempo de transferencia: '+str(end-start)+ ' segs'+'\n')    
                log.write('Cantidad de paquetes recibidos: '+str(num_paquetes)+'\n') 
                log.write('Valor total en bytes recibidos: '+str(tamano)+'\n')  
                
        finally:
            print (sys.stderr, 'Cerrar socket')
            sock.close()
            log.close()
            
            

def worker(c, nombre):
        c.cliente_funct(nombre)
        
hilo=Ejecucion()
for num_cliente in range(num_clientes):
    cliente = threading.Thread(name="Cliente%s" %(num_cliente+1),
                               target=worker,
                               args=(hilo,"Cliente%s" %(num_cliente+1))
                              )
    cliente.start()



