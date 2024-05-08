"""Funciones para procesar paquetes."""
import struct  # Libreria muy util para codificar y decodificar datos
from time import time
from modelos import Datum, LogEntry

HEADER_SIZE = 12
THCP_SIZE = 10
KPI_SIZE = 28
ACC_ARRAY_SIZE = 8000
ACC_SENSOR_SIZE = 48000
PROTOCOL_0_BODY_SIZE = 1
PROTOCOL_1_BODY_SIZE = PROTOCOL_0_BODY_SIZE + 4
PROTOCOL_2_BODY_SIZE = PROTOCOL_1_BODY_SIZE + THCP_SIZE
PROTOCOL_3_BODY_SIZE = PROTOCOL_2_BODY_SIZE + KPI_SIZE
PROTOCOL_4_BODY_SIZE = PROTOCOL_2_BODY_SIZE + ACC_SENSOR_SIZE
PROTOCOL_BODY_SIZE = [
    PROTOCOL_0_BODY_SIZE,
    PROTOCOL_1_BODY_SIZE,
    PROTOCOL_2_BODY_SIZE,
    PROTOCOL_3_BODY_SIZE,
    PROTOCOL_4_BODY_SIZE,
]


def get_packet_size(body_protocol_id):
    """Calcula el tamaño de paquete de un protocolo dado."""
    return PROTOCOL_BODY_SIZE[body_protocol_id] + HEADER_SIZE


# Little endian, unsigned short, 6 char, unsigned char, unsigned char,
# unsigned short
HEADER_FORMAT = '<H6sBBH'

PROTOCOL_0_BODY_FORMAT = '<B'
PROTOCOL_1_BODY_FORMAT = PROTOCOL_0_BODY_FORMAT + 'I'
PROTOCOL_2_BODY_FORMAT = PROTOCOL_1_BODY_FORMAT + 'BIBf'
PROTOCOL_3_BODY_FORMAT = PROTOCOL_2_BODY_FORMAT + '7f'
PROTOCOL_4_BODY_FORMAT = PROTOCOL_2_BODY_FORMAT + '12000f'
PROTOCOL_BODY_FORMAT = [
    PROTOCOL_0_BODY_FORMAT,
    PROTOCOL_1_BODY_FORMAT,
    PROTOCOL_2_BODY_FORMAT,
    PROTOCOL_3_BODY_FORMAT,
    PROTOCOL_4_BODY_FORMAT,
]


def unpack_header(header_bytes: bytes, datum_obj: Datum,
                  log_obj: LogEntry) -> tuple:
    """Desempaqueta el cuerpo de un paquete a los modelos objetivo."""
    packet_id: int
    packet_length: int
    mac: bytes
    (
        packet_id,
        mac,
        log_obj.transport_layer_id,
        log_obj.body_protocol_id,
        packet_length,
    ) = struct.unpack(HEADER_FORMAT, header_bytes)
    datum_obj.device_mac = mac.hex()

    return (packet_id, packet_length)


def unpack_body(protocol_id, body_bytes: bytes, datum_obj: Datum) -> None:
    """Desempaqueta el cuerpo de un paquete."""
    # TODO: abordar caso de pérdida
    unpacked = struct.unpack(PROTOCOL_BODY_FORMAT[protocol_id], body_bytes)

    # Estructuración de tupla desempaquetada según protocolo.
    datum_obj.batt_level = unpacked[0]

    if protocol_id == 0:
        return

    datum_obj.msg_timestamp = unpacked[1]

    if protocol_id == 1:
        return

    datum_obj.temp = unpacked[2]
    datum_obj.hum = unpacked[3]
    datum_obj.pres = unpacked[4]
    datum_obj.co = unpacked[5]

    if protocol_id == 2:
        return

    if protocol_id == 3:
        datum_obj.rms = unpacked[6]
        datum_obj.amp_x = unpacked[7]
        datum_obj.freq_x = unpacked[8]
        datum_obj.amp_y = unpacked[9]
        datum_obj.freq_y = unpacked[10]
        datum_obj.amp_z = unpacked[11]
        datum_obj.freq_z = unpacked[12]

    if protocol_id == 4:
        datum_obj.acc_x = unpacked[6]
        datum_obj.acc_y = unpacked[7]
        datum_obj.acc_z = unpacked[8]
        datum_obj.rgyr_x = unpacked[9]
        datum_obj.rgyr_y = unpacked[10]
        datum_obj.rgyr_z = unpacked[11]


def unpack(packet_bytes: bytes) -> Datum:
    """Desempaqueta bytes y devuelve los modelos correspondientes."""
    # Modelos para rellenar.
    new_datum = Datum()
    new_log_entry = LogEntry()

    # Obtención de datos.
    new_datum.saved_timestamp = int(time())
    (packet_id, packet_length) = unpack_header(
        packet_bytes[:12], new_datum, new_log_entry)
    new_datum.packet_loss = packet_length - len(packet_bytes)
    unpack_body(new_log_entry.body_protocol_id, packet_bytes[12:], new_datum)
    if new_log_entry.body_protocol_id > 0:
        new_datum.delta_time = new_datum.saved_timestamp \
            - new_datum.msg_timestamp

    return (packet_id, new_datum, new_log_entry)
