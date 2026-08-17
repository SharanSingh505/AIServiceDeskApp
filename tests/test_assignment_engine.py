import unittest

from assignment_engine import recommend
from sample_data import ENGINEERS, TICKETS


class AssignmentEngineTests(unittest.TestCase):
    def test_vpn_ticket_recommends_a_vpn_engineer(self):
        result = recommend(TICKETS[0], ENGINEERS)
        self.assertEqual(result["recommendation"]["engineer_name"], "Jordan Lee")
        self.assertTrue(result["recommendation"]["likely_to_meet_sla"])

    def test_no_engineers_raises_clear_error(self):
        with self.assertRaises(ValueError):
            recommend(TICKETS[0], [])


if __name__ == "__main__":
    unittest.main()
