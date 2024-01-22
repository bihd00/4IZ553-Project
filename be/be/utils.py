from csv import DictReader
from pathlib import Path
from typing import Any
from ast import literal_eval


def get_osm_csv_records(path: Path | str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with open(path, encoding='utf-8') as f:
        reader = DictReader(f)
        for row in reader:
            if 'tags' in row:
                tags = literal_eval(row['tags'])
                row['tags'] = tags
            records.append(row)
    return records