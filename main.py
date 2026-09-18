import argparse
import sys
import time
import urllib.request

# Стабильный файл 10 МБ от Cloudflare CDN (быстрый, без капч и строгих лимитов)
DEFAULT_TEST_URL = "https://speed.cloudflare.com/__down?bytes=10485760"


def measure_speed(url: str, attempts: int = 10) -> None:
    print(f"Целевой URL: {url}")
    print(f"Количество запросов: {attempts}\n")

    durations: list[float] = []
    total_bytes = 0

    # Полноценный браузерный заголовок, чтобы CDN не реджектил скрипт
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
    }

    for i in range(1, attempts + 1):
        # Добавляем антикэш-параметр в URL, чтобы не мерить скорость кэша провайдера
        separator = "&" if "?" in url else "?"
        cache_buster_url = f"{url}{separator}_nocache={time.time_ns()}"

        req = urllib.request.Request(cache_buster_url, headers=headers)
        start_time = time.perf_counter()

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
                elapsed = time.perf_counter() - start_time

                size = len(content)
                durations.append(elapsed)
                total_bytes += size

                speed_mb_s = (size / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                speed_mbits_s = speed_mb_s * 8

                print(
                    f"[{i:02d}/{attempts:02d}] "
                    f"Размер: {size / (1024 * 1024):.2f} МБ | "
                    f"Время: {elapsed:.3f} с | "
                    f"Скорость: {speed_mb_s:.2f} МБ/с ({speed_mbits_s:.1f} Мбит/с)"
                )
        except Exception as e:
            print(f"[{i:02d}/{attempts:02d}] Ошибка: {e}", file=sys.stderr)

    if not durations:
        print("\nНе удалось завершить ни одного запроса.", file=sys.stderr)
        sys.exit(1)

    successful_runs = len(durations)
    total_duration = sum(durations)
    avg_duration = total_duration / successful_runs

    total_megabytes = total_bytes / (1024 * 1024)
    avg_speed_mbytes_s = total_megabytes / total_duration if total_duration > 0 else 0
    avg_speed_mbits_s = avg_speed_mbytes_s * 8

    print("\n" + "=" * 48)
    print("ИТОГИ ТЕСТА")
    print("=" * 48)
    print(f"Успешных запросов:     {successful_runs}/{attempts}")
    print(f"Всего скачано:        {total_megabytes:.2f} МБ")
    print(f"Среднее время ответа: {avg_duration:.3f} с")
    print(f"Средняя скорость:     {avg_speed_mbytes_s:.2f} МБ/с ({avg_speed_mbits_s:.2f} Мбит/с)")
    print("=" * 48)


def main():
    parser = argparse.ArgumentParser(
        description="Замер скорости интернет-соединения через последовательную загрузку файла."
    )
    parser.add_argument(
        "-u",
        "--url",
        default=DEFAULT_TEST_URL,
        help="URL файла/изображения для теста (по умолчанию: 10 МБ с Cloudflare Speedtest)",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=10,
        help="Количество запросов (по умолчанию: 10)",
    )

    args = parser.parse_args()
    measure_speed(args.url, args.count)


if __name__ == "__main__":
    main()