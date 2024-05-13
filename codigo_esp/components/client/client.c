#include "client.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "esp_event.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "lwip/err.h"
#include "lwip/sockets.h"  // Para sockets
#include "lwip/sys.h"
#include "nvs_flash.h"
#include "esp_sleep.h"


void event_handler(void* arg, esp_event_base_t event_base,
                   int32_t event_id, void* event_data) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (event_base == WIFI_EVENT &&
               event_id == WIFI_EVENT_STA_DISCONNECTED) {
        if (s_retry_num < 10) {
            esp_wifi_connect();
            s_retry_num++;
            ESP_LOGI(TAG, "retry to connect to the AP");
        } else {
            xEventGroupSetBits(s_wifi_event_group, WIFI_FAIL_BIT);
        }
        ESP_LOGI(TAG, "connect to the AP fail");
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*)event_data;
        ESP_LOGI(TAG, "got ip:" IPSTR, IP2STR(&event->ip_info.ip));
        s_retry_num = 0;
        xEventGroupSetBits(s_wifi_event_group, WIFI_CONNECTED_BIT);
    }
}

void wifi_init_sta(char* ssid, char* password) {
    s_wifi_event_group = xEventGroupCreate();

    ESP_ERROR_CHECK(esp_netif_init());

    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    esp_event_handler_instance_t instance_any_id;
    esp_event_handler_instance_t instance_got_ip;
    ESP_ERROR_CHECK(esp_event_handler_instance_register(
        WIFI_EVENT, ESP_EVENT_ANY_ID, &event_handler, NULL, &instance_any_id));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(
        IP_EVENT, IP_EVENT_STA_GOT_IP, &event_handler, NULL, &instance_got_ip));

    wifi_config_t wifi_config;
    memset(&wifi_config, 0, sizeof(wifi_config_t));

    // Set the specific fields
    strcpy((char*)wifi_config.sta.ssid, WIFI_SSID);
    strcpy((char*)wifi_config.sta.password, WIFI_PASSWORD);
    wifi_config.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;
    wifi_config.sta.pmf_cfg.capable = true;
    wifi_config.sta.pmf_cfg.required = false;
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "wifi_init_sta finished.");

    EventBits_t bits = xEventGroupWaitBits(s_wifi_event_group,
                                           WIFI_CONNECTED_BIT | WIFI_FAIL_BIT,
                                           pdFALSE, pdFALSE, portMAX_DELAY);

    if (bits & WIFI_CONNECTED_BIT) {
        ESP_LOGI(TAG, "connected to ap SSID:%s password:%s", ssid,
                 password);
    } else if (bits & WIFI_FAIL_BIT) {
        ESP_LOGI(TAG, "Failed to connect to SSID:%s, password:%s", ssid,
                 password);
    } else {
        ESP_LOGE(TAG, "UNEXPECTED EVENT");
    }

    ESP_ERROR_CHECK(esp_event_handler_instance_unregister(
        IP_EVENT, IP_EVENT_STA_GOT_IP, instance_got_ip));
    ESP_ERROR_CHECK(esp_event_handler_instance_unregister(
        WIFI_EVENT, ESP_EVENT_ANY_ID, instance_any_id));
    vEventGroupDelete(s_wifi_event_group);
}

void nvs_init() {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES ||
        ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
}

void socket_tcp(Configuration cfg) {
    char* msg = get_message(cfg.transport_layer_id, cfg.protocol_id);
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT_TCP);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr.s_addr);

    // Crear un socket
    int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock < 0) {
        ESP_LOGE(TAG, "Error al crear el socket");
        return;
    }

    // Conectar al servidor
    if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) != 0) {
        ESP_LOGE(TAG, "Error al conectar");
        close(sock);
        return;
    }

    // Enviar mensaje
    ESP_LOGI(TAG, "Send message.");
    send(sock, msg, get_msg_size(cfg.protocol_id), 0);
    free(msg);

    //Espera a recibir la configuración como ack antes de entrar en deep sleep
    get_configuration(sock);
    // Cerrar el socket
    close(sock);

    //Gracefully shutdown wifi
    ESP_ERROR_CHECK(esp_wifi_stop());

    //Enter Deep Sleep
    esp_sleep_enable_timer_wakeup(5 * 1000000); // 60 segundos en microsegundos CAMBIAR A 60
    esp_deep_sleep_start();
}

Configuration get_configuration(int server_socket) {
    char configuration[2];
    int len = recv(server_socket, configuration, 2, 0);
    if (len < 0) {
        return (Configuration){0,0,0};
    }
    return (Configuration){configuration[1], configuration[0], 1};
}

void socket_udp(Configuration cfg) {
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT_UDP);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr.s_addr);
    enum TransportLayer trasnport_layer = UDP;

    // Crea un socket
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        ESP_LOGE(TAG, "Error al crear el socket");
        return;
    }
    // Configurar el socket para que sea no bloqueante
    fcntl(sock, F_SETFL, O_NONBLOCK);

    while (trasnport_layer == UDP) {
        char* msg = get_message(cfg.transport_layer_id, cfg.protocol_id);
        // Envia mensaje
        int err = sendto(sock, msg, get_msg_size(cfg.protocol_id), 0, (struct sockaddr*)&server_addr,
                         sizeof(server_addr));
        if (err < 0) {
            ESP_LOGE(TAG, "Error occurred during sending: errno %d", errno);
            return;
        }
        ESP_LOGI(TAG, "Mensaje enviado con éxito con UDP");

        vTaskDelay(1000 / portTICK_PERIOD_MS);
        // Recibe configuracion
        Configuration cfg = get_configuration(sock);
        if (cfg.recv == 1) {
            trasnport_layer = cfg.transport_layer_id;
        }
    }
    close(sock);
    esp_restart();
}
//--------------------------------------------------------------------//
// Empaquetado de datos
//--------------------------------------------------------------------//
int get_msg_size(char protocol) {
    int size = HEADER_SIZE + (int)PROTOCOL_BODY_SIZE[(int)protocol];
    return size;
}

void copy_mac(uint8_t* source, uint8_t* target) {
    for (int i = 0; i < 6; i++) {
        target[i] = source[i];
    }
}

uint8_t msg_id = 0;

uint8_t* get_header_(uint8_t mac[6], uint8_t transport_layer, uint8_t protocol_id, uint16_t msg_length) {
    Header* header = malloc(sizeof(Header));
    header->msg_id = msg_id++;
    if (mac == NULL) {
        esp_wifi_get_mac(WIFI_IF_STA, header->mac);
    } else {
        copy_mac(mac, header->mac);
    }
    header->transport_layer = transport_layer;
    header->protocol_id = protocol_id;
    header->length = msg_length;
    ESP_LOGI(TAG, "message size: %i", header->length);
    return (uint8_t*)header;
}

float random_float(float min, float max) {
    return min + (float)rand() / ((float)RAND_MAX / (max - min));
}

int random_int(int min, int max) {
    return min + rand() % (max - min + 1);
}

char* get_acceloremeter_kpi() {
    AccelerometerKPI* kpi = malloc(sizeof(AccelerometerKPI));
    kpi->amp_x = random_float(0.0059, 0.12);  // ampx
    kpi->freq_x = random_float(29.0, 31.0);   // freqx
    kpi->amp_y = random_float(0.0041, 0.11);  // ampy
    kpi->freq_y = random_float(59.0, 61.0);   // freqy
    kpi->amp_z = random_float(0.008, 0.15);   // ampz
    kpi->freq_z = random_float(89.0, 91.0);   // freqz
    kpi->rms = (float)sqrt(                   // rms
        (kpi->amp_x * kpi->amp_x) +
        (kpi->amp_y * kpi->amp_y) +
        (kpi->amp_z * kpi->amp_z));

    return (char*)kpi;
}

char* get_thpc_data() {
    THCP thcp;
    thcp.temp = (uint8_t) random_int(5, 30);  // temperatura 1 byte
    thcp.press = (uint32_t) random_int(1000, 1200);   // presion 4 bytes
    thcp.hum = (uint8_t) random_int(30, 80);  // humedad 1 byte
    thcp.co = random_float(30.0, 200.0);  // co 4 bytes

    char* data_thpc = malloc(THCP_SIZE);
    memcpy((void*)&(data_thpc[0]), (void*)&thcp.temp, sizeof(thcp.temp));
    memcpy((void*)&(data_thpc[1]), (void*)&thcp.press, sizeof(thcp.press));
    memcpy((void*)&(data_thpc[5]), (void*)&thcp.hum, sizeof(thcp.hum));
    memcpy((void*)&(data_thpc[6]), (void*)&thcp.co, sizeof(thcp.co));

    return data_thpc;
}

uint8_t get_batt_level() {
    return (uint8_t)rand() % 101;
}

uint32_t get_timestamp() {
    time_t t = time(NULL);  // preguntarrrrr
    return (uint32_t) t;
}

/**
 * @brief Crea un cuerpo para el protocolo 0.
 *
 * @return char* Puntero al cuerpo.
 */
char* get_data_protocol_0() {
    char* data = malloc(PROTOCOL_BODY_SIZE[0]);
    data[0] = get_batt_level();
    return data;
}

/**
 * @brief Crea un cuerpo para el protocolo 1.
 *
 * @return char* Puntero al cuerpo.
 */
char* get_data_protocol_1() {
    char* data = malloc(PROTOCOL_BODY_SIZE[1]);
    data[0] = get_batt_level();
    uint32_t timestamp = get_timestamp();
    memcpy((void*)&(data[1]), (void*)&timestamp, sizeof(timestamp));
    return data;
}

/**
 * @brief Copia bytes de un lugar a otro. Libera el espacio del origen de los
 * datos y actualiza el desfase del destino.
 *
 * @param destination Dirección del destino.
 * @param source Dirección del origen.
 * @param size Cantidad de bytes a copiar.
 * @param cursor Dirección del cursor que lleva la cuenta del desfase.
 */
void cat_n_free_n_shift(void* destination, void* source, size_t size,
                        int* cursor) {
    memcpy(destination, source, size);
    free(source);
    *cursor += size;
};

/**
 * @brief Crea un cuerpo para el protocolo 2.
 *
 * @return char* Puntero al cuerpo.
 */
char* get_data_protocol_2() {
    char* data = malloc(PROTOCOL_BODY_SIZE[2]);
    int cursor = 0;
    cat_n_free_n_shift(&(data[cursor]), get_data_protocol_1(),
                       PROTOCOL_BODY_SIZE[1], &cursor);
    cat_n_free_n_shift(&(data[cursor]), get_thpc_data(),
                       THCP_SIZE, &cursor);

    return data;
}

/**
 * @brief Crea un cuerpo para el protocolo 3.
 *
 * @return char* Puntero al cuerpo.
 */
char* get_data_protocol_3() {
    char* data = malloc(PROTOCOL_BODY_SIZE[3]);
    int cursor = 0;

    cat_n_free_n_shift(&(data[cursor]), get_data_protocol_2(),
                       PROTOCOL_BODY_SIZE[2], &cursor);
    cat_n_free_n_shift(&(data[cursor]), get_acceloremeter_kpi(),
                       KPI_SIZE, &cursor);

    return data;
}

float* get_acc() {
    float* acc_data = malloc(2000 * sizeof(float));
    for (int i = 0; i < 2000; i++) {
        acc_data[i] = random_float(-16.0, 16.0);
    }
    return acc_data;
}

float* get_rgyr() {
    float* rgyr_data = malloc(2000 * sizeof(float));
    for (int i = 0; i < 2000; i++) {
        rgyr_data[i] = random_float(-1000.0, 1000.0);
    }
    return rgyr_data;
}

/**
 * @brief Crea un cuerpo para el protocolo 4.
 *
 * @return char* Puntero al cuerpo.
 */
char* get_data_protocol_4() {
    char* data = malloc(PROTOCOL_BODY_SIZE[4]);
    int cursor = 0;

    cat_n_free_n_shift(&(data[cursor]), get_data_protocol_2(),
                       PROTOCOL_BODY_SIZE[2], &cursor);
    for (int i = 0; i < 3; i++) {  // Añade acc_<axis>
        cat_n_free_n_shift(&(data[cursor]), get_acc(),
                           ACC_ARRAY_SIZE, &cursor);
    }
    for (int i = 0; i < 3; i++) {  // Añade rgyr_<axis>
        cat_n_free_n_shift(&(data[cursor]), get_rgyr(),
                           ACC_ARRAY_SIZE, &cursor);
    }

    return data;
}

// Agrupa los generadores de cuerpo de mensaje.
char* (*body_creator[])() = {
    get_data_protocol_0,
    get_data_protocol_1,
    get_data_protocol_2,
    get_data_protocol_3,
    get_data_protocol_4,
};

/**
 * @brief Genera un mensaje para enviar al servidor.
 *
 * @param transport_layer Tipo de capa de transporte.
 * @param protocol_id Protocolo del cuerpo del mensaje.
 * @return char* Puntero al mensaje.
 */
char* get_message(uint8_t transport_layer, uint8_t protocol_id) {
    int body_size = PROTOCOL_BODY_SIZE[protocol_id];
    char* body_data = body_creator[protocol_id]();
    int msg_length = HEADER_SIZE + body_size;
    char* msg = malloc(msg_length);

    int cursor = 0;
    cat_n_free_n_shift(&msg[cursor],
                       get_header_(NULL, transport_layer, protocol_id,
                                   msg_length),
                       HEADER_SIZE,
                       &cursor);
    cat_n_free_n_shift(&msg[cursor], body_data, body_size, &cursor);

    return msg;
}
