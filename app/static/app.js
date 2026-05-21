const STARTING_PLAYER = Object.freeze({
  hp: 12,
  gold: 0,
  keys: 0,
});

const ENCOUNTER_SYMBOLS = {
  start: "S",
  empty: ".",
  monster: "M",
  npc: "N",
  trap: "T",
  loot: "L",
};

const state = {
  dungeon: null,
  selectedRoomId: null,
  visitedRooms: new Set(),
  resolvedRooms: new Set(),
  player: { ...STARTING_PLAYER },
  log: [],
};

const els = {
  grid: document.querySelector("#dungeon-grid"),
  generate: document.querySelector("#generate-btn"),
  reset: document.querySelector("#reset-btn"),
  roomCount: document.querySelector("#room-count"),
  seedValue: document.querySelector("#seed-value"),
  mapStatus: document.querySelector("#map-status"),
  hp: document.querySelector("#hp-value"),
  gold: document.querySelector("#gold-value"),
  keys: document.querySelector("#keys-value"),
  explored: document.querySelector("#explored-value"),
  roomType: document.querySelector("#room-type"),
  roomTitle: document.querySelector("#room-title"),
  roomDescription: document.querySelector("#room-description"),
  encounterBox: document.querySelector("#encounter-box"),
  runLog: document.querySelector("#run-log"),
};

els.generate.addEventListener("click", () => generateDungeon());
els.reset.addEventListener("click", () => resetRun({ keepDungeon: true }));

generateDungeon();

async function generateDungeon() {
  const roomCount = Number.parseInt(els.roomCount.value, 10) || 24;
  setStatus("Drawing fresh corridors...");
  const response = await fetch(`/api/dungeon?rooms=${encodeURIComponent(roomCount)}`);
  if (!response.ok) {
    setStatus("The dungeon refused to form. Try a smaller map.");
    return;
  }

  state.dungeon = await response.json();
  resetRun({ keepDungeon: true, quiet: true });
  state.selectedRoomId = state.dungeon.start_room_id;
  visitRoom(state.selectedRoomId);
  addLog(`Generated dungeon seed ${state.dungeon.seed}.`);
  render();
}

function resetRun({ keepDungeon, quiet } = {}) {
  state.selectedRoomId = keepDungeon && state.dungeon ? state.dungeon.start_room_id : null;
  state.visitedRooms = new Set();
  state.resolvedRooms = new Set();
  state.player = { ...STARTING_PLAYER };
  state.log = [];
  if (!quiet) {
    addLog("Run reset. Your pack feels lighter and your pulse steadier.");
  }
  if (state.dungeon && keepDungeon) {
    visitRoom(state.dungeon.start_room_id);
  }
  render();
}

function visitRoom(roomId) {
  const room = getRoom(roomId);
  if (!room || state.player.hp <= 0) {
    return;
  }

  state.selectedRoomId = roomId;
  const firstVisit = !state.visitedRooms.has(roomId);
  state.visitedRooms.add(roomId);

  if (firstVisit && !state.resolvedRooms.has(roomId)) {
    resolveEncounter(room);
  }

  render();
}

function resolveEncounter(room) {
  state.resolvedRooms.add(room.id);
  const effect = room.encounter.effect || {};
  state.player.hp = Math.max(0, state.player.hp + (effect.hp || 0));
  state.player.gold = Math.max(0, state.player.gold + (effect.gold || 0));
  state.player.keys = Math.max(0, state.player.keys + (effect.keys || 0));

  if (room.encounter.type === "start") {
    addLog("You arrive at the entry stair.");
  } else {
    addLog(`${room.encounter.name}: ${room.encounter.text}`);
  }

  if (state.player.hp <= 0) {
    addLog("Your HP reached zero. Reset the run or generate a new dungeon.");
  }
}

function render() {
  renderStats();
  renderRoomDetails();
  renderGrid();
  renderLog();
}

function renderStats() {
  els.hp.textContent = state.player.hp;
  els.gold.textContent = state.player.gold;
  els.keys.textContent = state.player.keys;
  els.explored.textContent = state.visitedRooms.size;
}

function renderRoomDetails() {
  if (!state.dungeon) {
    return;
  }
  const room = getRoom(state.selectedRoomId);
  if (!room) {
    return;
  }

  els.seedValue.textContent = state.dungeon.seed;
  els.roomType.textContent = room.encounter.type;
  els.roomTitle.textContent = room.name;
  els.roomDescription.textContent = room.description;
  els.encounterBox.textContent = `${room.encounter.name}. ${room.encounter.text}`;
  setStatus(`${state.visitedRooms.size} of ${state.dungeon.room_count} rooms explored.`);
}

function renderGrid() {
  els.grid.replaceChildren();
  if (!state.dungeon) {
    return;
  }

  const rooms = state.dungeon.rooms;
  const minX = Math.min(...rooms.map((room) => room.x));
  const maxX = Math.max(...rooms.map((room) => room.x));
  const minY = Math.min(...rooms.map((room) => room.y));
  const maxY = Math.max(...rooms.map((room) => room.y));
  const roomByPosition = new Map(rooms.map((room) => [`${room.x},${room.y}`, room]));

  els.grid.style.setProperty("--grid-cols", String(maxX - minX + 1));

  for (let y = minY; y <= maxY; y += 1) {
    for (let x = minX; x <= maxX; x += 1) {
      const room = roomByPosition.get(`${x},${y}`);
      if (!room) {
        const empty = document.createElement("div");
        empty.className = "empty-cell";
        els.grid.append(empty);
        continue;
      }

      const tile = document.createElement("button");
      tile.type = "button";
      tile.className = [
        "room-tile",
        room.encounter.type,
        state.visitedRooms.has(room.id) ? "visited" : "",
        state.selectedRoomId === room.id ? "selected" : "",
      ].join(" ");
      tile.disabled = state.player.hp <= 0 && !state.visitedRooms.has(room.id);
      tile.setAttribute("aria-label", `${room.name}, ${room.encounter.type}`);
      tile.addEventListener("click", () => visitRoom(room.id));

      const symbol = document.createElement("span");
      symbol.className = "tile-symbol";
      symbol.textContent = state.visitedRooms.has(room.id)
        ? ENCOUNTER_SYMBOLS[room.encounter.type]
        : "?";
      tile.append(symbol);
      els.grid.append(tile);
    }
  }
}

function renderLog() {
  els.runLog.replaceChildren();
  for (const entry of state.log.slice(-8).reverse()) {
    const item = document.createElement("li");
    item.textContent = entry;
    els.runLog.append(item);
  }
}

function addLog(message) {
  state.log.push(message);
}

function getRoom(roomId) {
  return state.dungeon?.rooms.find((room) => room.id === roomId);
}

function setStatus(message) {
  els.mapStatus.textContent = message;
}
