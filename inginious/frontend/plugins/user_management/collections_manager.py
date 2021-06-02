class CollectionsManagerSingleton:
    __instance = None

    @staticmethod
    def get_instance(db=None):
        if not CollectionsManagerSingleton.__instance:
            CollectionsManagerSingleton(db)
        return CollectionsManagerSingleton.__instance

    def __init__(self, database):
        if CollectionsManagerSingleton.__instance:
            raise Exception("This class is a singleton!")
        else:
            self.db = database
            CollectionsManagerSingleton.__instance = self

    def get_collections_names(self):
        return self.db.list_collection_names()

    def get_all_key_names(self, collection_name):
        collection = getattr(self.db, collection_name)
        all_keys = list(collection.aggregate([
            {
                "$project": {
                    "array_of_key_value": {
                        "$objectToArray": "$$ROOT"
                    }
                }
            },
            {
                "$unwind": "$array_of_key_value"
            },
            {
                "$group": {
                    "_id": None,
                    "all_keys": {
                        "$addToSet": "$array_of_key_value.k"
                    }
                }
            },
            {
                "$project": {
                    "all_keys": 1,
                    "_id": 0
                }
            }
        ]))
        return all_keys[0]["all_keys"] if all_keys else []

    def make_aggregation(self, collection_name, query):
        collection = getattr(self.db, collection_name)
        return list(collection.aggregate(query))

    def make_update(self, collection_name, filters, update, settings):
        collection = getattr(self.db, collection_name)
        return collection.update_one(filters, update, upsert=settings["upsert"])

    def make_update_many(self, collection_name, filters, update, settings):
        collection = getattr(self.db, collection_name)
        return collection.update_many(filters, update, upsert=settings["upsert"])

    def insert_register_user_change(self, register):
        return self.db.users_changes.insert(register)

    def make_find_request(self, collection_name, query=None, projection=None):
        collection = getattr(self.db, collection_name)
        return collection.find(filter=query, projection=projection)
