import os
import datetime

import humanize
from tinydb import TinyDB, Query


DEFAULT_DB = os.path.join(os.path.dirname(__file__), "data.json")


class Database:
    def __init__(self, path=DEFAULT_DB):
        self.path = path
        self.db = TinyDB(path)

    def add_change(self, change):
        self.db.insert(change)

    def add_changes(self, changes):
        for change in changes:
            self.db.insert(change)

    def get_changelog(self):
        for line in self.db:
            date_str = datetime.datetime.strptime(line["date"], "%Y-%m-%dT%H:%M:%SZ")
            line["date_str"] = humanize.naturalday(date_str)
            yield line
