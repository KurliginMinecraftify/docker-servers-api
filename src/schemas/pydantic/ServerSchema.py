from pydantic import UUID4, BaseModel, IPvAnyAddress


class ServerCreateSchema(BaseModel):
    ip: IPvAnyAddress
    port: int
    version: str


class ServerResponseSchema(ServerCreateSchema):
    uuid: UUID4


__all__ = ["ServerCreateSchema", "ServerResponseSchema"]
