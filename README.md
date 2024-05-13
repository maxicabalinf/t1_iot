## Plantilla T1

### Integrantes

- Renato Andaur
- Maximiliano Cabalín
- Cristian Romero

---

El repositorio se compone de dos grandes secciones: codigo_esp y codigo_rasp.

### codigo_esp
Contiene el código para la ESP32 escrito en C y con CMake de la mano del framework de ESP. Tiene una carpeta `main` que contiene el ejecutable principal para el cliente del proyecto y una carpeta `components/client` que tiene las definiciones e implementaciones necesarias para las funcionalidades del cliente.

#### Compilación y ejecución
Se puede compilar y flashear en el dispositivo usando la extensión ESP-IDF de VSCode.

TODO: agregar comandos

### codigo_rasp
Contiene el código del servidor del proyecto escrito en Python. Define los modelos de datos en el archivo `modelos.py`, las herramientas para decodificación de paquetes en `packet_parser.py` y el flujo del servidor está definido en el archivo `server.py`. Para ejecutar el servidor se debe ejecutar lo siguiente:
```bash
python server.py
```

### Flujo

![Flujo de operación](/images/flujoiot.png)



## Comandos de docker


### Iniciar la base de datos

```bash
docker compose up -d
```

### Detener la base de datos

```bash
docker compose down
```

### Borrar la base de datos

```bash
docker compose down 
docker volume rm postgres_data_iot
```