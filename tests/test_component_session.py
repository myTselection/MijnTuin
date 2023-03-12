import unittest
import requests
import logging
import json
import sys
sys.path.append('../custom_components/MijnTuin/')

from utils import ComponentSession
from secret import USERNAME, PASSWORD

_LOGGER = logging.getLogger(__name__)



# pip install homeassistant
# run this test on command line with: python -m unittest test_component_session

logging.basicConfig(level=logging.DEBUG)

class TestComponentSession(unittest.TestCase):
    def setUp(self):
        self.session = ComponentSession()

    def test_login(self):
        # Test successful login
        self.session.login(USERNAME, PASSWORD)
        _LOGGER.debug(f"self.session.calendarlink {self.session.calendarlink}")
        self.assertIsNotNone(self.session.calendarlink)
        
                
        # Test login failure
        self.session = ComponentSession()
        try:
            self.session.s = requests.Session() # reset session object
            self.assertEqual(self.session.userdetails,{})
        except AssertionError:
            self.assertEqual(self.session.userdetails,{})
if __name__ == '__main__':
    unittest.main()