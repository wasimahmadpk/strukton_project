# -*- coding: utf-8 -*-
"""Shared file helpers used by the ABA / route-file parsers.

The skip and split rules match the original inline CSV readers so SEG/POI
parsing stays identical.
"""

import csv
import os


def read_semicolon_table(path, header_prefixes):
    """Read a Strukton route file (``;``-separated, ``#`` comments).

    ``header_prefixes`` is a string or tuple of strings. Rows that start
    with those prefixes are treated as headers (printed, not stored).
    """
    if isinstance(header_prefixes, str):
        header_prefixes = (header_prefixes,)

    rows = []
    line_count = 0
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            temp_str = "".join(row)
            if temp_str.startswith("#") or len(temp_str) == 0:
                continue
            if temp_str.startswith(header_prefixes):
                print("Column names are {}".format(", ".join(row)))
                line_count += 1
            else:
                line_count += 1
                rows.append(temp_str.split(";"))
    return rows, line_count


def write_csv(path, header, rows):
    """Write ``header`` plus ``rows`` with the original csv dialect."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", newline="") as file:
        writer = csv.writer(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)
