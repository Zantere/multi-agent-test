from app.dungeon import DIRECTIONS, generate_dungeon, is_connected


VALID_TYPES = {"start", "empty", "monster", "npc", "trap", "loot"}
OPPOSITE = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
}


def test_seeded_generation_is_stable():
    first = generate_dungeon(seed=123, rooms=18)
    second = generate_dungeon(seed=123, rooms=18)

    assert first.model_dump() == second.model_dump()


def test_generated_rooms_have_unique_ids_and_valid_encounters():
    dungeon = generate_dungeon(seed=50, rooms=24)
    room_ids = [room.id for room in dungeon.rooms]

    assert len(room_ids) == len(set(room_ids))
    assert dungeon.room_count == 24
    assert dungeon.start_room_id in room_ids
    assert {room.encounter.type for room in dungeon.rooms} <= VALID_TYPES


def test_generated_dungeon_is_connected():
    dungeon = generate_dungeon(seed=999, rooms=36)

    assert is_connected(dungeon.rooms)


def test_exits_are_symmetrical():
    dungeon = generate_dungeon(seed=321, rooms=30)
    rooms_by_position = {(room.x, room.y): room for room in dungeon.rooms}

    for room in dungeon.rooms:
        for direction in room.exits:
            dx, dy = DIRECTIONS[direction]
            neighbor = rooms_by_position[(room.x + dx, room.y + dy)]
            assert OPPOSITE[direction] in neighbor.exits


def test_room_count_is_clamped_for_direct_engine_calls():
    assert generate_dungeon(seed=1, rooms=2).room_count == 8
    assert generate_dungeon(seed=1, rooms=100).room_count == 36
