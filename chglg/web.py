import os
import json

from aiohttp import web
import aiohttp_jinja2
import jinja2
import aiohttp_cors

from chglg.db import Database


db = Database()
routes = web.RouteTableDef()
HERE = os.path.dirname(__file__)
STATIC = os.path.join(HERE, "static")


def add_context(webview):
    async def _add_context(request):
        res = await webview(request)
        path = request.rel_url.path
        if path == "/":
            url = "/json"
        else:
            url = path + "/json"
        if request.rel_url.raw_query_string:
            url += "?" + request.rel_url.raw_query_string
        # fragment... XXX
        res["json_url"] = url
        return res

    return _add_context


@routes.get("/watchlist")
@aiohttp_jinja2.template("watchlist.html")
@add_context
async def watchlist(request):
    with open(os.path.join(HERE, "repositories.json")) as f:
        config = json.loads(f.read())
    return config


@routes.get("/watchlist/json")
async def watchlist_json(request):
    with open(os.path.join(HERE, "repositories.json")) as f:
        config = json.loads(f.read())
    return web.json_response(config)


@routes.get("/")
@aiohttp_jinja2.template("index.html")
@add_context
async def index(request):
    return {"changelog": db.get_changelog(**dict(request.query))}


@routes.get(r"/change/{id}")
@aiohttp_jinja2.template("change.html")
@add_context
async def change(request):
    try:
        change_id = int(request.match_info["id"])
    except ValueError:
        change_id = request.match_info["id"]
    return {"change": db.get_change(change_id)}


@routes.get(r"/change/{id}/json")
async def change_json(request):
    try:
        change_id = int(request.match_info["id"])
    except ValueError:
        change_id = request.match_info["id"]
    return web.json_response({"change": db.get_change(change_id)})


@routes.get("/json")
async def json_index(request):
    data = {"changelog": list(db.get_changelog(**dict(request.query)))}
    return web.json_response(data)


CORS_DEFAULTS = {
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True, expose_headers="*", allow_headers="*"
    )
}


def make_app():
    app = web.Application()
    app.add_routes(routes)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(HERE))
    app.add_routes([web.static("/static", STATIC)])
    cors = aiohttp_cors.setup(app, defaults=CORS_DEFAULTS)
    for route in list(app.router.routes()):
        cors.add(route)
    return app


if __name__ == "__main__":
    web.run_app(make_app(), port=8080)
