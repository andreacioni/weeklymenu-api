class BaseRESTException(Exception):
    code = 500
    error = 'GENERIC'
    description = 'generic REST exception raised'
    details = []

    def __init__(self, code: int, error=None, description=None, details=None):
        self.code = code

        if error != None:
            self.error = error
        
        if description != None:
            self.description = description

        if details != None:
            self.details = details

    def __repr__(self):
        return "<RESTException: error: '{}'; description: '{}', details: '{}'".format(self.error, self.description, self.details)

class InvalidPayloadSupplied(BaseRESTException):

    def __init__(self, description=None, details=None):
        super().__init__(400, 'BAD_REQUEST', description, details)