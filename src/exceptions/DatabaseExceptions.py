class DatabaseError(Exception):
    pass


class ServerCreateError(DatabaseError):
    pass


class ServerDeleteError(DatabaseError):
    pass


__all__ = ["DatabaseError", "ServerCreateError", "ServerDeleteError"]
