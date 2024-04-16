CREATE TABLE transport_layer (
  id SERIAL PRIMARY KEY,
  name_ VARCHAR (3) NOT NULL
);

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