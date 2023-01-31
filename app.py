import falcon
from bankdb import bankdb

app = falcon.App()
app.add_route("/account", bankdb())
