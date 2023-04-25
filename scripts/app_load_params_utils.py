#!/usr/bin/env python3

from pathlib import Path
import json


def format_database(database: dict) -> str:
    database_str = json.dumps(database, indent=2, sort_keys=True)
    # Drop some newlines to compact a bit the data while still
    # making it readable.
    database_str = database_str.replace("[\n      ", "[")
    database_str = database_str.replace("{\n      ", "{")
    database_str = database_str.replace("\n    ]", "]")
    database_str = database_str.replace("\n    }", "}")
    database_str = database_str.replace("\n      ", " ")

    # Add newline at the end of file
    database_str += "\n"

    return database_str


def load_database(database_path: Path):
    database = {}
    if database_path.exists():
        with open(database_path, 'r') as f:
            database = json.load(f)
    return database


def save_database(database: dict, database_path: Path):
    database_str = format_database(database)
    with open(database_path, 'w') as f:
        f.write(database_str)
