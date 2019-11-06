def deployment(change):
    message = change["message"]
    if "*PRODUCTION*" in message or "*STAGING*" in message:
        change["tags"] = ["deployment"]
        return change


def only_releases(change):
    if change["type"] == "release":
        return change


def remove_auto_commits(change):
    message = change["message"]
    start_text = ("Scheduled weekly dependency update", "Merge pull request")
    if not message.startswith(start_text):
        return change


_FILTERS = {
    "deployment": deployment,
    "only_releases": only_releases,
    "remove_auto_commits": remove_auto_commits,
}


def filter_out(filters, message):
    for filter in filters:
        message = _FILTERS[filter](message)
        if message is None:
            return None
    return message
