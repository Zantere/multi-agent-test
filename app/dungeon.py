from __future__ import annotations

import random
import time
from collections import deque

from app.schemas import DungeonResponse, Effect, Encounter, Room


MIN_ROOMS = 8
MAX_ROOMS = 36
DEFAULT_ROOMS = 24

DIRECTIONS = {
    "north": (0, -1),
    "south": (0, 1),
    "east": (1, 0),
    "west": (-1, 0),
}

ROOM_NAMES = [
    "Echoing Armory",
    "Lantern Hall",
    "Sunken Gallery",
    "Old Watch Post",
    "Mosaic Vault",
    "Whispering Library",
    "Cinder Chapel",
    "Broken Fountain",
    "Moonlit Storehouse",
    "Ironbound Crossing",
]

ROOM_DETAILS = [
    "Cold air rolls across carved flagstones and fades into the dark.",
    "A low shimmer of dust hangs where old magic refuses to settle.",
    "Scratches on the wall mark the passage of earlier explorers.",
    "Water drips somewhere beyond sight, counting seconds like coins.",
    "Ancient stonework bends the torchlight into strange angles.",
    "The room smells faintly of rain, rust, and forgotten bargains.",
]

MONSTERS = [
    ("Bone Warden", "It rattles awake and swings a chipped halberd.", Effect(hp=-3)),
    ("Ash Knight", "Its armor glows at the seams as it blocks your path.", Effect(hp=-4, gold=1)),
    ("Cave Stalker", "A shadow drops from the ceiling and tests your guard.", Effect(hp=-2)),
]

NPCS = [
    ("Lost Cartographer", "They mark a shortcut on your map and hand over a brass key.", Effect(keys=1)),
    ("Muttering Oracle", "A warning sharpens your focus before the next chamber.", Effect(hp=1)),
    ("Tired Mercenary", "They share a useful rumor and a few coins.", Effect(gold=2)),
]

TRAPS = [
    ("Needle Floor", "A hidden plate clicks underfoot. You jump, but not fast enough.", Effect(hp=-2)),
    ("Falling Grate", "Iron teeth crash down and scrape your shoulder.", Effect(hp=-3)),
    ("Rune Snare", "A blue sigil flares and steals the breath from your lungs.", Effect(hp=-2)),
]

LOOT = [
    ("Coin Cache", "A loose stone hides a handful of old gold.", Effect(gold=5)),
    ("Field Tonic", "A sealed vial restores some of your strength.", Effect(hp=3)),
    ("Key Ring", "One iron key still fits something important.", Effect(keys=1, gold=1)),
]

EMPTY_EVENTS = [
    ("Quiet Chamber", "Nothing moves here. For once, the dungeon lets you breathe.", Effect()),
    ("Cold Alcove", "You find old bootprints and no immediate danger.", Effect()),
    ("Spent Camp", "A dead firepit suggests someone survived this far.", Effect()),
]


def clamp_room_count(room_count: int | None) -> int:
    if room_count is None:
        return DEFAULT_ROOMS
    return max(MIN_ROOMS, min(MAX_ROOMS, room_count))


def generate_dungeon(seed: int | None = None, rooms: int | None = None) -> DungeonResponse:
    seed_value = seed if seed is not None else time.time_ns() % 1_000_000_000
    rng = random.Random(seed_value)
    room_count = clamp_room_count(rooms)
    coordinates = _connected_coordinates(rng, room_count)
    start = (0, 0)

    room_models = []
    for x, y in sorted(coordinates, key=lambda item: (item[1], item[0])):
        room_id = _room_id(x, y)
        encounter = _build_encounter(rng, is_start=(x, y) == start)
        room_models.append(
            Room(
                id=room_id,
                x=x,
                y=y,
                name="Entry Stair" if (x, y) == start else rng.choice(ROOM_NAMES),
                description=_description_for(rng, x, y, (x, y) == start),
                exits=_exits_for(x, y, coordinates),
                encounter=encounter,
            )
        )

    min_x = min(x for x, _ in coordinates)
    max_x = max(x for x, _ in coordinates)
    min_y = min(y for _, y in coordinates)
    max_y = max(y for _, y in coordinates)

    return DungeonResponse(
        seed=seed_value,
        room_count=len(room_models),
        start_room_id=_room_id(*start),
        width=max_x - min_x + 1,
        height=max_y - min_y + 1,
        rooms=room_models,
    )


def is_connected(rooms: list[Room]) -> bool:
    if not rooms:
        return True
    room_by_id = {room.id: room for room in rooms}
    seen = {rooms[0].id}
    queue: deque[str] = deque([rooms[0].id])

    while queue:
        current = room_by_id[queue.popleft()]
        for direction in current.exits:
            dx, dy = DIRECTIONS[direction]
            neighbor_id = _room_id(current.x + dx, current.y + dy)
            if neighbor_id in room_by_id and neighbor_id not in seen:
                seen.add(neighbor_id)
                queue.append(neighbor_id)

    return len(seen) == len(rooms)


def _connected_coordinates(rng: random.Random, room_count: int) -> set[tuple[int, int]]:
    coordinates = {(0, 0)}
    current = (0, 0)
    attempts = 0

    while len(coordinates) < room_count and attempts < room_count * 80:
        attempts += 1
        dx, dy = rng.choice(list(DIRECTIONS.values()))
        candidate = (current[0] + dx, current[1] + dy)
        if _within_bounds(candidate):
            coordinates.add(candidate)
            current = candidate
        elif coordinates:
            current = rng.choice(tuple(coordinates))

    # If the walk brushes the boundary too often, grow from existing rooms.
    while len(coordinates) < room_count:
        base = rng.choice(tuple(coordinates))
        rng.shuffle(direction_values := list(DIRECTIONS.values()))
        for dx, dy in direction_values:
            candidate = (base[0] + dx, base[1] + dy)
            if _within_bounds(candidate):
                coordinates.add(candidate)
                break

    return coordinates


def _within_bounds(coordinate: tuple[int, int]) -> bool:
    x, y = coordinate
    return -4 <= x <= 4 and -4 <= y <= 4


def _exits_for(x: int, y: int, coordinates: set[tuple[int, int]]) -> list[str]:
    exits = []
    for name, (dx, dy) in DIRECTIONS.items():
        if (x + dx, y + dy) in coordinates:
            exits.append(name)
    return exits


def _description_for(rng: random.Random, x: int, y: int, is_start: bool) -> str:
    if is_start:
        return "The stairway behind you is the last honest path back to daylight."
    return f"{rng.choice(ROOM_DETAILS)} This chamber lies at map point {x}, {y}."


def _build_encounter(rng: random.Random, is_start: bool) -> Encounter:
    if is_start:
        return Encounter(
            type="start",
            name="Safe Landing",
            text="You gather yourself before stepping deeper into the dungeon.",
        )

    encounter_type = rng.choices(
        ["empty", "monster", "loot", "trap", "npc"],
        weights=[30, 24, 20, 16, 10],
        k=1,
    )[0]
    table = {
        "empty": EMPTY_EVENTS,
        "monster": MONSTERS,
        "loot": LOOT,
        "trap": TRAPS,
        "npc": NPCS,
    }[encounter_type]
    name, text, effect = rng.choice(table)
    return Encounter(type=encounter_type, name=name, text=text, effect=effect)


def _room_id(x: int, y: int) -> str:
    return f"{x},{y}"
