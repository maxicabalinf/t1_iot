"""Definición de modelos de datos."""
from peewee import Model, PostgresqlDatabase, IntegerField, TextField, \
    TimestampField, ForeignKeyField, TimeField

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'database': 'db'
}
db = PostgresqlDatabase(**db_config)


class BaseModel(Model):
    """Definición de un modelo"""
    class Meta:
        #pylint: disable
        database = db


class TransportLayer(BaseModel):
    """Representación de los valores de capa de transporte."""
    # TODO: agregar clave primaria
    id = IntegerField()
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
    timestamp = TimestampField()
    delta_time = TimeField()
    packet_loss = IntegerField()


class Configuration(BaseModel):
    """Representación de la configuración de comunicación."""
    # TODO: asegurar única tupla
    body_protocol_id = IntegerField()
    transport_layer_id = ForeignKeyField(TransportLayer, to_field='id')

# Ahora puedes definir tus modelos específicos heredando de BaseBaseModel
# y db estará conectado al servicio de PostgreSQL cuando realices operaciones de base de datos.


# Ver la documentación de peewee para más información, es super parecido a Django
