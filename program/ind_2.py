#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Для своего варианта лабораторной работы 2.16
# необходимо дополнительно реализовать интерфейс командной строки (CLI).

import argparse
import bisect
import json
import os
import sys

from dotenv import load_dotenv
from jsonschema import ValidationError, validate


def add_route(routes, start, end, count):
    """
    Добавить данные о маршруте.
    """
    route = {
        "начальный пункт": start.lower(),
        "конечный пункт": end.lower(),
        "номер маршрута": count,
    }
    if route not in routes:
        bisect.insort(
            routes,
            route,
            key=lambda item: item.get("номер маршрута"),
        )
    else:
        print("Данный маршрут уже добавлен.")
    return routes


def display_routes(routes):
    """
    Отобразить список маршрутов.
    """
    if routes:
        line = "+-{}-+-{}-+-{}-+".format("-" * 30, "-" * 20, "-" * 8)
        print(line)
        print("| {:^30} | {:^20} | {:^8} |".format("Начало", "Конец", "Номер"))
        print(line)
        for route in routes:
            print(
                "| {:<30} | {:<20} | {:>8} |".format(
                    route.get("начальный пункт", ""),
                    route.get("конечный пункт", ""),
                    route.get("номер маршрута", ""),
                )
            )
        print(line)
    else:
        print("Список маршрутов пуст.")


def select_routes(routes, name_point):
    """
    Выбрать маршруты с заданным пунктом отправления или прибытия.
    """
    selected = []
    for route in routes:
        if (
            route["начальный пункт"] == name_point
            or route["конечный пункт"] == name_point
        ):
            selected.append(route)

    return selected


def save_routes(file_name, routes):
    """
    Сохранить все маршруты в файл JSON.
    """
    # Открыть файл с заданным именем для записи.
    with open(file_name, "w") as file_out:
        # Записать данные из словаря в формат JSON и сохранить их
        # в открытый файл.
        json.dump(routes, file_out, ensure_ascii=False, indent=4)


def load_routes(file_name):
    """
    Загрузить все маршруты из файла JSON.
    """
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "начальный пункт": {"type": "string"},
                "конечный пункт": {"type": "string"},
                "номер маршрута": {"type": "integer"},
            },
            "required": [
                "начальный пункт",
                "конечный пункт",
                "номер маршрута",
            ],
        },
    }
    # Открыть файл с заданным именем и прочитать его содержимое.
    with open(file_name, "r") as file_in:
        data = json.load(file_in)  # Прочитать данные из файла

    try:
        # Валидация
        validate(instance=data, schema=schema)
        print("\033[92mJSON валиден по схеме.\033[0m")
        return data
    except ValidationError as e:
        print(f"\033[91mОшибка валидации: {e.message}\033[0m")
        return []


def main(command_line=None):
    """
    Главная функция программы.
    """
    load_dotenv()
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "-d",
        "--data",
        action="store",
        required=False,
        help="The data file name",
    )
    parser = argparse.ArgumentParser("routes")
    parser.add_argument(
        "--version", action="version", version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    add = subparsers.add_parser(
        "add", parents=[file_parser], help="Add a new route"
    )
    add.add_argument(
        "-s", "--start", action="store", required=True, help="The route start"
    )
    add.add_argument(
        "-e", "--end", action="store", required=True, help="The route endpoint"
    )
    add.add_argument(
        "-n",
        "--number",
        action="store",
        type=int,
        required=True,
        help="The number of route",
    )

    _ = subparsers.add_parser(
        "list", parents=[file_parser], help="Display all routes"
    )

    select = subparsers.add_parser(
        "select", parents=[file_parser], help="Select the routes"
    )
    select.add_argument(
        "-p",
        "--point",
        action="store",
        required=True,
        help="Routes starting or ending at this point",
    )

    args = parser.parse_args(command_line)

    data_file = args.data
    if not data_file:
        data_file = os.environ.get("WORKERS_DATA_IND_2")
    if not data_file:
        print("The data file name is absent", file=sys.stderr)
        sys.exit(1)
    # Загрузить всех работников из файла, если файл существует.
    is_dirty = False

    if os.path.exists(data_file):
        routes = load_routes(data_file)
    else:
        routes = []

    match args.command.lower():
        case "add":
            routes = add_route(routes, args.start, args.end, args.number)
            is_dirty = True

        case "list":
            display_routes(routes)

        case "select":
            name_point = args.point.lower()
            selected = select_routes(routes, name_point)
            display_routes(selected)
    if is_dirty:
        save_routes(data_file, routes)


if __name__ == "__main__":
    main()
