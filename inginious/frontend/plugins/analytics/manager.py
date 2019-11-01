

class AnalyticsManager:
    """ This class Manages the DBs analytics collection. """

    def __init__(self, database):
        self.db = database

    def add_visit(self, service, username, date, session_id):
        """ Adds record of visit to a service """
        return self.db.analytics.insert({'username': username, 
                                'service' : service,
                                'date' : date,
                                'session_id' : session_id })


    def check_record(self, id):
        return self.db.analytics.find_one({'_id': id})

    def check_user_records(self, username):
        return self.db.analytics.find({'username' : username})

    def _reset_records(self):
        self.db.analytics.drop()

    
