#pragma once

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "esp_event.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "lwip/err.h"
#include "lwip/sockets.h"  // Para sockets
#include "lwip/sys.h"
#include "nvs_flash.h"
// Credenciales de WiFi

#define WIFI_SSID "Julieta 2.4"
#define WIFI_PASSWORD "chile.com"
#define SERVER_IP "192.168.100.36"  // IP del servidor
#define SERVER_PORT_TCP 1234
#define SERVER_PORT_UDP 1235

// Variables de WiFi
#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAIL_BIT BIT1
static const char* TAG = "WIFI";
static int s_retry_num = 0;
static EventGroupHandle_t s_wifi_event_group;

// WIFI
void nvs_init();
void socket_tcp();
void wifi_init_sta(char* ssid, char* password);

uint8_t* get_header_(uint8_t mac[6], uint8_t transport_layer, uint8_t protocol_id, uint16_t msg_length);
void event_handler(void* arg, esp_event_base_t event_base, int32_t event_id, void* event_data);
int get_msg_size(char protocol);
void socket_tcp(char* msg, int size);
void socket_udp(char* msg, int size);

enum TransportLayer {
    TCP = 0,
    UDP = 1
};

typedef struct {
    uint8_t protocol_id;
    uint8_t transport_layer_id;
    uint8_t recv;
} Configuration;

typedef struct {
    uint16_t msg_id;
    uint8_t mac[6];
    uint8_t transport_layer;
    uint8_t protocol_id;
    uint16_t length;
} Header;

#define HEADER_SIZE 12

typedef struct {
    int8_t temp;
    uint32_t press;
    uint8_t hum;
    float co;
} THCP;

#define THCP_SIZE 10

typedef struct {
    float rms;
    float amp_x;
    float freq_x;
    float amp_y;
    float freq_y;
    float amp_z;
    float freq_z;
} AccelerometerKPI;

#define KPI_SIZE 28

typedef struct {
    float acc_x[2000];
    float acc_y[2000];
    float acc_z[2000];
    float rgyr_x[2000];
    float rgyr_y[2000];
    float rgyr_z[2000];
} AccelerometerSensor;

#define ACC_ARRAY_SIZE 8000
#define ACC_SENSOR_SIZE 48000

typedef struct {
    uint8_t batt_level;
} Protocol0;

static const int PROTOCOL_0_BODY_SIZE = 1;

typedef struct {
    uint8_t batt_level;
    uint32_t timestamp;
} Protocol1;

static const int PROTOCOL_1_BODY_SIZE = (PROTOCOL_0_BODY_SIZE + 4);

typedef struct {
    uint8_t batt_level;
    uint32_t timestamp;
    THCP tchp;
} Protocol2;

static const int PROTOCOL_2_BODY_SIZE = (PROTOCOL_1_BODY_SIZE + THCP_SIZE);

typedef struct {
    uint8_t batt_level;
    uint32_t timestamp;
    THCP tchp;
    AccelerometerKPI kpi;
} Protocol3;

static const int PROTOCOL_3_BODY_SIZE = (PROTOCOL_2_BODY_SIZE + KPI_SIZE);

typedef struct {
    uint8_t batt_level;
    uint32_t timestamp;
    THCP tchp;
    AccelerometerSensor sensor;
} Protocol4;

static const int PROTOCOL_4_BODY_SIZE = (PROTOCOL_2_BODY_SIZE + ACC_SENSOR_SIZE);

static const int PROTOCOL_BODY_SIZE[] = {
    PROTOCOL_0_BODY_SIZE,
    PROTOCOL_1_BODY_SIZE,
    PROTOCOL_2_BODY_SIZE,
    PROTOCOL_3_BODY_SIZE,
    PROTOCOL_4_BODY_SIZE,
};

/**
 * @brief Genera un mensaje para enviar al servidor.
 *
 * @param transport_layer Tipo de capa de transporte.
 * @param protocol_id Protocolo del cuerpo del mensaje.
 * @return char* Puntero al mensaje.
 */
char* get_message(uint8_t transport_layer, uint8_t protocol_id);

/**
 * @brief Devuelve la configuración del servidor. Asume que recibe únicamente
 * dos bytes.
 *
 * @return Configuration
 */
Configuration get_configuration(int socket);