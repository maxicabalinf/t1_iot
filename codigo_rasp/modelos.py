"""Definición de modelos de datos."""
from enum import Enum
from playhouse.postgres_ext import ArrayField
from peewee import Model, PostgresqlDatabase, IntegerField, TextField, \
    TimestampField, ForeignKeyField, FloatField, CompositeKey, BooleanField, \
    Check, SQL

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'database': 'iot_db'
}
db = PostgresqlDatabase(**db_config)


class TransportLayerValue(Enum):
    """Enumeración de tipos de capa de transporte."""
    TCP = 0
    UDP = 1


class BaseModel(Model):
    """Definición de un modelo"""
    class Meta:
        database = db
        legacy_table_names = False


class TransportLayer(BaseModel):
    """Representación de los valores de capa de transporte."""
    id = IntegerField(primary_key=True)
    name = TextField(unique=True)


class Device(BaseModel):
    """Representación de un dispositivo."""
    id = IntegerField(primary_key=True)
    mac = TextField()

    class Meta:
        indexes = ((('id', 'mac'), True),)


class LogEntry(BaseModel):
    """BaseModelo de datos para los logs."""
    device_id = ForeignKeyField(Device, field='id')
    transport_layer_id = ForeignKeyField(TransportLayer, field='id')
    body_protocol_id = IntegerField()
    timestamp = TimestampField()

    class Meta:
        primary_key = CompositeKey('device_id', 'timestamp')


class Datum(BaseModel):
    """Representación de un dato guardado."""
    device_id = IntegerField()
    device_mac = TextField()
    saved_timestamp = TimestampField()
    delta_time = IntegerField()
    packet_loss = IntegerField()

    # Data fields
    batt_level = IntegerField()
    msg_timestamp = TimestampField()

    # THCP fields
    temp = IntegerField()
    hum = IntegerField()
    pres = IntegerField()
    co = FloatField()

    # accelerometer_kpi fields
    rms = FloatField()
    amp_x = FloatField()
    freq_x = FloatField()
    amp_y = FloatField()
    freq_y = FloatField()
    amp_z = FloatField()
    freq_z = FloatField()

    # accelerometer_sensor fields
    acc_x = ArrayField(FloatField)
    acc_y = ArrayField(FloatField)
    acc_z = ArrayField(FloatField)
    rgyr_x = ArrayField(FloatField)
    rgyr_y = ArrayField(FloatField)
    rgyr_z = ArrayField(FloatField)

    class Meta:
        primary_key = CompositeKey('device_id', 'saved_timestamp')
        constraints = [SQL('FOREIGN KEY (device_id, device_mac) ' +
                           'REFERENCES device(id, mac)')]


class Configuration(BaseModel):
    """Representación de la configuración de comunicación."""
    body_protocol_id = IntegerField()
    transport_layer_id = ForeignKeyField(TransportLayer, field='id')
    one_row_only_uidx = BooleanField(
        unique=True,
        default=True,
        constraints=[Check('one_row_only_uidx = TRUE')])

    class Meta:
        primary_key = CompositeKey('body_protocol_id', 'transport_layer_id')


MODELS = (
    Device,
    TransportLayer,
    LogEntry,
    Datum,
    Configuration,
)


def initialize_tables(database):
    """Inicializa las tablas del modelo de datos."""
    if len(database.get_tables()) == 0:
        database.create_tables([
            Device
        ], safe=True)
        database.create_tables([
            TransportLayer,
            LogEntry,
            Datum,
            Configuration,
        ], safe=True)

        # Llena con valores iniciales
        TransportLayer.create(id=TransportLayerValue.TCP, name='TCP')
        TransportLayer.create(id=TransportLayerValue.UDP, name='UDP')

        Configuration.create(body_protocol_id=0,
                             transport_layer_id=TransportLayerValue.TCP)


# Crea y llena tablas si no existen
initialize_tables(db)
