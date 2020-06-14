class ImmediateHttpResponse(Exception):
    """
    This exception is used to interrupt the flow of processing to immediately
    return a custom HttpResponse.
    """
    def __init__(self, response):
        self.response = response


class AccountExistError(Exception):
    """
    This exception is raised when trying to create a social account and the
    email address is associated with an USER_MODEL instance.
    """
    def __init__(self, *args, **kwargs):
        self.message = 'An account already exists with this e-mail address.'


class OAuth2Error(Exception):
    """
    This exception used for general oauth errors.
    """
    def __init__(self, message, *args, **kwargs):
        self.message = message
