class DatabaseError(Exception):
    pass


class ContainerManagerError(Exception):
    pass


class ImageNotFoundError(ContainerManagerError):
    pass


class NoAvailablePortError(ContainerManagerError):
    pass


class ContainerNotFoundError(ContainerManagerError):
    pass


class ContainerStartError(ContainerManagerError):
    pass


class ContainerStopError(ContainerManagerError):
    pass


class ContainerDeleteError(ContainerManagerError):
    pass


class ServerAlreadyExistsError(ContainerManagerError):
    pass


class ServerRestartError(ContainerManagerError):
    pass


class ContainerCreateError(ContainerManagerError):
    pass
