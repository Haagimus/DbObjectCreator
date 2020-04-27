import unittest
from time import time

from main import test_sqlalchemy_core


class QuerySpeedTest(unittest.TestCase):
    # result count : time restriction
    count = [{'count': '5', 'time': 0.5},
             {'count': '50', 'time': 0.5},
             {'count': '500', 'time': 0.75},
             {'count': '5000', 'time': 2.0},
             {'count': '50000', 'time': 10.0},
             {'count': '500000', 'time': 30.0}]

    def test_query(self):
        for i in self.count:
            result = test_sqlalchemy_core(i['count'])[1]
            self.assertTrue(result < i['time'], f'Actual time reported from method: {result}')


if __name__ == '__main__':
    unittest.main()
