class DataException(Exception):
    pass


class DataNotFoundException(DataException):
    pass


class DataPermissionDeniedException(DataException):
    pass

class DataParserErrorException(DataException):
    pass
