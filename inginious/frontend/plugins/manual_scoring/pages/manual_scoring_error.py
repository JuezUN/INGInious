class ManualScoringError(ValueError):
    """ Error with manual scoring """

    def __init__(self, message, *args):
        super().__init__(message, *args)
        self._message = message

    def get_message(self):
        """ return the message """
        return self._message
