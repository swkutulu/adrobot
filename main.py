import argparse
from time import perf_counter
from typing import Tuple, List, Final
from functools import reduce
import requests
import statistics


DEFAULT_URL: Final = 'https://speedtest.selectel.ru/10MB'


def error(output):
    print(f'\033[91m{str(output)}\033[0m')


def success(output):
    print(f'\033[92m{str(output)}\033[0m')


def warn(output):
    print(f'\033[93m{str(output)}\033[0m')


class AppError(Exception):
    pass


def _req(url: str) -> Tuple[float, int]:
    size = 0
    time_start = perf_counter()
    r = requests.get(url)
    time_res = perf_counter() - time_start
    size = len(r.content)
    if r.status_code != 200:
        raise AppError(f'Запрос завершился с ошибкой: {r.status_code}')
    return time_res, size


def main(url: str, count: int) -> None:
    size: int = 0
    times: List[float] = []
    try:
        for _ in range(count):
            time, s = _req(url)
            times.append(time)
            if s != size and size != 0:
                error(f'Размер ответа изменился: {size} -> {s}')
            size = s
        time_avg = reduce(lambda x, y: x + y, times, 0.0) / count
        # print(times, size)
        success(f"Среднее время запроса [сек]: {time_avg:.4f}")
        success(f"Средняя скорость [Мбит/с]: {8 * size / 1024 / 1024 / time_avg:.2f}")
        success(f"Джиттер [сек]: {statistics.stdev(times):.2f}")
    except AppError as e:
        error(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Замер скорости соединения с удаленным сервером")
    parser.add_argument("--url", help=f"URL для тестирования, по умолчанию: {DEFAULT_URL}")
    parser.add_argument("--count", type=int, default=10, help="Количество запросов, по умолчанию: 10")
    args = parser.parse_args()
    if args.count <= 0:
        error("Количество запросов должно быть больше 0")
        exit(1)
    if not args.url:
        warn(f"Будет использован URL по умолчанию: {DEFAULT_URL}")
    main(
        args.url if args.url else DEFAULT_URL,
        args.count
    )

'''
Написать скрипт-замерятель скорости интернета со своего компьютера.
Он должен принимать адрес, куда стучаться (какая-нибудь тяжелая картинка),
запускать последовательно 10 запросов к этому адресу,
дожидаться ответа, вычислять среднее время запроса,
объем скачанных данных и печатать в консоли скорость мб/с.
'''
