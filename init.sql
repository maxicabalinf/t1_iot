CREATE TABLE transport_layer (
  id SERIAL PRIMARY KEY,
  name_ VARCHAR (3) NOT NULL
);

-- Valores de capa de transporte
INSERT INTO
  transport_layer (id, name_)
VALUES
  (0, 'TCP'),
  (1, 'UDP');

CREATE TABLE device (
  id SERIAL PRIMARY KEY,
  mac MACADDR,
  UNIQUE (id, mac)
);

CREATE TABLE body_protocol (
  id SERIAL PRIMARY key,
  has_timestamp BOOLEAN,
  has_thpc BOOLEAN,
  has_acc_kpi BOOLEAN,
  has_acc_sensor BOOLEAN
  -- n_atts INTEGER
);

-- Valores de protocolos
INSERT INTO
  body_protocol (
    id,
    has_timestamp,
    has_thpc,
    has_acc_kpi,
    has_acc_sensor
  )
VALUES
  (0, 'f', 'f', 'f', 'f'),
  (1, 't', 'f', 'f', 'f'),
  (2, 't', 't', 'f', 'f'),
  (3, 't', 't', 't', 'f'),
  (4, 't', 't', 'f', 't');

CREATE TABLE log_entry (
  device_id INTEGER,
  transport_layer_id INTEGER,
  timestamp_ TIMESTAMP,
  PRIMARY KEY (device_id, timestamp_),
  FOREIGN KEY (device_id) REFERENCES device(id),
  FOREIGN KEY (transport_layer_id) REFERENCES transport_layer(id)
);

CREATE TABLE datum (
  device_id INTEGER,
  device_mac MACADDR,
  timestamp_ TIMESTAMP,
  delta_time TIME,
  packet_loss INTEGER,
  PRIMARY KEY (device_id, timestamp_),
  FOREIGN KEY (device_id, device_mac) REFERENCES device(id, mac)
);

CREATE TABLE configuration (
  body_protocol_id INTEGER,
  transport_layer_id INTEGER,
  one_row_only_uidx BOOLEAN UNIQUE DEFAULT 't', -- Asegura única fila
  PRIMARY KEY (body_protocol_id, transport_layer_id),
  CHECK (one_row_only_uidx = 't') -- Asegura única fila
);

-- Valor inicial de configuración
INSERT INTO
  configuration (body_protocol_id, transport_layer_id)
VALUES
  (0, 0);