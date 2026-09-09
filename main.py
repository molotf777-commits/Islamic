import discord
from discord.ext import commands
import asyncio
import sys

# استيراد الإعدادات
from config import BOT_TOKEN

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    print(f"✅ Bot is ready!")
    print(f"📊 Logged in as: {bot.user.name}")
    print(f"🆔 Bot ID: {bot.user.id}")
    print(f"📡 Servers: {len(bot.guilds)}")
    
    # تحميل الكوجات
    try:
        await bot.load_extension("azkar")
        print("✅ Azkar cog loaded!")
        await bot.load_extension("quran")
        print("✅ Quran cog loaded!")
    except Exception as e:
        print(f"❌ Error loading cogs: {e}")

@bot.command(name="reload")
@commands.is_owner()
async def reload_cogs(ctx):
    """إعادة تحميل الكوجات (للمطور فقط)"""
    try:
        await bot.reload_extension("azkar")
        await bot.reload_extension("quran")
        await ctx.send("✅ تم إعادة تحميل جميع الكوجات!")
        print("✅ Cogs reloaded!")
    except Exception as e:
        await ctx.send(f"❌ خطأ: {e}")
        print(f"❌ Error reloading: {e}")

# تشغيل البوت
if __name__ == "__main__":
    if BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        print("❌ يرجى وضع توكن البوت في config.py")
        sys.exit(1)
    
    try:
        bot.run(BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ خطأ في التوكن! تأكد من وضع التوكن الصحيح في config.py")
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
