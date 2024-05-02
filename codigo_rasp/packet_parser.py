"""

--- Packing en C ---



char * pack(int packet_id, float value_float, char * text) {
    char * packet = malloc(12 + strlen(text));
    memcpy(packet, &packet_id, 4);
    memcpy(packet + 4, &value_float, 4);
    memcpy(packet + 8, &largo_text, 4);
    memcpy(packet + 12, text, largo_text);
    return packet;
}

//Luego mandan el paquete por el socket


--- Unpacking en C ---


void unpack(char * packet) {
    int packet_id;
    float value_float;
    int largo_text;
    char * text;

    memcpy(&packet_id, packet, 4);
    memcpy(&value_float, packet + 4, 4);
    memcpy(&largo_text, packet + 8, 4);

    text = malloc(largo_text + 1); // +1 for the null-terminator
    if (text == NULL) {
        // Handle memory allocation failure
        return;
    }

    memcpy(text, packet + 12, largo_text);
    text[largo_text] = '\0'; // Null-terminate the string

    printf("Packet ID: %d\n", packet_id);
    printf("Float Value: %f\n", value_float);
    printf("Text: %s\n", text);

    free(text);
}


"""

import struct  # Libreria muy util para codificar y decodificar datos

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


def pack(packet_id: int, value_float: float, text: str) -> bytes:
    """
     '<' significa que se codifica en little-endian
     'i' significa que el primer dato es un entero de 4 bytes
     'f' significa que el segundo dato es un float de 4 bytes
     'i' significa que el tercer dato es un entero de 4 bytes
     '{}s'.format(largo_text) (ej: 10s para un string de largo 10) significa
     que el string tiene largo variable,

    Documentacion de struct: https://docs.python.org/3/library/struct.html
    """
    largo_text = len(text)
    return struct.pack(f'<ifi{largo_text}s',
                       packet_id,
                       value_float,
                       largo_text,
                       text.encode('utf-8'))


# Little endian, unsigned short, 6 char, unsigned char, unsigned char,
# unsigned short
HEADER_FORMAT = '<H6sBBH'


class Header:
    """Representación del encabezado de un paquete."""
    packet_id: int
    mac: bytes
    transport_layer: int
    protocol_id: int
    packet_length: int

    def __init__(self, header_bytes: bytes) -> None:
        (
            self.packet_id,
            self.mac,
            self.transport_layer,
            self.protocol_id,
            self.packet_length,
        ) = struct.unpack(HEADER_FORMAT, header_bytes)


def unpack(packet: bytes) -> list:
    """Desempaqueta en [packet_id, value_float, text]"""
    packet_id, value_float, largo_text = struct.unpack('<ifi', packet[:12])
    text = struct.unpack(f'<{largo_text}s', packet[12:])[0] \
        .decode('utf-8')
    return [packet_id, value_float, text]


if __name__ == "__main__":
    mensage = pack(1, 3.20, "Hola mundo")
    print(mensage)
    print(unpack(mensage))
