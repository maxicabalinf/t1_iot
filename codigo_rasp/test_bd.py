"""Tests"""

import unittest
from server import get_cfg, build_headers
from modelos import MODELS, initialize_tables
import pytest
from peewee import PostgresqlDatabase


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


def test_header_building():
    mock_data = (0, 'abc839bf879d', 1, 4, 7)
    bytes_res = build_headers(*mock_data)
    expected = (
        b'\x00\x00' +  # ID msg
        b'\xab\xc8\x39\xbf\x87\x9d' +  # mac
        b'\x01' +  # Transport layer
        b'\x04' +  # ID protocol
        b'\x00\x07'
    )
    assert bytes_res == expected
