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

    def add_visit(self, service, username, date, session_id, course_id):
        """ Adds record of visit to a service """
        return self.db.analytics.insert({'username': username,
                                         'service': service["key"],
                                         'date': date,
                                         'session_id': session_id,
                                         'course_id': course_id})

    def check_record(self, record_id):
        return self.db.analytics.find_one({'_id': record_id})

    def check_user_records(self, username):
        return self.db.analytics.find({'username': username})

    def get_course_records(self, course_id):
        return self.db.analytics.find({'course_id': course_id})

    def _reset_records(self):
        self.db.analytics.drop()

    def get_course_list(self):
        """ return a list of the courses registered in analytics """
        return self.db.analytics.distinct("course_id")

    def filter_analytics_data(self, filters):
        """ get data from DB according the filters """
        results = self.db.analytics.aggregate([
            {
                "$match": filters
            },
            {
                "$project": {
                    "username": 1,
                    "service": 1,
                    "date": 1,
                    "course_id": 1
                }
            }
        ])
        return results
