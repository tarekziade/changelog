""" Collector, grabs changes in various sources and put them in a DB.
"""
import github3
import json
import os

from chglg.db import Database


CFG = os.path.join(os.path.dirname(__file__), "repositories.json")

with open(CFG) as f:
    CFG = json.loads(f.read())


def filter_out(filters, message):
    for filter in filters:
        if filter(message):
            return False
    return True


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

    def get_changes(self, user, repository, **kw):
        repo = self.gh.repository(user, repository)
        filters = kw.get("filters")

        for release in repo.releases(number=kw.get("number", 25)):
            release = json.loads(release.as_json())
            name = release["name"] or release["tag_name"]
            yield {
                "date": release["published_at"],
                "author": release["author"]["login"],
                "message": "Released " + name,
                "id": release["id"],
                "type": "release",
            }

        for commit in repo.commits(number=kw.get("number", 25)):
            commit = json.loads(commit.as_json())
            message = commit["commit"]["message"]
            message = message.split("\n")[0]
            res = {
                "date": commit["commit"]["author"]["date"],
                "author": commit["commit"]["author"]["name"],
                "message": message,
                "id": commit["sha"],
                "type": "commit",
            }
            if filter_out(filters, res):
                continue
            yield res


def deployment(change):
    message = change["message"]
    return "*PRODUCTION*" in message or "*STAGING*" in message


def only_releases(change):
    return change["type"] == "release"


def remove_auto_commits(change):
    message = change["message"]
    start_text = ("Scheduled weekly dependency update",
                  "Merge pull request")
    return not message.startswith(start_text)

readers = {"github": GitHub()}
filters = {"deployment": deployment, "only_releases": only_releases,
           "remove_auto_commits":remove_auto_commits}


def main():
    db = Database()
    for repo_info in CFG["repositories"]:
        source = dict(repo_info["source"])
        reader = readers.get(source["type"])
        if not reader:
            raise NotImplementedError(source["type"])
        source["filters"] = [filters[name] for name in source["filters"]]

        for change in reader.get_changes(**source):
            change.update(repo_info["metadata"])  # XXX duplicated for now
            if db.add_change(change):
                print("%(date)s - %(message)s [%(author)s]" % change)


if __name__ == "__main__":
    main()
