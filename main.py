import argparse
import sys
import time
import urllib.request
from typing import NamedTuple

DEFAULT_TEST_URL = "https://speed.cloudflare.com/__down?bytes=10485760"


class DownloadResult(NamedTuple):
    bytes_count: int
    duration: float


class SpeedStats(NamedTuple):
    successful_runs: int
    total_bytes: int
    total_megabytes: float
    avg_duration: float
    avg_speed_mbytes_s: float
    avg_speed_mbits_s: float


def calculate_stats(results: list[DownloadResult], total_attempts: int) -> SpeedStats:
    if not results:
        raise ValueError("Results list is empty")

    successful_runs = len(results)
    total_bytes = sum(r.bytes_count for r in results)
    total_duration = sum(r.duration for r in results)

    avg_duration = total_duration / successful_runs
    total_megabytes = total_bytes / (1024 * 1024)
    avg_speed_mbytes_s = total_megabytes / total_duration if total_duration > 0 else 0.0
    avg_speed_mbits_s = avg_speed_mbytes_s * 8

    return SpeedStats(
        successful_runs=successful_runs,
        total_bytes=total_bytes,
        total_megabytes=total_megabytes,
        avg_duration=avg_duration,
        avg_speed_mbytes_s=avg_speed_mbytes_s,
        avg_speed_mbits_s=avg_speed_mbits_s,
    )


def fetch_chunk(url: str, timeout: int = 30) -> DownloadResult:
    separator = "&" if "?" in url else "?"
    cache_buster_url = f"{url}{separator}_t={time.time_ns()}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
    }

    req = urllib.request.Request(cache_buster_url, headers=headers)
    start_time = time.perf_counter()

    with urllib.request.urlopen(req, timeout=timeout) as response:
        content = response.read()
        duration = time.perf_counter() - start_time
        return DownloadResult(bytes_count=len(content), duration=duration)


def measure_speed(url: str, attempts: int = 10) -> None:
    print(f"URL: {url}")
    print(f"Attempts: {attempts}\n")

    results: list[DownloadResult] = []

    for i in range(1, attempts + 1):
        try:
            res = fetch_chunk(url)
            results.append(res)
            speed_mb_s = (res.bytes_count / (1024 * 1024)) / res.duration if res.duration > 0 else 0
            print(
                f"[{i:02d}/{attempts:02d}] "
                f"Size: {res.bytes_count / (1024 * 1024):.2f} MB | "
                f"Time: {res.duration:.3f}s | "
                f"Speed: {speed_mb_s:.2f} MB/s ({speed_mb_s * 8:.1f} Mbps)"
            )
        except Exception as e:
            print(f"[{i:02d}/{attempts:02d}] Error: {e}", file=sys.stderr)

    if not results:
        print("\nAll requests failed.", file=sys.stderr)
        sys.exit(1)

    stats = calculate_stats(results, attempts)

    print("\n" + "=" * 48)
    print("RESULTS")
    print("=" * 48)
    print(f"Success:      {stats.successful_runs}/{attempts}")
    print(f"Total downloaded: {stats.total_megabytes:.2f} MB")
    print(f"Avg latency:  {stats.avg_duration:.3f}s")
    print(f"Avg speed:    {stats.avg_speed_mbytes_s:.2f} MB/s ({stats.avg_speed_mbits_s:.2f} Mbps)")
    print("=" * 48)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", default=DEFAULT_TEST_URL)
    parser.add_argument("-c", "--count", type=int, default=10)
    args = parser.parse_args()

    measure_speed(args.url, args.count)


if __name__ == "__main__":
    main()  