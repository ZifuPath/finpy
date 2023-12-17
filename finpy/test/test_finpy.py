import unittest
from finpy import FINPY

class TestFINPY(unittest.TestCase):

    def setUp(self):
        # Setup code that runs before each test method
        self.finpy = FINPY()

    def tearDown(self):
        # Teardown code that runs after each test method
        pass

    def test_generate_session(self):
        session = self.finpy.generate_session()
        self.assertIsNotNone(session)

    def test_modify_symbol(self):
        modified_symbol = self.finpy.modify_symbol('&AAPL')
        self.assertEqual(modified_symbol, '%26AAPL')

    # Add more test methods for other functions in FINPY class

if __name__ == '__main__':
    unittest.main()
