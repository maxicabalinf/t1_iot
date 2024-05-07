#include "client.h"
#include "esp_log.h"

void app_main(void) {
    nvs_init();
    wifi_init_sta(WIFI_SSID, WIFI_PASSWORD);
    ESP_LOGI(TAG, "Conectado a WiFi!\n");
    char* message = get_message(0, 1);
    // FLujo
    while (1) {  // comenzamos siempre con TCP
        struct sockaddr_in server_addr;
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(SERVER_PORT);
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
        while (1) {
            char* configuration = malloc(2);
            int len = recv(sock_inicial, configuration, 2, 0);
            char transport_layer = configuration[0];
            char protocolo = configuration[1];
            char* message = get_message(transport_layer, protocolo);
            free(configuration);
            if (transport_layer == 0) {                // si es TCP
                socket_tcp(message, sizeof(message));  // falta ver una forma de ver el tamaño del protocolo
            }
            if (transport_layer == 1) {
                // hago funcion que envie udp
            }
            // Reiniciamos el ciclo
        }
    }
}