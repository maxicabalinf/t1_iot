import socket
""""
HOST = '0.0.0.0'  # Escucha en todas las interfaces disponibles
PORT = 1234       # Puerto en el que se escucha

# Crea un socket para IPv4 y conexión TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    print("El servidor está esperando conexiones en el puerto", PORT)

    while True:
        conn, addr = s.accept()  # Espera una conexión
        with conn:
            print('Conectado por', addr)
            data = conn.recv(1024)  # Recibe hasta 1024 bytes del cliente
            if data:
                print("Recibido: ", data.decode('utf-8'))
                respuesta = "tu mensaje es: " + data.decode('utf-8')
                # Envía la respuesta al cliente
                conn.sendall(respuesta.encode('utf-8'))
"""

## Consultar la tabla de configuración en la base de datos
## Crear 2 sockets, TCP Y UDP
## while infinito revisando la base de datos.(siempre comienza con TCP)
## Parsear los datos
## Guardarlos en la base de datos

## Si el largo del body es menor que de los headers, entonces se calcula
## la diferencia entre el largo indicado en los headers y lo que llegó.
 
 ## Se almacena la diferencia de timestamps entre que se guardó la conexión en la tabla Logs 
## y el servidor escribió los datos en la tabla Datos.

## Finalmente se reinicia el ciclo.