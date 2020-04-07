# Description

This script is an example of how a Discord Server can be exported in its entirety.

This script is using the `tyrrrz/discordchatexporter` Docker image of [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter).

# Usage

```sh
export API_TOKEN=abcd
export GUILD_ID=1234
./export.sh
```

# Instructions

You can get instructions on getting the necessary values by running:
```sh
docker run --rm -it tyrrrz/discordchatexporter guide
```
