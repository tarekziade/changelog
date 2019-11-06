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

    def get_change(self, change_id):
        Change = Query()
        res = self.changes.search(Change.id == change_id)
        res = len(res) == 1 and res[0] or None
        if res:
            d = datetime.datetime.strptime(res["date"], "%Y-%m-%dT%H:%M:%SZ")
            res["date_str"] = humanize.naturalday(d)
        return res

    def get_changelog(self, **filters):
        # limited set of supported filters
        def has_tag(tags, tag):
            return tag in tags

        Change = Query()
        if "tag" in filters:
            res = self.changes.search(Change.tags.test(has_tag, filters['tag']))
        else:
            res = self.changes

        changes = []
        for line in res:
            d = datetime.datetime.strptime(line["date"], "%Y-%m-%dT%H:%M:%SZ")
            line["date_str"] = humanize.naturalday(d)
            changes.append((d, line))
        changes.sort()
        return reversed([change for _, change in changes])
