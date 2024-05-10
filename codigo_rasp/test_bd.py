"""Tests"""

import unittest
from server import get_cfg, build_headers
from modelos import MODELS, initialize_tables, TransportLayerValue
import pytest
from peewee import PostgresqlDatabase
from packet_parser import unpack


test_db_config = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'database': 'test'
}


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.test_db = PostgresqlDatabase(**test_db_config)

        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        self.test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        self.test_db.connect()
        initialize_tables(self.test_db)
        # self.test_db.create_tables(MODELS)

    def tearDown(self):
        # Not strictly necessary since SQLite in-memory databases only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        self.test_db.drop_tables(MODELS, cascade=True)

        # Close connection to db.
        self.test_db.close()

        # If we wanted, we could re-bind the models to their original
        # database here. But for tests this is probably not necessary


class TestDataBase(BaseTestCase):
    def test_get_cfg(self):
        """Verifica configuración inicial"""
        res = get_cfg()
        assert res['transport_layer_id'] == 0 and res['body_protocol_id'] == 0

    def test_unpacking(self):
        """Verifica desempaquetado de paquetes."""
        mock_data = (
            b'\x02\x00' +                   # ID msg = 2
            b'\xab\xc8\x39\xbf\x87\x9d' +   # mac
            b'\x00' +                       # Transport layer TCP
            b'\x03' +                       # ID protocol = 3
            b'\x37\x00' +                   # Length = 55
            b'\x63' +                       # batt_level = 99
            b'\x41\x01\x3D\x66' +           # timestamp = 1715274049
            b'\x0A' +                       # temp = 10
            b'\x0A\x00\x00\x00' +           # pres = 10
            b'\x0A' +                       # hum = 10
            b'\x00\x00\x20\x41' +           # co = 10
            b'\x00\x00\x48\xc3' +           # rms = -200
            b'\x00\x00\x49\xc3' +           # amp_x = -201
            b'\x00\x00\x4a\xc3' +           # freq_x = -202
            b'\x00\x00\x4b\xc3' +           # amp_y = -203
            b'\x00\x00\x4c\xc3' +           # freq_y = -204
            b'\x00\x00\x4d\xc3' +           # amp_z = -205
            b'\x00\x00\x4e\xc3' +           # freq_z = -206
            b''
        )
        (_, new_datum, new_log_entry) = unpack(mock_data)
        new_log_entry.transport_layer_id = TransportLayerValue.TCP
        new_datum.save(force_insert=True)
        new_log_entry.save(force_insert=True)

        assert new_datum.device_id is not None
        assert new_datum.device_mac == 'abc839bf879d'
        assert new_datum.saved_timestamp is not None
        assert new_datum.delta_time is not None
        assert new_datum.packet_loss == 0
        assert new_datum.batt_level == 99
        assert new_datum.msg_timestamp == 1715274049
        assert new_datum.temp == 10
        assert new_datum.hum == 10
        assert new_datum.pres == 10
        assert new_datum.co == 10
        assert new_datum.rms == -200
        assert new_datum.amp_x == -201
        assert new_datum.freq_x == -202
        assert new_datum.amp_y == -203
        assert new_datum.freq_y == -204
        assert new_datum.amp_z == -205
        assert new_datum.freq_z == -206
        assert new_datum.acc_x is None
        assert new_datum.acc_y is None
        assert new_datum.acc_z is None
        assert new_datum.rgyr_x is None
        assert new_datum.rgyr_y is None
        assert new_datum.rgyr_z is None


def test_header_building():
    mock_data = (0, 'abc839bf879d', 1, 4, 7)
    bytes_res = build_headers(*mock_data)
    expected = (
        b'\x00\x00' +  # ID msg
        b'\xab\xc8\x39\xbf\x87\x9d' +  # mac
        b'\x01' +  # Transport layer
        b'\x04' +  # ID protocol
        b'\x07\x00'
    )
    assert bytes_res == expected
