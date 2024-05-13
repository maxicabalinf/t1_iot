#include "client.h"
#include "esp_log.h"

void app_main(void) {
    nvs_init();
    wifi_init_sta(WIFI_SSID, WIFI_PASSWORD);
    ESP_LOGI(TAG, "Conectado a WiFi!\n");
    // FLujo
    // comenzamos siempre con TCP
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT_CONEXION);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr.s_addr);

    // Crear un socket
    int sock_inicial = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock_inicial < 0) {
        ESP_LOGE(TAG, "Error al crear el socket");
        return;
    }

    // Conectar al servidor
    if (connect(sock_inicial, (struct sockaddr*)&server_addr, sizeof(server_addr)) != 0) {
        ESP_LOGE(TAG, "Error al conectar");
        close(sock_inicial);
        return;
    }
    Configuration cfg = get_configuration(sock_inicial);

    ESP_LOGI(TAG, "transport layer: %i y protocolo: %i", (int)cfg.transport_layer_id, (int)cfg.protocol_id);
    if (cfg.transport_layer_id == 0) {                        // si es TCP
        socket_tcp(cfg); 
    }
    if (cfg.transport_layer_id == 1) {
        // hago funcion que envie udp
        socket_udp(cfg);
    }
}