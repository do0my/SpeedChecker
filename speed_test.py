import argparse
import sys
import time
import urllib.error
import urllib.request


def run_benchmark(url: str, iterations: int = 10, timeout: int = 30) -> None:
    total_bytes = 0
    total_time = 0.0

    # Заголовок User-Agent, чтобы некоторые серверы не блокировали запрос как бота
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; SpeedCheckScript/1.0)",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    print(f"Запуск теста для: {url}")
    print(f"Количество последовательных запросов: {iterations}\n")

    for i in range(1, iterations + 1):
        req = urllib.request.Request(url, headers=headers)
        start_time = time.perf_counter()
        request_bytes = 0

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                # Читаем ответ чанками по 64 КБ до полного завершения загрузки
                while chunk := response.read(65536):
                    request_bytes += len(chunk)
        except urllib.error.HTTPError as e:
            print(f"\n[Ошибка] Запрос #{i} завершился со статусом HTTP {e.code}: {e.reason}")
            sys.exit(1)
        except urllib.error.URLError as e:
            print(f"\n[Ошибка] Не удалось выполнить запрос #{i}: {e.reason}")
            sys.exit(1)
        except TimeoutError:
            print(f"\n[Ошибка] Превышено время ожидания ({timeout} сек) на запросе #{i}")
            sys.exit(1)

        elapsed = time.perf_counter() - start_time
        total_bytes += request_bytes
        total_time += elapsed

        print(f"Запрос {i:2d}/{iterations}: {request_bytes / (1024 * 1024):.2f} МБ за {elapsed:.3f} сек")

    avg_time = total_time / iterations
    total_mb = total_bytes / (1024 * 1024)
    # Скорость в мегабайтах в секунду (МБ/с) и мегабитах в секунду (Мбит/с)
    speed_mb_s = total_mb / total_time if total_time > 0 else 0.0
    speed_mbps = (total_bytes * 8) / (total_time * 1_000_000) if total_time > 0 else 0.0

    print("\n" + "=" * 45)
    print(f"Всего скачано:         {total_mb:.2f} МБ ({total_bytes} байт)")
    print(f"Общее время:           {total_time:.3f} сек")
    print(f"Среднее время запроса: {avg_time:.3f} сек")
    print(f"Средняя скорость:      {speed_mb_s:.2f} МБ/с ({speed_mbps:.2f} Мбит/с)")
    print("=" * 45)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Скрипт для замера скорости скачивания по HTTP/HTTPS."
    )
    parser.add_argument("url", help="URL ресурса для скачивания (например, прямой адрес картинки)")
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=10,
        help="Количество последовательных запросов (по умолчанию: 10)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=30,
        help="Таймаут одного запроса в секундах (по умолчанию: 30)",
    )

    args = parser.parse_args()
    run_benchmark(url=args.url, iterations=args.count, timeout=args.timeout)


if __name__ == "__main__":
    main()
