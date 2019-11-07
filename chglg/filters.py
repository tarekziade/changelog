import fnmatch


def deployment(change, *options):
    message = change["message"]
    if "*PRODUCTION*" in message or "*STAGING*" in message:
        change["tags"] = ["deployment"]
        return change


def only_releases(change, *options):
    if change["type"] == "release":
        return change


def remove_auto_commits(change, *options):
    message = change["message"]
    start_text = ("Scheduled weekly dependency update", "Merge pull request")
    if not message.startswith(start_text):
        return change


def filter_by_path(change, *options):
    if "files" not in change:
        return
    for file in change["files"]:
        for filter in options:
            if fnmatch.fnmatch(file, filter):
                return change


_FILTERS = {
    "deployment": deployment,
    "only_releases": only_releases,
    "remove_auto_commits": remove_auto_commits,
    "filter_by_path": filter_by_path,
}


def filter_out(filters, message):
    for filter in filters:
        if isinstance(filter, list):
            filter, options = filter[0], filter[1:]
        else:
            options = []
        message = _FILTERS[filter](message, *options)
        if message is None:
            return None
    return message
