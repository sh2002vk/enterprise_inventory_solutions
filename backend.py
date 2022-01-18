import uuid
from abc import ABC

import inventory_database
import tornado.web
import tornado.httpserver

connection = inventory_database.inventory_database()
web = tornado.web
handler = web.RequestHandler


class MainHandler(handler, ABC):
    def get(self):
        items = connection.get_current_inventory()
        curr_val = round(float(connection.get_total_inventory_value()), 2)
        print("CURR VAL", curr_val)
        self.render("inventory.html", total_value=curr_val, items=items)


class NewInventory(handler, ABC):
    def get(self):
        curr_categories = connection.get_current_categories()
        self.render("add_inventory.html", categories=curr_categories)


class AddToDB(handler, ABC):
    def get(self):
        uid = str(uuid.uuid1())
        name = self.get_argument("item-name")
        count = int(self.get_argument("item-count"))
        single_unit_value = float(self.get_argument("item-cost"))
        category = str(self.get_argument("item-category")).upper()
        total_value = round(count * single_unit_value, 2)
        connection.add_inventory(
            name=name,
            uid=uid,
            count=count,
            single_unit_value=single_unit_value,
            total_value=total_value,
            category=category
        )
        self.redirect("/")


class DeleteStock(handler):
    def get(self):
        uid = str(self.get_argument("deletion-uid"))
        connection.delete_inventory(uid=uid)
        self.redirect("/")


class UpdateStock(handler):
    def get(self):
        uid = self.get_argument("update-uid")
        name = self.get_argument("update-name")
        count = self.get_argument("update-stock")
        price = self.get_argument("update-cost")
        category = self.get_argument("update-category")
        connection.update_inventory(uid=uid, new_name=name, new_count=count, new_price=price, new_category=category)
        self.redirect("/")


class EditPage(handler, ABC):
    def get(self):
        self.render("edit_inventory.html")


class PageNotFound(handler, ABC):
    def prepare(self):
        self.write("404 NOT FOUND ERROR")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/add", NewInventory),
        (r"/add_info", AddToDB),
        (r"/edit", EditPage),
        (r"/delete_stock", DeleteStock),
        (r"/update_stock", UpdateStock),
    ], default_handler_class=PageNotFound, debug=True)


if __name__ == "__main__":
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(5000)
    tornado.ioloop.IOLoop.instance().start()
