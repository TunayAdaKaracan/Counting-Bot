import discord
import json
import aiohttp
import urllib.parse


intents = discord.Intents.default()
intents.guild_messages = True
intents.message_content = True


with open("./settings/config.json", "r") as f:
    data = json.load(f)

with open("./settings/count.json", "r") as f:
    number = json.load(f)["number"]


class Counter(discord.Bot):
    def __init__(self):
        super().__init__(intents=intents)
        self.data = data
        self.number = number

    async def on_ready(self):
        print("Bot is ready")

    async def get_number(self, expr):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.mathjs.org/v4/?expr='+urllib.parse.quote_plus(expr)) as r:
                if r.status == 200:
                    return [True, await r.text()]
                elif r.status == 400:
                    return [False, None]

    async def push_number(self, number):
        with open("./settings/count.json", "w") as f:
            f.write(json.dumps({"number": number}))

    async def on_message(self, message: discord.Message):
        if message.author.bot: return
        if isinstance(message.channel, discord.DMChannel): return
        if message.guild.id == self.data["guild-id"] and message.channel.id == self.data["channel-id"]:
            if message.content.isdigit() or str(float(self.number+1)) == message.content:
                if int(message.content) == self.number+1:
                    await message.add_reaction("✅")
                    await self.push_number(self.number+1)
                    self.number += 1
                    return
            else:
                valid, text = await self.get_number(message.content)
                if valid and ((text.isdigit() and int(text) == self.number + 1) or str(float(self.number+1)) == text):
                    await message.add_reaction("✅")
                    await self.push_number(self.number + 1)
                    self.number += 1
                    return
                elif valid:
                    if self.data["delete-wrong-numbers"]:
                        errormessage = await message.channel.send(f"{message.author.mention} Please Type {self.number+1}")
                        await message.delete(delay=5)
                        await errormessage.delete(delay=5)
                    else:
                        await message.channel.send(f"{message.author.mention} RUINED AT {self.number+1}! Start From **1**")
                        await self.push_number(0)
                        self.number = 0


if __name__ == "__main__":
    client = Counter()
    client.run(client.data["bot-token"])
