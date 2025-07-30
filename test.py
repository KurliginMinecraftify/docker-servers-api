import asyncio
from aiodocker import Docker

async def main():
    docker = Docker(url='npipe:////./pipe/dockerDesktopLinuxEngine')
    info = await docker.system.info()
    print(info)
    await docker.close()

asyncio.run(main())
