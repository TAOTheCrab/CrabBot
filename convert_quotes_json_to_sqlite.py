#!/usr/bin/env python3

# Convert legacy JSON quotes format to SQLite3 format

# It non-destructively reads in "quotes.json"
# and writes out a new file "quotes.sqlite3".
# It will prompt if "quotes.sqlite3" exists
# and will ask if you want to merge the quotes.
# "quotes.sqlite3" modifications will not be committed until the process is finished,
# so don't open it in the meantime and expect new data.

import json
from pathlib import Path
import sqlite3
import sys

print("Converting quotes.json to quotes.sqlite3")

with open("quotes.json") as f:
    quotes = json.load(f)

if Path("quotes.sqlite3").exists():
    print("'quotes.sqlite3' exists. It could be from a previous run, and may have quotes in it.")
    print("You may want to check the existing file for data, or at least back it up.")
    print()
    print("Do you want to continue and attempt to merge the existing and new quotes?")
    answer = input('If you wish to merge them, type "yes" without quotes: ')
    if answer != "yes":
        print("Aborting conversion. Move, delete, or prepare to merge 'quotes.sqlite3' and rerun this script.")
        sys.exit("'quotes.sqlite3' exists")

# Should create a new file if it doesn't exist
quotes_db_connection = sqlite3.connect("quotes.sqlite3")
quotes_db_cursor = quotes_db_connection.cursor()
quotes_db_cursor.execute("CREATE TABLE IF NOT EXISTS quotes "
                         "(author text NOT NULL, quote text NOT NULL)")

for author in quotes:
    for quote in quotes[author]:
        quotes_db_cursor.execute("INSERT INTO quotes VALUES "
                                 "(?,?)", (author, quote))

quotes_db_connection.commit()
quotes_db_connection.close()

print("quotes.sqlite3 written. Should be good to go.")