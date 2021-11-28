class UnauthorizedException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class BusinessCalendarValidationError(Exception):
    def __init__(self, message, **kwargs):
        if kwargs:
            message = message.format(**kwargs)
        self.message = message
        super().__init__(self.message)


class NotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
