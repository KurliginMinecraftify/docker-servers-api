from pydantic import UUID4, BaseModel


class ServerCreateSchema(BaseModel):
    version: str


class ServerActivationSchema(BaseModel):
    uuid: UUID4


class ServerResponseSchema(ServerCreateSchema):
    port: int
    rcon_port: int
    rcon_password: str
    uuid: UUID4
