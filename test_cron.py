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
    
    def test_comma_separated_values(self):
        dt = datetime.datetime(2025, 4, 5, 23, 10, 0)
        self.assertTrue(check_cron("10,20,30 23 5 4 *", dt))
        
        dt = datetime.datetime(2025, 4, 5, 23, 15, 0)
        self.assertFalse(check_cron("10,20,30 23 5 4 *", dt))
        
        dt = datetime.datetime(2025, 4, 5, 10, 15, 0)
        self.assertTrue(check_cron("15 10,12,14 5 4 *", dt))
        
        dt = datetime.datetime(2025, 4, 3, 10, 15, 0)
        self.assertTrue(check_cron("15 10 1,3,5 4 *", dt))
        
        dt = datetime.datetime(2025, 6, 5, 10, 15, 0)
        self.assertTrue(check_cron("15 10 5 4,6,8 *", dt))
        
        dt = datetime.datetime(2025, 4, 5, 10, 15, 0)  # Saturday
        self.assertTrue(check_cron("15 10 * 4 MON,WED,SAT", dt))
    
    def test_slash_operator(self):
        dt = datetime.datetime(2025, 4, 5, 10, 0, 0)
        self.assertTrue(check_cron("*/10 10 5 4 *", dt))
        
        dt = datetime.datetime(2025, 4, 5, 10, 10, 0)
        self.assertTrue(check_cron("*/10 10 5 4 *", dt))
        
        dt = datetime.datetime(2025, 4, 5, 10, 5, 0)
        self.assertFalse(check_cron("*/10 10 5 4 *", dt))
        
        dt = datetime.datetime(2025, 4, 5, 0, 15, 0)
        self.assertTrue(check_cron("15 */6 5 4 *", dt))
        
        dt = datetime.datetime(2025, 4, 5, 6, 15, 0)
        self.assertTrue(check_cron("15 */6 5 4 *", dt))
        
        dt = datetime.datetime(2025, 4, 5, 7, 15, 0)
        self.assertFalse(check_cron("15 */6 5 4 *", dt))
    
    def test_slash_operator_day_of_month(self):
        dt = datetime.datetime(2025, 4, 5, 0, 0, 0)  # 5th day of month
        self.assertTrue(check_cron("0 0 */5 * *", dt))
        
        dt = datetime.datetime(2025, 4, 10, 0, 0, 0)  # 10th day of month
        self.assertTrue(check_cron("0 0 */5 * *", dt))
        
        dt = datetime.datetime(2025, 4, 15, 0, 0, 0)  # 15th day of month
        self.assertTrue(check_cron("0 0 */5 * *", dt))
        
        dt = datetime.datetime(2025, 4, 7, 0, 0, 0)  # 7th day of month
        self.assertFalse(check_cron("0 0 */5 * *", dt))
        
        dt = datetime.datetime(2025, 4, 5, 1, 0, 0)  # 5th day but wrong hour
        self.assertFalse(check_cron("0 0 */5 * *", dt))
    
    def test_slash_operator_month(self):
        dt = datetime.datetime(2025, 1, 1, 0, 0, 0)  # January 1st
        self.assertTrue(check_cron("0 0 1 */3 *", dt))
        
        dt = datetime.datetime(2025, 4, 1, 0, 0, 0)  # April 1st
        self.assertTrue(check_cron("0 0 1 */3 *", dt))
        
        dt = datetime.datetime(2025, 7, 1, 0, 0, 0)  # July 1st
        self.assertTrue(check_cron("0 0 1 */3 *", dt))
        
        dt = datetime.datetime(2025, 10, 1, 0, 0, 0)  # October 1st
        self.assertTrue(check_cron("0 0 1 */3 *", dt))
        
        dt = datetime.datetime(2025, 2, 1, 0, 0, 0)  # February 1st
        self.assertFalse(check_cron("0 0 1 */3 *", dt))
        
        dt = datetime.datetime(2025, 1, 2, 0, 0, 0)  # January 2nd
        self.assertFalse(check_cron("0 0 1 */3 *", dt))
        
        dt = datetime.datetime(2025, 1, 1, 1, 0, 0)  # January 1st, wrong hour
        self.assertFalse(check_cron("0 0 1 */3 *", dt))
    
    def test_invalid_formats(self):
        dt = datetime.datetime(2025, 4, 5, 10, 5, 0)
        
        with self.assertRaises(ValueError):
            check_cron("*/0 10 5 4 *", dt)  # Division by zero
            
        with self.assertRaises(ValueError):
            check_cron("*/ten 10 5 4 *", dt)  # Non-numeric divisor


if __name__ == '__main__':
    unittest.main()
