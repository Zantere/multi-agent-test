from __future__ import annotations

from pydantic import BaseModel, Field


class Effect(BaseModel):
    hp: int = 0
    gold: int = 0
    keys: int = 0


class Encounter(BaseModel):
    type: str
    name: str
    text: str
    effect: Effect = Field(default_factory=Effect)


class Room(BaseModel):
    id: str
    x: int
    y: int
    name: str
    description: str
    exits: list[str]
    encounter: Encounter


class DungeonResponse(BaseModel):
    seed: int
    room_count: int
    start_room_id: str
    width: int
    height: int
    rooms: list[Room]
