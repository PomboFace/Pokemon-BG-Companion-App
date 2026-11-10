# Pokemon TT Companion App

A companion web app for the Pokemon tabletop game. The host runs the room and manages the party, and each player joins from their phone with a short room ID, similar to Jackbox. Dice are rolled in real life, so the app only tracks and manages the game.

## How it works

- Plain HTML and JavaScript with no build step. All the code is in `index.html`.
- Browsers connect directly to each other using [PeerJS](https://peerjs.com) (WebRTC). The host's browser holds the game state. Players send actions, the host validates them and broadcasts the new state to everyone.
- The room ID is 4 letters. Players type it in to join.
- The host's tab must stay open. The game is saved in the host's browser, so after a refresh the host can press **Resume room** to get the same room ID and game back. Players reconnect automatically.
- Players on very restrictive networks, such as some mobile carriers, may fail to connect without a TURN server. On the same Wi-Fi this is rarely a problem.

## Running and hosting

The app loads JSON files, so it must be served over http. Opening `index.html` directly from disk will not work.

- **Testing locally:** run `python -m http.server` in this folder and open `http://localhost:8000`.
- **Free hosting:** upload the whole folder to GitHub Pages, Cloudflare Pages or Netlify. It is just static files.

## Folder layout

```
index.html
make_chips_list.py   regenerates chips/chips.json
regions/
  regions.json         list of regions the host can pick from
  kanto.json           encounter table for one region
trainers/
  trainers.json        list of trainers (name + color)
  red.png ...          trainer icons
chips/
  0001_bulbasaur.png   Pokemon chip images
  chips.json           list of chip files (made by make_chips_list.py)
  placeholder.png      shown in empty slots
badges/
  boulder.png ...      the 8 badge images
```

Missing images are not fatal. A Pokemon shows its name, a trainer shows a colored circle with their initial, a badge shows its number, and an empty slot shows a dashed circle.

### Regions

A static website cannot list a folder, so `regions/regions.json` lists the available regions. When you add a region, put its file in `regions/` and add a line here:

```json
{
  "regions": [
    { "name": "Kanto", "file": "kanto.json" }
  ]
}
```

Each region file maps a location to its possible encounters. Every top-level key becomes a button on the host screen. `BP` is the Pokemon's power level and is only used to weight the rolls.

```json
{
  "Viridian Forest": [
    { "pokemon": "Caterpie", "BP": 1 },
    { "pokemon": "Pikachu", "BP": 4 }
  ]
}
```

### Trainers

`trainers/trainers.json`:

```json
{
  "trainers": [
    { "name": "Red", "color": "#E53935" },
    { "name": "Blue", "color": "#1E88E5" }
  ]
}
```

- The icon is loaded from `trainers/<lowercase name>.png`, for example `trainers/red.png`. To use another file name, add `"image": "red_icon.png"` to that trainer.
- The color becomes the player's whole app background and the color of their rectangle on the host screen.
- Each trainer can only be picked by one player at a time.

### Chips and badges

- **The chips folder is the Pokemon database for search.** Any Pokemon with a chip image can be searched, even if it is not in the current region's encounters, and it is not limited to Gen 1. A website cannot list a folder, so after adding or removing chips run `python make_chips_list.py`, which writes `chips/chips.json`. Without that file the app falls back to the 151 Gen 1 names.
- Chip images are named `<4 digit dex number>_<lowercase name>.png`, with symbols removed. The name part is also how the app shows the Pokemon, so `0083_farfetchd` displays as Farfetch’d for Gen 1 and other names are capitalised, with `_` or `-` turned into spaces (`0019_raticate_alola` shows as Raticate Alola). For example `0001_bulbasaur.png`, `0083_farfetchd.png`, `0122_mrmime.png`. The Nidorans are looked up as `0029_nidoranf.png` and `0032_nidoranm.png`.
- If your naming differs, change the `chipSrc` and `badgeSrc` lines near the top of `index.html`.
- Badge images are named after the gym: `boulder`, `cascade`, `thunder`, `rainbow`, `soul`, `marsh`, `volcano`, `earth` (all `.png`).

## Player screen

The top row has the trainer icon and name on the left. On the player's turn, a **YOUR TURN** sign and a **Pass** button appear at the top right. Earned badges are shown in the bottom-right corner, and **Leave** is in the bottom-left.

Below that is a row of four slots:

- **Slots 1 to 3 are the party.** Each shows the Pokemon's chip image in full, with its battle point bonus underneath.
- **Slot 1, on the left, is always the active Pokemon.** It has a gold highlight behind the image. To change the active Pokemon, drag one into that slot.
- **Slot 4 is the encounter.** It is closed like a drawer and slides open only when the host gives the player an encounter, with a purple highlight behind the image.

Gestures:

| Gesture | Effect |
| --- | --- |
| Drag a chip onto another slot | Swaps the two Pokemon. The bonus moves with the Pokemon. |
| Double-tap a chip | Faints or revives it. Fainted chips are darkened. |
| Swipe left or right over the bonus | Changes it by 0.5 per step. |
| Hold the right half of the bonus | Counts up continuously. |
| Hold the left half of the bonus | Counts down continuously. |

The bonus ranges from 0 to 10 and starts at 0 for every new Pokemon. It is shown as ◀ +4 ▶ with arrows to show it can be slid.

**Encounters:** when an encounter appears in slot 4, it is always for that player to choose. Drag it onto a party Pokemon to swap, which puts the party Pokemon in slot 4. Drag it onto an empty slot to add it to the team. When done, press **Done** to close the slot. Anything still left in slot 4 is released.

**Passing the turn:** the Pass button only appears on the player's own turn, and asks for confirmation.

## Host screen

The left panel has the **Early / Mid slider** at the top and the **region list** below it. Each region is a button that rolls an encounter for the current player.

The main area has, from top to bottom:

- **Room code:** click it to copy it. **Pass turn** is on the right.
- **Search bar:** type a Pokemon name and its picture appears next to the box. Drag the picture onto a player's rectangle to give it to them, or onto the encounter box to make it the current player's encounter.
- **Current encounter:** shows the Pokemon, who it is for, and a **Dismiss** button.
- **Players:** one colored rectangle per player, showing:
  - their trainer icon and name
  - their three Pokemon with chip images, bonus and fainted state, with the active one highlighted
  - their badges, which the host can toggle on and off
  - buttons to remove a single Pokemon (the ✕ on its chip) or remove the player

Drag a player's ⠿ handle to set the turn order. Passing the turn simply moves the gold highlight to the next player and shows YOUR TURN on their screen. It does not skip players who are offline.

### Encounter odds

Rolls are weighted per region by the slider:

- **Early game:** Pokemon with BP 4 or less are 4 times as likely as the rest.
- **Mid game:** Pokemon with BP 4 to 7 are 4 times as likely as the rest.
- **BP 8 and above:** each such Pokemon always has exactly a 1 in 100 chance, regardless of the slider.

Searching for a Pokemon by name and dropping it bypasses the odds entirely. Any Pokemon in the chips folder can be found this way.

## Known limitations

- The host tab must remain open for the room to work.
- The game state lives in the host's browser. Clearing its storage loses the saved game.
- Passing the turn does not skip offline players.
- Only one encounter can be active at a time. Starting a new one asks before replacing the current one.
