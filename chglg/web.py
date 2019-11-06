import os

from aiohttp import web
import aiohttp_jinja2
import jinja2

from chglg.db import Database


db = Database()
routes = web.RouteTableDef()
HERE = os.path.dirname(__file__)
STATIC = os.path.join(HERE, "static")


@routes.get("/")
@aiohttp_jinja2.template("index.html")
async def index(request):
    return {"changelog": db.get_changelog(**dict(request.query))}


@routes.get(r"/change/{id}")
@aiohttp_jinja2.template("change.html")
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


def make_app():
    app = web.Application()
    app.add_routes(routes)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(HERE))
    app.add_routes([web.static("/static", STATIC)])
    return app


if __name__ == "__main__":
    web.run_app(make_app(), port=8080)
