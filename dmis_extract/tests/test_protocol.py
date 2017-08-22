from django.test.testcases import TestCase
from dmis_extract.protocol_data import ProtocolData


class TestProtocol(TestCase):

    def test_protocols(self):
        db = ProtocolData(database='BHPLAB')
        db.protocols

    def test_data_dictionaries(self):
        db = ProtocolData(database='BHPLAB')
        db.data_dictionaries

    def test_get_data_dictionary(self):
        db = ProtocolData(database='BHPLAB')
        db.get_data_dictionary(form_id='LB232')
