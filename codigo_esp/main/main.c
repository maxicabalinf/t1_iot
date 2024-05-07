#include "client.h"
#include "esp_log.h"

void app_main(void) {
    nvs_init();
    wifi_init_sta(WIFI_SSID, WIFI_PASSWORD);
    ESP_LOGI(TAG, "Conectado a WiFi!\n");
    // FLujo
    while (1) {  // comenzamos siempre con TCP
        struct sockaddr_in server_addr;
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(SERVER_PORT_TCP);
        inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr.s_addr);

        // Crear un socket
        int sock_inicial = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (sock_inicial < 0) {
            ESP_LOGE(TAG, "Error al crear el socket");
            break;
        }

        // Conectar al servidor
        if (connect(sock_inicial, (struct sockaddr*)&server_addr, sizeof(server_addr)) != 0) {
            ESP_LOGE(TAG, "Error al conectar");
            close(sock_inicial);
            break;
        }
        while (1) {
            char* configuration = malloc(2);
            int len = recv(sock_inicial, configuration, 2, 0);
            char transport_layer = configuration[0];
            char protocolo = configuration[1];
            printf("transport layer: %i y protocolo: %i", (int) transport_layer, (int) protocolo);
            char* message = get_message(transport_layer, protocolo);
            free(configuration);
            if (transport_layer == 0) {                // si es TCP
                socket_tcp(message, get_msg_size(protocolo));  // falta ver una forma de ver el tamaño del protocolo
                free(message);
            }
            if (transport_layer == 1) {
                // hago funcion que envie udp
                socket_udp(message,get_msg_size(protocolo));
                free(message);
            }
            // Reiniciamos el ciclo
        }
    }
}