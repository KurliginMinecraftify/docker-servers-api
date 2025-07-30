from .manager import ContainerManager


async def getManager():
    manager = ContainerManager()
    try:
        yield manager
    finally:
        await manager.close()
