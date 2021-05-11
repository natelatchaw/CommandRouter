import discord
from router.settings import Settings

class Logger():
    
    def __init__(self, settings: Settings, guild: discord.Guild):
        self.settings = settings
        self.guild = guild

    async def print(self, *args):
        message = '\n'.join(args)
        try:
            # get the logging channel id from the config
            channel_id: int = self.settings.logging_channel
        except (TypeError, ValueError):
            return
        # get the channel object from the channel id
        logging_channel = self.guild.get_channel(channel_id)
        if not isinstance(logging_channel, discord.TextChannel):
            return
        await logging_channel.send(f'{message}')

