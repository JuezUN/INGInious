from collections import OrderedDict


class ServicesCollectionManagerSingleton:
    """ This Singleton class manages the services collection. """

    __instance = None

    @staticmethod
    def get_instance(db=None):
        """ Static access method. """
        if not ServicesCollectionManagerSingleton.__instance:
            ServicesCollectionManagerSingleton(db)
        return ServicesCollectionManagerSingleton.__instance

    def __init__(self, database):
        """ Virtually private constructor. """
        if ServicesCollectionManagerSingleton.__instance:
            raise Exception("This class is a singleton!")
        else:
            self.db = database
            ServicesCollectionManagerSingleton.__instance = self

    def add_service(self, service):
        """ Adds record of service to a service """
        if not self.check_record(service["key"]):
            return self.db.services.insert({'service_name': service["name"], 'service_key': service["key"]})

    def get_all_services(self):
        cursor = self.db.services.find({}, {"_id": 0, "service_name": 1, "service_key": 1})
        return OrderedDict({val["service_key"]: val["service_name"] for val in cursor})

    def check_record(self, key):
        return self.db.services.find_one({'service_key': key})

    def _reset_records(self):
        self.db.services.drop()
