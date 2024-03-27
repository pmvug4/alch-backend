from pydantic import BaseModel


class UserGroup(BaseModel):
    id: int
    name: str


PlayerGroup = UserGroup(
    id=1,
    name='player'
)

AdminGroup = UserGroup(
    id=5,
    name='admin'
)
