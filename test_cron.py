import unittest
import datetime
from cron import check_cron


class CronTestCase(unittest.TestCase):
    def test_exact_match(self):
        dt = datetime.datetime(2025, 4, 5, 23, 46, 0)
        self.assertTrue(check_cron("46 23 5 4 *", dt))
        
        dt = datetime.datetime(2025, 4, 5, 23, 45, 0)
        self.assertFalse(check_cron("46 23 5 4 *", dt))
    
    def test_wildcard_minute(self):
        dt = datetime.datetime(2025, 4, 5, 23, 0, 0)
        self.assertTrue(check_cron("* 23 5 4 *", dt))
        
        dt = datetime.datetime(2025, 4, 5, 23, 59, 0)
        self.assertTrue(check_cron("* 23 5 4 *", dt))
        
        dt = datetime.datetime(2025, 4, 5, 22, 46, 0)
        self.assertFalse(check_cron("* 23 5 4 *", dt))
    
    def test_wildcard_hour(self):
        dt = datetime.datetime(2025, 4, 5, 0, 46, 0)
        self.assertTrue(check_cron("46 * 5 4 *", dt))
        
        dt = datetime.datetime(2025, 4, 5, 23, 46, 0)
        self.assertTrue(check_cron("46 * 5 4 *", dt))
        
        dt = datetime.datetime(2025, 4, 5, 23, 45, 0)
        self.assertFalse(check_cron("46 * 5 4 *", dt))
    
    def test_wildcard_day_of_month(self):
        dt = datetime.datetime(2025, 4, 1, 23, 46, 0)
        self.assertTrue(check_cron("46 23 * 4 *", dt))
        
        dt = datetime.datetime(2025, 4, 5, 23, 46, 0)
        self.assertTrue(check_cron("46 23 * 4 *", dt))
        
        dt = datetime.datetime(2025, 5, 5, 23, 46, 0)
        self.assertFalse(check_cron("46 23 * 4 *", dt))
    
    def test_all_wildcards(self):
        dt = datetime.datetime(2025, 4, 5, 23, 46, 0)
        self.assertTrue(check_cron("* * * * *", dt))
        
        dt = datetime.datetime(2024, 1, 1, 0, 0, 0)
        self.assertTrue(check_cron("* * * * *", dt))
        
    def test_day_of_week_strings(self):
        dt = datetime.datetime(2025, 4, 5, 23, 46, 0)
        self.assertTrue(check_cron("46 23 5 4 SAT", dt))
        self.assertTrue(check_cron("46 23 5 4 sat", dt))
        
        dt = datetime.datetime(2025, 4, 6, 23, 46, 0)  # Sunday
        self.assertFalse(check_cron("46 23 * 4 SAT", dt))
        
        dt = datetime.datetime(2025, 4, 6, 23, 46, 0)  # Sunday
        self.assertTrue(check_cron("46 23 6 4 SUN", dt))
        self.assertTrue(check_cron("46 23 6 4 sun", dt))


if __name__ == '__main__':
    unittest.main()
