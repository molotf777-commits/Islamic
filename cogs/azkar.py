import discord
from discord.ext import commands, tasks
import random
import datetime
import os
import asyncio

# ✅ استيراد من config
from config import (
    COLOR_MAIN,
    AZKAR_IMAGE,
    AZKAR_CHANNEL_ID,
    AZKAR_INTERVAL,
    FOOTER_TEXT
)

class Azkar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.time_file = "last_azkar_time.txt"
        self.auto_azkar.start()

    def cog_unload(self):
        self.auto_azkar.cancel()

    def get_last_send_time(self):
        if os.path.exists(self.time_file):
            try:
                with open(self.time_file, "r", encoding="utf-8") as f:
                    timestamp = float(f.read().strip())
                    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
            except Exception:
                return None
        return None

    def save_last_send_time(self):
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        with open(self.time_file, "w", encoding="utf-8") as f:
            f.write(str(now))

    def get_azkar_list(self):
        # ... القائمة الطويلة (نفسها)
        return [ ... ]

    async def send_zekr_embed(self, target):
        zekr = random.choice(self.get_azkar_list())

        embed = discord.Embed(
            title="عطر فمك بذكر الله 📿",
            description=f"**• {zekr}**",
            color=COLOR_MAIN  # ✅ من config
        )
        
        embed.set_image(url=AZKAR_IMAGE)  # ✅ من config
        embed.set_footer(text=FOOTER_TEXT)  # ✅ من config

        message = await target.send(embed=embed)

        try:
            emoji = self.bot.get_emoji(1542236588686311596)
            if emoji:
                await message.add_reaction(emoji)
            else:
                await message.add_reaction("<:custom_emoji:1542236588686311596>")
        except Exception as e:
            print(f"حدث خطأ أثناء إضافة الريأكت: {e}")

        return message

    @commands.command(name="testazkar", aliases=["testz", "تست_اذكار"])
    async def test_azkar_cmd(self, ctx):
        await self.send_zekr_embed(ctx.channel)

    @tasks.loop(minutes=AZKAR_INTERVAL)  # ✅ من config
    async def auto_azkar(self):
        channel_id = AZKAR_CHANNEL_ID  # ✅ من config
        channel = self.bot.get_channel(channel_id)

        if channel is None:
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except Exception as e:
                print(f"لم يتم العثور على القناة: {e}")
                return

        try:
            await self.send_zekr_embed(channel)
            self.save_last_send_time()
        except Exception as e:
            print(f"حدث خطأ أثناء إرسال الذكر التلقائي: {e}")

    @auto_azkar.before_loop
    async def before_auto_azkar(self):
        await self.bot.wait_until_ready()
        
        last_time = self.get_last_send_time()
        if last_time:
            now = datetime.datetime.now(datetime.timezone.utc)
            elapsed_seconds = (now - last_time).total_seconds()
            interval_seconds = AZKAR_INTERVAL * 60  # ✅ من config
            
            if elapsed_seconds < interval_seconds:
                remaining_seconds = interval_seconds - elapsed_seconds
                print(f"[Azkar System] باقي {int(remaining_seconds // 60)} دقيقة")
                await asyncio.sleep(remaining_seconds)

async def setup(bot):
    await bot.add_cog(Azkar(bot))
