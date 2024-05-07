idf_component_register(SRCS "main.c"
    INCLUDE_DIRS "."
    REQUIRES client
    PRIV_REQUIRES
    esp_event
    log
    esp_system
    esp_wifi
    freertos
    lwip
    nvs_flash
)
                  
