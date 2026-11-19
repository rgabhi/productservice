"""Application errors have no HTTP dependency; controllers decide status codes."""


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


class Unavailable(Exception):
    pass
