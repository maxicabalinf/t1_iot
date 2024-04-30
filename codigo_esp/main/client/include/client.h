#include <stdint.h>

char* get_header_(uint8_t mac[6], char transport_layer, char protocol_id, uint16_t msg_length);

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
    uint32_t co;
} THCP;

#define THCP_SIZE 10

typedef struct {
    uint32_t rms;
    uint32_t amp_x;
    uint32_t freq_x;
    uint32_t amp_y;
    uint32_t freq_y;
    uint32_t amp_z;
    uint32_t freq_z;
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

const int PROTOCOL_0_BODY_SIZE = 1;

typedef struct {
    uint8_t batt_level;
    uint32_t timestamp;
} Protocol1;

const int PROTOCOL_1_BODY_SIZE = (PROTOCOL_0_BODY_SIZE + 4);

typedef struct {
    uint8_t batt_level;
    uint32_t timestamp;
    THCP tchp;
} Protocol2;

const int PROTOCOL_2_BODY_SIZE = (PROTOCOL_1_BODY_SIZE + THCP_SIZE);

typedef struct {
    uint8_t batt_level;
    uint32_t timestamp;
    THCP tchp;
    AccelerometerKPI kpi;
} Protocol3;

const int PROTOCOL_3_BODY_SIZE = (PROTOCOL_2_BODY_SIZE + KPI_SIZE);

typedef struct {
    uint8_t batt_level;
    uint32_t timestamp;
    THCP tchp;
    AccelerometerSensor sensor;
} Protocol4;

const int PROTOCOL_4_BODY_SIZE = (PROTOCOL_2_BODY_SIZE + ACC_SENSOR_SIZE);

const int PROTOCOL_BODY_SIZE[] = {
    PROTOCOL_0_BODY_SIZE,
    PROTOCOL_1_BODY_SIZE,
    PROTOCOL_2_BODY_SIZE,
    PROTOCOL_3_BODY_SIZE,
    PROTOCOL_4_BODY_SIZE,
};