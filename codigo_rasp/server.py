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

import socket
import sys
import jsockets
from modelos import Configuration
from peewee import DoesNotExist


def get_cfg():
    """Extrae la configuración de la base de datos"""
    try:
        return Configuration.get()
    except DoesNotExist:
        return None


print(get_cfg())


def build_headers(id_msg, mac, transport_layer, id_protocol, length):
    """Retorna el header de un mensaje"""
    bytes_list = [
        id_msg.to_bytes(2),
        mac.to_bytes(6),
        transport_layer.to_bytes(1),
        id_protocol.to_bytes(1),
        length.to_bytes(2),
    ]

    header = b''.join(bytes_list)
    return header


# HOST = '0.0.0.0'  # Escucha en todas las interfaces disponibles
PORT = 1234       # Puerto en el que se escucha


def send_headers(sock):
    # Consulta BD para obtener configuración
    # Crea headers
    # Envía headers mediante el socket entregado
    pass


def parse_msg(pkt):
    """Deconstruye el paquete."""
    pass


# Espera un mensaje y protocolo de acuerdo  a lo que consulto en la BD.
# Parsear y guardar en la base de datos.
packet: bytes = None
parse_msg(packet)


res: bytes = None  # solicitud de conexión
sock: socket = None
send_headers(sock)


# Crear 2 sockets, TCP Y UDP
# while infinito revisando la base de datos.(siempre comienza con TCP)
# Parsear los datos
# Guardarlos en la base de datos

# Si el largo del body es menor que de los headers, entonces se calcula
# la diferencia entre el largo indicado en los headers y lo que llegó.

# Se almacena la diferencia de timestamps entre que se guardó la conexión en la tabla Logs
# y el servidor escribió los datos en la tabla Datos.

# Finalmente se reinicia el ciclo.


# Esperando un mensaje con TCP
if __name__ == '__main__':
    # Abre socket y queda a la escucha
    s = jsockets.socket_tcp_bind(PORT)
    if s is None:
        print('could not open socket')
        sys.exit(1)

    while True:
        # Acepta una conexión de ESP
        conn, addr = s.accept()
        print('Connected by', addr)
        header_ini = conn.recv(1024)
        # Consultar la tabla de configuración en la base de datos
        cfg = get_cfg()
        response_header = """"""
        conn.send(response_header)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.send(data)
        # conn.close()
        # print('Client disconnected')
