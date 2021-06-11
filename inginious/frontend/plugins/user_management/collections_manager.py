class CollectionsManagerSingleton:
    """ This Singleton class manages the collections operations. """
    __instance = None

    @staticmethod
    def get_instance(db=None):
        """ Static access method. """
        if not CollectionsManagerSingleton.__instance:
            CollectionsManagerSingleton(db)
        return CollectionsManagerSingleton.__instance

    def __init__(self, database):
        """ Virtually private constructor. """
        if CollectionsManagerSingleton.__instance:
            raise Exception("This class is a singleton!")
        else:
            self.db = database
            CollectionsManagerSingleton.__instance = self

    def get_collections_names(self):
        """ returns a list of the collection's names """
        return self.db.list_collection_names()

    def get_all_key_names(self, collection_name):
        """ return a list with the keys that appear in a collection """
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
        """ Make an aggregation to a collection """
        collection = getattr(self.db, collection_name)
        return list(collection.aggregate(query))

    def update_collection(self, collection_name, filters, update):
        """ update one document of a collection """
        collection = getattr(self.db, collection_name)
        return collection.update_one(filters, update, upsert=False)

    def update_many_in_collection(self, collection_name, filters, update):
        """ update the documents in a collection that do match with the filters """
        collection = getattr(self.db, collection_name)
        return collection.update_many(filters, update, upsert=False)

    def insert_register_user_change(self, register):
        """ Insert a register in users_changes collection """
        return self.db.users_changes.insert(register)

    def make_find_request(self, collection_name, query=None, projection=None):
        """ Find request to a collection """
        collection = getattr(self.db, collection_name)
        return collection.find(filter=query, projection=projection)

    def make_find_one_request(self, collection_name, query=None, projection=None):
        """ find one request to a collection """
        collection = getattr(self.db, collection_name)
        return collection.find_one(filter=query, projection=projection)
