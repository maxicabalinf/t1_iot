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
import struct
import threading
from modelos import Configuration, TransportLayerValue, Datum, LogEntry, Header
from packet_parser import get_packet_size, unpack

HOST = '0.0.0.0'  # Escucha en todas las interfaces disponibles
PORT_CONEXION = 1233
PORT_TCP = 1234       # Puerto en el que se escucha
PORT_UDP = 1235

conexiones_udp = set()

def get_cfg():
    """Extrae la configuración de la base de datos"""
    cfg_row = Configuration.select(
        Configuration.body_protocol_id,
        Configuration.transport_layer_id
    ).dicts()
    if len(cfg_row) == 0:
        raise Exception('No hay configuración')
    return cfg_row[0]


def build_headers(id_msg: int, mac: str, transport_layer: int, id_protocol: int,
                  length: int):
    """Retorna el header de un mensaje"""
    assert len(mac) == 12
    bytes_list = [
        id_msg.to_bytes(2, byteorder='little'),
        bytearray.fromhex(mac),
        transport_layer.to_bytes(1, byteorder='little'),
        id_protocol.to_bytes(1, byteorder='little'),
        length.to_bytes(2, byteorder='little'),
    ]

    header = b''.join(bytes_list)
    return header


def send_headers(sock):
    # Consulta BD para obtener configuración
    # Crea headers
    # Envía headers mediante el socket entregado
    pass


def parse_msg(pkt):
    """Deconstruye el paquete."""

def recv_msg(client, len_data):
    data= bytearray()
    while len(data)<len_data:
        packet = client.recv(len_data-len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

# Crear 2 sockets, TCP Y UDP
# while infinito revisando la base de datos.(siempre comienza con TCP)
# Parsear los datos
# Guardarlos en la base de datos

# Si el largo del body es menor que de los headers, entonces se calcula
# la diferencia entre el largo indicado en los headers y lo que llegó.

# Se almacena la diferencia de timestamps entre que se guardó la conexión en la
# tabla Logs y el servidor escribió los datos en la tabla Datos.

# Finalmente se reinicia el ciclo.

def handle_client(client_sock, addr):
    # pkt = client_sock.recv(13000)
    # parse_msg(pkt)
    pass


def handle_tcp_client(tcp_client: socket.socket, config):
    """Ejecuta el procedimiento de almacenado para un cliente TCP."""
    protocol_id = config['body_protocol_id']
    pckt = recv_msg(tcp_client, get_packet_size(protocol_id))
    header: Header
    new_datum: Datum
    new_log_entry: LogEntry

    (header, new_datum, new_log_entry) = unpack(pckt)

    new_log_entry.transport_layer_id = header.transport_layer_id
    new_datum.save(force_insert=True)
    new_log_entry.save(force_insert=True)
    #Aviso que recibi la data
    respuesta = struct.pack('BB', config['transport_layer_id'], config['body_protocol_id'])
    tcp_client.sendall(respuesta)
    tcp_client.close()
def handle_udp_client(udp_client: socket.socket, config):
    """Ejecuta el procedimiento de almacenado para un cliente UDP."""
    protocol_id = config['body_protocol_id']
    trasport_layer = config["transport_layer_id"]
    
    conexiones_udp_close = set()
    
    #Espero datos hasta que cambie la TL o el Protocolo
    while trasport_layer == config["transport_layer_id"] and protocol_id == config['body_protocol_id']:
        try:
            pckt, address = udp_client.recvfrom(get_packet_size(protocol_id))
        except Exception as error:
            print("Error al recibir udp:", error)
            break
        #Solo recibo las que me hicieron el handshake inicial
        if address[0] not in conexiones_udp:
            continue
        conexiones_udp_close.add(address)
        print('recv')
        header: Header
        new_datum: Datum
        new_log_entry: LogEntry

        (header, new_datum, new_log_entry) = unpack(pckt)

        new_log_entry.transport_layer_id = header.transport_layer_id
        new_datum.save(force_insert=True)
        new_log_entry.save(force_insert=True)
        cfg = get_cfg()
        protocol_id = cfg['body_protocol_id']
        trasport_layer = cfg["transport_layer_id"]
        #Mando los datos para que la esp salga del loop
        respuesta = struct.pack('BB', trasport_layer, protocol_id)
        udp_client.sendto(respuesta, address)
    #Para detener el envio en todas las esp
    for address in conexiones_udp_close:
        udp_client.sendto(respuesta, address)
    print("thread cerrado")
    udp_client.close()
        


if __name__ == '__main__':
    # Referenciado de https://www.datacamp.com/tutorial/a-complete-guide-to-socket-programming-in-python

    # Esperando un mensaje con TCP
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to the host and port
        server.bind((HOST, PORT_CONEXION))
        # listen for incoming connections
        server.listen()
        print(f"Listening on {HOST}:{PORT_CONEXION}")

        while True:
            # accept a client connection
            client_socket, addr = server.accept()
            client_socket.settimeout(10)
            print(f"Accepted connection from {addr[0]}:{addr[1]}")

            # # Consultar la tabla de configuración en la base de datos
            cfg = get_cfg()
            respuesta = struct.pack(
                'BB', cfg['transport_layer_id'], cfg['body_protocol_id'])
            client_socket.sendall(respuesta)

            # Abre conexión con protocolo correspondiente
            if cfg['transport_layer_id'] == TransportLayerValue.TCP:
                server_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # bind the socket to the host and port
                server_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_tcp.bind((HOST, PORT_TCP))
                # listen for incoming connections
                server_tcp.listen()
                print(f"Listening on {HOST}:{PORT_TCP}")
                # Busca a la misma esp.
                tcp_socket, tcp_addr = server_tcp.accept()
                tcp_socket.settimeout(10)
                if tcp_addr[0] == addr[0]:
                    # Usa nuevo socket creado
                    thread = threading.Thread(
                        target=handle_tcp_client, args=(tcp_socket, cfg,))
                    thread.start()
                else:
                    print(f"Invalid connection. Waiting for {addr[0]} instead recv {tcp_addr[0]}")

            elif cfg['transport_layer_id'] == TransportLayerValue.UDP:
                # Establece nueva conexión por UCP con cliente
                #abro un socket udp
                conexiones_udp.add(addr[0])
                if len(conexiones_udp)>1:
                    continue
                server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                server_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                server_udp.bind((HOST, PORT_UDP))
                #Agrego un timeout
                server_udp.settimeout(10)
                print(f"Listening on {HOST}:{PORT_UDP}")
                thread = threading.Thread(
                    target=handle_udp_client, args=(server_udp, cfg,))
                thread.start()
            else:
                print(f'Invalid transport layer ({cfg["transport_layer_id"]})')

            
    except socket.error as e:
        print(f"Error: {e}")
    finally:
        server.close()
