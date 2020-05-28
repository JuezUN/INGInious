class AnalyticsCollectionManagerSingleton:
    """ This Singleton class manages the DBs analytics collection. """

    __instance = None

    @staticmethod
    def get_instance(db=None):
        """ Static access method. """
        if not AnalyticsCollectionManagerSingleton.__instance:
            AnalyticsCollectionManagerSingleton(db)
        return AnalyticsCollectionManagerSingleton.__instance

    def __init__(self, database):
        """ Virtually private constructor. """
        if AnalyticsCollectionManagerSingleton.__instance:
            raise Exception("This class is a singleton!")
        else:
            self.db = database
            AnalyticsCollectionManagerSingleton.__instance = self

    def add_visit(self, service, username, date, session_id):
        """ Adds record of visit to a service """
        return self.db.analytics.insert({'username': username,
                                         'service': service["key"],
                                         'date': date,
                                         'session_id': session_id})

    def check_record(self, record_id):
        return self.db.analytics.find_one({'_id': record_id})

    def check_user_records(self, username):
        return self.db.analytics.find({'username': username})

    def _reset_records(self):
        self.db.analytics.drop()
