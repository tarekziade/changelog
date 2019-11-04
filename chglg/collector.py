""" Collector, grabs changes in various sources and put them in a DB.
"""
import github3
import json
import os

from chglg.db import Database


CFG = os.path.join(os.path.dirname(__file__), "repositories.json")

with open(CFG) as f:
    CFG = json.loads(f.read())


class GitHub:
    def __init__(self):
        self.token = os.environ["GITHUB_TOKEN"]
        self.id = os.environ["GITHUB_ID"]
        self.gh = github3.login(token=self.token, two_factor_callback=self._2FA)

    def _2FA(self):
        code = ""
        while not code:
            # The user could accidentally press Enter before being ready,
            # let's protect them from doing that.
            code = input("Enter 2FA code: ")
        return code

    def get_commits(self, user, repository, **kw):
        repo = self.gh.repository(user, repository)
        filters = kw.get("filters")

        def filter_out(message):
            for filter in filters:
                if filter(message):
                    return False
            return True

        for commit in repo.commits(number=kw.get("number", 25)):
            commit = json.loads(commit.as_json())
            message = commit["commit"]["message"]
            if filter_out(message):
                continue
            message = message.split("\n")[0]
            yield {
                "date": commit["commit"]["author"]["date"],
                "author": commit["commit"]["author"]["name"],
                "message": message,
                "sha": commit["sha"],
            }


def deployment(message):
    return "*PRODUCTION*" in message or "*STAGING*" in message


readers = {"github": GitHub()}
filters = {"deployment": deployment}


def main():
    db = Database()
    for repo_info in CFG["repositories"]:
        source = dict(repo_info["source"])
        reader = readers.get(source["type"])
        if not reader:
            raise NotImplementedError(source["type"])
        source["filters"] = [filters[name] for name in source["filters"]]

        for commit in reader.get_commits(**source):
            commit.update(repo_info["metadata"])  # XXX duplicated for now
            if db.add_change(commit):
                print("%(date)s - %(message)s [%(author)s]" % commit)


if __name__ == "__main__":
    main()
