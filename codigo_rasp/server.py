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
from modelos import Configuration, TransportLayerValue
from packet_parser import get_packet_size

HOST = '0.0.0.0'  # Escucha en todas las interfaces disponibles
PORT_TCP = 1234       # Puerto en el que se escucha


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


def unpack_body_protocol(protocol, body):
    print(len(body))
    if protocol == 0:
        data = struct.unpack('B', body)
        return {"batt_level": data[0]}    
    elif protocol ==1:
        bat, time_stamp = struct.unpack('=BI', body)
        return {"batt_level": bat, 'msg_timestamp': time_stamp}    
    elif protocol ==2:
        bat, time_stamp, temp, pres, hum, co = struct.unpack('=BIBIBI', body)
        return {"batt_level": bat, 'msg_timestamp': time_stamp, "temp" : temp, "hum" : hum , "pres" : pres, "co" : co}
    elif protocol == 3:
        bat, time_stamp, temp, pres, hum, co, *acc_kpi = struct.unpack('=BIBIBI7f', body)
        res= {"batt_level": bat, 'msg_timestamp': time_stamp, "temp" : temp, "hum" : hum , "pres" : pres, "co" : co}
        res["rms"] = acc_kpi[0]
        res["amp_x"] = acc_kpi[1]
        res["freq_x"] = acc_kpi[2]
        res["amp_y"] = acc_kpi[3]
        res["freq_y"] = acc_kpi[4]
        res["amp_z"] = acc_kpi[5]
        res["freq_z"] = acc_kpi[6]
        return res
    elif protocol == 4:
        common = body[:15]
        sensor = body[15:]
        bat, time_stamp, temp, pres, hum, co = struct.unpack('=BIBIBI', common)
        res= {"batt_level": bat, 'msg_timestamp': time_stamp, "temp" : temp, "hum" : hum , "pres" : pres, "co" : co}
        acc_sensor =  struct.unpack('12000f', sensor)
        res['acc_x'] = acc_sensor[0:2000]
        res['acc_y'] = acc_sensor[2000:4000]
        res['acc_z'] = acc_sensor[4000:6000]
        res['rgyr_x'] = acc_sensor[6000:8000]
        res['rgyr_x'] = acc_sensor[8000:10000]
        res['rgyr_x'] = acc_sensor[10000:12000]
        return res

def parse_msg(pkt):
    """Deconstruye el paquete."""
    header = pkt[:12]
    body = pkt[12:]
    id_msg, *mac_adress, transport_layer, protocolo, message_len = struct.unpack('H6BBBH', header)
    body_unpack = unpack_body_protocol(protocolo, body)
    print(body_unpack)

    


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
    pkt = client_sock.recv(13000)
    parse_msg(pkt)


def handle_tcp_client(tcp_client: socket, config):
    """Ejecuta el procedimiento de almacenado para un cliente TCP."""
    protocol_id = config['body_protocol_id']
    pckt = tcp_client.recv(get_packet_size(protocol_id))
    # TODO: parsear paquete
    # TODO: almacenar mensaje (Datum)
    # TODO: escribir logs (Log)
    # TODO: escribir loss


if __name__ == '__main__':
    # Referenciado de https://www.datacamp.com/tutorial/a-complete-guide-to-socket-programming-in-python

    # Esperando un mensaje con TCP
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to the host and port
        server.bind((HOST, PORT_TCP))
        # listen for incoming connections
        server.listen()
        print(f"Listening on {HOST}:{PORT_TCP}")

        while True:
            # accept a client connection
            client_socket, addr = server.accept()
            client_socket.settimeout(10)
            print(f"Accepted connection from {addr[0]}:{addr[1]}")

            # # Consultar la tabla de configuración en la base de datos
            cfg = get_cfg()
            respuesta = struct.pack('BB', cfg['transport_layer_id'], cfg['body_protocol_id'])
            client_socket.sendall(respuesta)
            
            # Abre conexión con protocolo correspondiente
            if cfg['transport_layer_id'] == TransportLayerValue.TCP.value:
                #Busca a la misma esp
                tcp_socket, tcp_addr = server.accept()
                if tcp_addr[0] == addr[0]:
                    # Usa nuevo socket creado
                    thread = threading.Thread(
                        target=handle_client, args=(tcp_socket, tcp_addr,))
                    thread.start()
                else:
                    print(f"Invalid connection. Waiting for {addr[0]} instead recv {tcp_addr[0]}")
                
                        
            elif cfg['transport_layer_id'] == TransportLayerValue.UDP.value:
                # Establece nueva conexión por UCP con cliente
                thread = threading.Thread(
                    target=handle_client, args=(client_socket, addr,))
                thread.start()
            else:
                print(f'Invalid transport layer ({cfg["transport_layer_id"]})')
            
            break
    except socket.error as e:
        print(f"Error: {e}")
    finally:
        server.close()
