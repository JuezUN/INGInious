class SlackURLError(ValueError):
    """ Error getting main slack url """
    def __init__(self, message, *args):
        super().__init__(message, *args)
