#include <math.h>
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

#define WIFI_SSID "raspiiot"
#define WIFI_PASSWORD "raspiiot"
#define SERVER_IP "192.168.0.1"  // IP del servidor
#define SERVER_PORT 1234

// Variables de WiFi
#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAIL_BIT BIT1
static const char* TAG = "WIFI";
static int s_retry_num = 0;
static EventGroupHandle_t s_wifi_event_group;

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

void socket_tcp() {
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
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

    // Enviar mensaje "Hola Mundo"
    send(sock, "hola mundo", strlen("hola mundo"), 0);

    // Recibir respuesta

    char rx_buffer[128];
    int rx_len = recv(sock, rx_buffer, sizeof(rx_buffer) - 1, 0);
    if (rx_len < 0) {
        ESP_LOGE(TAG, "Error al recibir datos");
        return;
    }
    ESP_LOGI(TAG, "Datos recibidos: %s", rx_buffer);

    // Cerrar el socket
    close(sock);
}
//--------------------------------------------------------------------//
// Empaquetado de datos
//--------------------------------------------------------------------//

char* get_headers(char t_l, char protocol){
  char* header = malloc(12);
  int n = 65535;
  int id = rand() % (n + 1); //2 bytes
  memcpy((void*) header, (void*) &id, 2);
  ///no se como leer la mac adress //6 bytes
  header[8] = t_l; // 1 byte
  header[9] = protocol // 1 byte
  unsigned short length;
  switch (protocol){
    case 0:
       length = 13;
    case 1:
       length = 17;
    case 2:
       length = 27;
    case 3:
       length = 55;
    case 4:
       length = 48027;
    memcpy((void*) &(head[10]), (void*) &length, 2);
  }
  return header;
}

float random_float(float min, float max) {
    return min + (float)rand() / ((float)RAND_MAX / (max - min));
}

void get_acceloremeter_kpi(float* res) {
    res[1] = random_float(0.0059, 0.12);  // ampx
    res[2] = random_float(29.0, 31.0);    // freqx
    res[3] = random_float(0.0041, 0.11);  // ampy
    res[4] = random_float(59.0, 61.0);    // freqy
    res[5] = random_float(0.008, 0.15);   // ampz
    res[6] = random_float(89.0, 91.0);    // freqz
    res[0] = (float)sqrt(
        (res[1] * res[1]) +
        (res[3] * res[3]) +
        (res[5] * res[5]));  // rms
}



char* get_thpc_data() {
    char* data_thpc = malloc(10);
    data_thpc[0] = (char) 5 + (rand() % 26); //temperatura 1 byte
    long pres = 1000 + (rand() % 201); // presion 4 bytes
    memcpy((void*) &(data_thpc[1]), (void*) &pres, 4);
    data_thpc[5] = (char) random_float(30.0,80.0); // humedad 1 byte
    float co = random_float(30.0,200.0); // co 4 bytes
    memcpy((void*) &(data_thpc[6]), (void*) &co, 4); 
    return data_thpc;
}

uint8_t get_batt_level() {
    return (uint8_t)rand() % 101;
}

uint32_t get_timestamp() {
    time_t t = time(NULL); //preguntarrrrr
    return (uint32_t)t;
}

char* get_data_protocol_0(){
    char* data = malloc(1);
    data[0] = get_batt_level();
    return data;
}
char* get_data_protocol_1(){
    char* data = malloc(5);
    data[0] = get_batt_level();
    uint32_t timestamp = get_timestamp();
    memcpy((void*) &(data[1]), (void*) &timestamp, 4);
    return data;
}
char* get_data_protocol_2(){
    char* data = malloc(15);
    data[0] = get_batt_level();
    uint32_t timestamp = get_timestamp();
    memcpy((void*) &(data[1]), (void*) &timestamp, 4);
    char* thcp_data = get_thpc_data();
    memcpy((void*) &(data[5]), (void*) &thcp_data, 10);
    free(thcp_data);
    return data;
}

void app_main(void) {
    //nvs_init();
    //wifi_init_sta(WIFI_SSID, WIFI_PASSWORD);
    //ESP_LOGI(TAG, "Conectado a WiFi!\n");
    //socket_tcp();
    float t_data[7];
    get_acceloremeter_kpi(t_data);
    printf("%f\t%f\t%f\t%f\t%f\t%f\t%f", t_data[0],t_data[1],t_data[2],t_data[3],t_data[4],t_data[5],t_data[6]);

}