""" Collector, grabs changes in various sources and put them in a DB.
"""
import github3
import json
import os

CFG = os.path.join(os.path.dirname(__file__), "repositories.json")

with open(CFG) as f:
    CFG = json.loads(f.read())


class GitHub:
    def __init__(self):
        self.token = os.environ['GITHUB_TOKEN']
        self.id = os.environ['GITHUB_ID']
        self.gh = github3.login(token=self.token, two_factor_callback=self._2FA)

    def _2FA(self):
        code = ''
        while not code:
            # The user could accidentally press Enter before being ready,
            # let's protect them from doing that.
            code = input('Enter 2FA code: ')
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
            message = commit['commit']['message']
            if filter_out(message):
                continue
            message = message.split("\n")[0]
            yield {"date": commit['commit']['author']['date'],
                   "author": commit['commit']['author']['name'],
                   "message": message}

def deployment(message):
    return "*PRODUCTION*" in message or "*STAGING*" in message

readers = {"github": GitHub()}
filters = {"deployment": deployment}


for repo_info in CFG['repositories']:
    repo_info['filters'] = [filters[name] for name in repo_info['filters']]
    reader = readers.get(repo_info['type'])
    if not reader:
        raise NotImplementedError(repo_info['type'])

    for commit in reader.get_commits(**repo_info):
        print("%(date)s - %(message)s [%(author)s]" % commit)
