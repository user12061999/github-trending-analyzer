import json
import unittest
from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch

from src.growth import aggregate_history, get_star_growth, _cache


class TestGrowth(unittest.TestCase):
    def setUp(self):
        _cache.clear()

    def history(self, today, count=1):
        sunday = today - timedelta(days=(today.weekday() + 1) % 7)
        return [{'week': int(datetime.combine(sunday - timedelta(weeks=i), datetime.min.time(), timezone.utc).timestamp()),
                 'days': [count] * 7} for i in range(6)]

    def test_windows_cross_week_and_month_boundaries(self):
        today = date(2026, 10, 1)
        self.assertEqual(aggregate_history(self.history(today), today), {'daily': 1, 'weekly': 7, 'monthly': 30})

    def test_zero_is_known_but_missing_history_is_unknown(self):
        today = date(2026, 10, 1)
        self.assertEqual(aggregate_history(self.history(today, 0), today)['monthly'], 0)
        counts = aggregate_history(self.history(today)[:1], today)
        self.assertEqual(counts['daily'], 1)
        self.assertIsNone(counts['weekly'])
        self.assertIsNone(counts['monthly'])

    def test_invalid_counts_and_duplicate_weeks_rejected(self):
        rows = self.history(date(2026, 10, 1))
        with self.assertRaises(ValueError): aggregate_history(rows + rows[:1], date(2026, 10, 1))
        rows[0]['days'][0] = True
        with self.assertRaises(ValueError): aggregate_history(rows, date(2026, 10, 1))

    @patch('src.growth.urllib.request.urlopen')
    def test_fetch_cached_and_failure_does_not_become_zero(self, request):
        today = datetime.now(timezone.utc).date()
        request.return_value.__enter__.return_value.read.return_value = json.dumps(self.history(today)).encode()
        self.assertEqual(get_star_growth('team', 'repo')['weekly'], 7)
        self.assertEqual(get_star_growth('team', 'repo')['weekly'], 7)
        self.assertEqual(request.call_count, 1)
        request.side_effect = OSError('offline')
        result = get_star_growth('other', 'repo')
        self.assertEqual(result['status'], 'unavailable')
        self.assertIsNone(result['daily'])


if __name__ == '__main__': unittest.main()
