idf_component_register(
  SRCS "client.c"
  INCLUDE_DIRS "include"
  PRIV_REQUIRES
    esp_event
    log
    esp_system
    esp_wifi
    freertos
    lwip
    nvs_flash
)