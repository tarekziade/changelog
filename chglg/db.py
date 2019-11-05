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
        if self.changes.search(Change.id == change["id"]):
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
        changes = []
        for line in self.changes:
            d = datetime.datetime.strptime(line["date"], "%Y-%m-%dT%H:%M:%SZ")
            line["real_date"] = d
            line["date_str"] = humanize.naturalday(d)
            changes.append(line)
        changes.sort(key=lambda c: c["real_date"])
        return reversed(changes)
