class SlackURLError(ValueError):
    def __init__(self, message, *args):
        super(SlackURLError, self).__init__(message, *args)
