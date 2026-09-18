import unittest
from unittest.mock import MagicMock, patch

from main import DownloadResult, calculate_stats, fetch_chunk


class TestSpeedTest(unittest.TestCase):
    def test_calculate_stats(self):
        chunk_size = 1024 * 1024
        mock_results = [
            DownloadResult(bytes_count=chunk_size, duration=0.5),
            DownloadResult(bytes_count=chunk_size, duration=0.5),
        ]

        stats = calculate_stats(mock_results, total_attempts=2)

        self.assertEqual(stats.successful_runs, 2)
        self.assertAlmostEqual(stats.total_megabytes, 2.0)
        self.assertAlmostEqual(stats.avg_duration, 0.5)
        self.assertAlmostEqual(stats.avg_speed_mbytes_s, 2.0)
        self.assertAlmostEqual(stats.avg_speed_mbits_s, 16.0)

    def test_calculate_stats_empty(self):
        with self.assertRaises(ValueError):
            calculate_stats([], total_attempts=10)

    @patch("speedtest.urllib.request.urlopen")
    def test_fetch_chunk(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"test" * 256
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = fetch_chunk("https://example.com/test.png")

        self.assertEqual(result.bytes_count, 1024)
        self.assertGreater(result.duration, 0)
        mock_urlopen.assert_called_once()


if __name__ == "__main__":
    unittest.main()