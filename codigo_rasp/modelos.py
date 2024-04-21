"""Definición de modelos de datos."""
from peewee import Model, PostgresqlDatabase, IntegerField, TextField, \
    TimestampField, ForeignKeyField, TimeField, FloatField
from playhouse.postgres_ext import ArrayField

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'database': 'iot_db'
}
db = PostgresqlDatabase(**db_config)


class BaseModel(Model):
    """Definición de un modelo"""
    class Meta:
        database = db


class TransportLayer(BaseModel):
    """Representación de los valores de capa de transporte."""
    # TODO: agregar clave primaria
    id = IntegerField(primary_key=True, unique=True)
    name = TextField()


class Device(BaseModel):
    """Representación de un dispositivo."""
    # TODO: agregar clave primaria
    id = IntegerField()
    mac = TextField()  # TODO: verificar tipo de datos correcto.


class LogEntry(BaseModel):
    """BaseModelo de datos para los logs."""
    # TODO: agregar clave primaria
    device_id = IntegerField()
    transport_layer_id = ForeignKeyField(TransportLayer, to_field='id')
    timestamp = TimestampField()


class Datum(BaseModel):
    """Representación de un dato guardado."""
    # TODO: agregar clave primaria
    device_id = ForeignKeyField(Device, to_field='id')
    device_mac = ForeignKeyField(Device, to_field='mac')
    save_timestamp = TimestampField()
    delta_time = TimeField()
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


class Configuration(BaseModel):
    """Representación de la configuración de comunicación."""
    # TODO: asegurar única tupla
    body_protocol_id = IntegerField()
    transport_layer_id = ForeignKeyField(TransportLayer, to_field='id')


db.create_tables([TransportLayer,
                  Device,
                  LogEntry,
                  Datum,
                  Configuration,
                  ])
# Ahora puedes definir tus modelos específicos heredando de BaseBaseModel
# y db estará conectado al servicio de PostgreSQL cuando realices operaciones de base de datos.


# Ver la documentación de peewee para más información, es super parecido a Django
