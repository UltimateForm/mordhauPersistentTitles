# mordhauPersistentTitles

This a Discord X RCON bot that is used to implement persistent tags (via RCON's `renameplayer`) and salutes (via RCON's `say`)

- [mordhauPersistentTitles](#mordhaupersistenttitles)
	- [What it do?](#what-it-do)
	- [Usage](#usage)
		- [Setup](#setup)
		- [Discord usage](#discord-usage)
	- [Example .env](#example-env)
	- [Important notes](#important-notes)

## What it do?

This bot allows you to 
- have custom tags (or titles) in front of player's names, i.e. you can tag a player with name "FFAer" or "Champion". These tags will last until they're removed. **Note that if you add a tag to player while he is ingame he will need to rejoin server for tag to take effect**
- have specific server messages spawn when selected players join server

These features are managed via discord


## Usage
You need at least Docker installed and a terminal that can run .sh files (linux or unix-like system)

### Setup

1. clone repo or download code
1. create .env file in same folder as code with these parameters:
    1. RCON_PASSWORD
    1. RCON_ADDRESS
    1. RCON_PORT
    2. RCON_CONNECT_TIMEOUT (optional)
    3. D_TOKEN (discord bot auth token)
2. run `sh restart.sh` in terminal
    1. if you're familar with docker or python you don't necessarily need to this, you can run this bot anywhere and however you want

### Discord usage

I will not tell you here how to setup a discord bot, there's already plenty of guides about that. The bot code here does not manage permissions so it's on you to manage the access.

Commands:
- .setTagFormat {tag format}
  - sets the tag format, must always include {0} which is the placeholder for the tag
  - example: `.setTagFormat -{0}-`
- .setSaluteTimer {number of seconds}
  - sets the time in seconds for salute to show up in server,
  - example: `.setSaluteTimer 2`
- .addTag {playfab id} {tag}
  - sets a tag for a playfab id
  - example: `.addTag D98123JKAS78354 CryBaby`
- .removeTag {playfab id}
  - removes tag for playfabid
  - example: `.removeTag D98123JKAS78354`
- .addSalute {playfab id} {salute text}
  - adds salute for playfab id
  - use quotes ("") for multi word salutes
  - example: `.addSalute D98123JKAS78354 "Welcome back Dan"`
- .removeSalute {playfab id}
  - removes salute for playfab id
  - example: `.removeSalute D98123JKAS78354`
- .ptConf
  - shows full config
  - example: `.ptConf`

## Example .env
```
RCON_PASSWORD=superD_uprSecurePw
RCON_ADDRESS=192.168.0.52
RCON_PORT=27019
RCON_CONNECT_TIMEOUT=10
D_TOKEN=sNb5gkzmvnJ8W9rxHP23kNV5s7GDwtY4J4cY4JNbbM5Bctd8UFURsv8TAShsPdPDXFcaai2WlPaHy3Rxis5C3m5dHXk1leUU
```


## Important notes
1. This bot doesn't use (yet) the native discord commands
2. This bot hasn't been stress tested, a previous version has been tested on a server with 20-40 players, but was different code