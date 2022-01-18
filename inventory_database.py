class inventory_database:
    """ A temporary database used to keep track of inventory """

    uid_list = set()  # Keeps a list of uid for quick indexing
    data = {}  # Format: {uid: [name, count, single unit value, total value, category]}
    current_value = 0  # Keeps track of total value of current inventory
    category_info = {}  # Keeps track of all current categories their associated UIDs. eg: {"FOOD_ITEMS": [uid1, uid2]}

    def __init__(self):
        print("connected to database")

    def add_inventory(self, name: str, uid: str, count: int, single_unit_value: float, total_value: float,
                      category: str):
        """ Adds new inventory to the database of items

        :param (str) name: Item name
        :param (str) uid: Unique ID of item
        :param (int) count: Amount of items in stock
        :param (float) single_unit_value: Value of a single item, eg: 899 for macbook air
        :param (float) total_value: Value of all the units of a given item, ie. count * single_unit_value
        :param (str) category: group of the item, defaults to "UNCATEGORIZED"
        """

        if uid not in self.data:
            self.uid_list.add(uid)  # Adds to a quick index
            if category:
                self.data[uid] = [name, count, single_unit_value, total_value, category]
                if category in self.category_info:
                    self.category_info[category].append(uid)
                else:
                    self.category_info[category] = [uid]
            else:
                # Uncategorized items are all considered to be of the same category, "UNCATEGORIZED"
                if "UNCATEGORIZED" in self.category_info:
                    self.category_info["UNCATEGORIZED"].append(uid)
                else:
                    self.category_info["UNCATEGORIZED"] = [uid]
                self.data[uid] = [name, count, single_unit_value, total_value, "UNCATEGORIZED"]
            self.current_value += self.data[uid][3]  # Updated total value of ALL inventory
            print("added something new to the database")
        else:
            print("something with this uid already exists in the db")

    def return_dict_from_uid(self, uid: str) -> list:
        """ Gets all the info of an item from its UID, and returns it in tornado readable format

        :param (str) uid: Unique ID of item
        :return: (list) Item data in the format [name, count, value/item, total_value, uid, category]
        """

        return [
            self.data[uid][0],  # Name of object
            str(self.data[uid][1]),  # Count of stock
            str(self.data[uid][2]),  # Value of a single item
            str(self.data[uid][3]),  # Total value
            uid,  # Unique ID of the object
            str(self.data[uid][4])  # Category of item
        ]

    def get_current_inventory(self):
        """ Goes through all current categories to compile list of all items in the inventory

        :return: (list) Inventory items in order of groups
        """

        return_data = []
        for category in self.category_info:
            for uid in self.category_info[category]:
                # Returns the current inventory, with categories "grouped" together
                print("UID IS: ", uid)
                item_info = self.return_dict_from_uid(uid)
                return_data.append(item_info)
        return return_data

    def get_current_categories(self) -> list:
        """ Converts the keys of the category_info dict to tornado readable format

        :return: (list) All current categories
        """

        categories = [*self.category_info]
        return categories

    def get_category_items(self, category: str) -> list:
        """ Gets all the items associated with a given category

        :param (str) category: Category whose items you want to access
        :return: (list) Inventory items in of the param group
        """

        return_data = []
        category = category
        for uid in self.category_info[category]:
            item_info = self.return_dict_from_uid(uid)
            return_data.append(item_info)
        return return_data

    def delete_inventory(self, uid: str):
        """ Permanently deletes an inventory item

        :param (str) uid: Unique ID for the item that is to be deleted
        """

        if uid in self.uid_list:
            self.current_value -= self.data[uid][3]
            category = self.data[uid][4]
            self.category_info[category].remove(uid)
            del self.data[uid]
            self.uid_list.discard(uid)
            print(f"removed {uid}")
        else:
            print("UID does not exist in db")

    def update_inventory(self, uid, new_name, new_count, new_price, new_category):
        """ Updates a specifc inventory item to new user specs

        :param (str) uid: Unique ID of item to update
        :param (str) new_name: Updated name of item
        :param (int) new_count: Updated count
        :param (float) new_price: Updated stock
        :param (str) new_category: Updated category
        """

        if uid not in self.uid_list:
            print("UID does not exist in db")
        else:
            self.current_value -= self.data[uid][3]  # Accounts for the change in total value change
            if new_name:
                self.data[uid][0] = new_name
            if new_count:
                self.data[uid][1] = int(new_count)
            if new_price:
                self.data[uid][2] = float(new_price)
            if new_category:
                prev_category = self.data[uid][4]
                self.data[uid][4] = str(new_category).upper()
                # Updates category_info to account for the new category assignment
                self.category_info[prev_category].remove(uid)
                if len(self.category_info[prev_category]) < 1:  # Gets rid of categories no longer in use
                    del self.category_info[prev_category]
                if new_category in self.category_info:
                    self.category_info[new_category].append(uid)
                else:
                    self.category_info[new_category] = [uid]

            self.data[uid][3] = round(self.data[uid][1] * self.data[uid][2], 2)
            self.current_value += self.data[uid][3]  # Updates the total value with new price
            print("inventory updated")

    def get_total_inventory_value(self):
        """This is not implemented in the UI,
        but this can be used to keep track of the total value of ALL inventory"""

        return self.current_value
