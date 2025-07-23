class ServerManagerError(Exception):
    pass


class ImageNotFoundError(ServerManagerError):
    pass


class NoAvailablePortError(ServerManagerError):
    pass


class ServerAlreadyExistsError(ServerManagerError):
    pass


class ServerNotFoundError(ServerManagerError):
    pass


class ServerStartError(ServerManagerError):
    pass


class ServerStopError(ServerManagerError):
    pass


__all__ = [
    "ServerManagerError",
    "ImageNotFoundError",
    "NoAvailablePortError",
    "ServerNotFoundError",
    "ServerStartError",
    "ServerStopError",
]
