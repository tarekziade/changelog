import os
import datetime

import humanize
from tinydb import TinyDB, Query


DEFAULT_DB = os.path.join(os.path.dirname(__file__), "data.json")


class Database:
    def __init__(self, path=DEFAULT_DB):
        self.path = path
        self.db = TinyDB(path)
        self.changes = self.db.table("changes")

    def add_change(self, change):
        # XXXX slow, will do better later
        Change = Query()
        if self.changes.search(Change.sha == change["sha"]):
            return False
        self.changes.insert(change)
        return True

    def add_changes(self, changes):
        added = 0
        for change in changes:
            if self.add_change(change):
                added += 1
        return added

    def get_changelog(self):
        for line in self.changes:
            date_str = datetime.datetime.strptime(line["date"], "%Y-%m-%dT%H:%M:%SZ")
            line["date_str"] = humanize.naturalday(date_str)
            yield line
