import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import json
from typing import Optional
import aiohttp

# ✅ Enable opus for voice
try:
    import nacl
    print("✅ PyNaCl loaded successfully!")
except ImportError:
    print("⚠️ PyNaCl not found! Installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'PyNaCl==1.6.2'])
    import nacl
    print("✅ PyNaCl installed successfully!")

# ✅ Try to import davey (new Discord voice encryption)
try:
    import davey
    print("✅ Davey loaded successfully!")
except ImportError:
    print("⚠️ Davey not found! Installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'davey>=0.1.0'])
    import davey
    print("✅ Davey installed successfully!")

# ✅ FFmpeg setup with static-ffmpeg
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
    print("✅ FFmpeg loaded successfully via static-ffmpeg!")
except Exception as e:
    print(f"⚠️ FFmpeg loading issue: {e}")

# ✅ ملف حفظ الحالة
STATE_FILE = "quran_state.json"

def save_state(data):
    """حفظ الحالة في ملف JSON"""
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"⚠️ Error saving state: {e}")

def load_state():
    """تحميل الحالة من ملف JSON"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading state: {e}")
    return None

class QuranRadio(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.is_playing = False
        self.voice_channel_id = None
        self.guild_id = None
        self.retry_count = 0
        self.max_retries = 3
        self.current_mode = "recitation"  # "recitation" or "radio"
        self.current_radio = "cairo"
        self.current_surah = 1
        self.current_reciter = "minsh1387"
        self.control_channel_id = 1471987630399819908
        self.voice_channel_target_id = 1471987630399819908
        self.control_message_id = None
        self.current_embed_message = None
        self.is_radio_playing = False  # متغير جديد لتتبع حالة الإذاعة
        
        # ✅ FFmpeg options for stability
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -vn',
            'options': '-b:a 128k'
        }
        
        # ✅ الإذاعات
        self.radio_stations = {
            "cairo": {
                "id": "cairo",
                "name": "📻 إذاعة القرآن الكريم - القاهرة",
                "emoji": "📻",
                "url": "https://stream.radiojar.com/8s5u5tpdtwzuv",
                "img": "https://i1.sndcdn.com/artworks-000096282703-s9wldh-t200x200.jpg"
            },
            "saudi": {
                "id": "saudi",
                "name": "📻 إذاعة القرآن الكريم - السعودية",
                "emoji": "📻",
                "url": "https://n12.radiojar.com/0tpy1h0kxtzuv",
                "img": "https://i1.sndcdn.com/artworks-000096282703-s9wldh-t200x200.jpg"
            }
        }
        
        # ✅ قائمة التلاوات (القُراء)
        self.recitations = {
            "minsh1387": {
                "id": "minsh1387",
                "name": "🕌 محمد صديق المنشاوي - 1387 هـ",
                "emoji": "🕌",
                "base_url": "https://server10.mp3quran.net/minsh1387/",
                "img": "https://i1.sndcdn.com/artworks-000096282703-s9wldh-t200x200.jpg",
                "total_surahs": 114
            },
            "yasser": {
                "id": "yasser",
                "name": "🕌 ياسر الدوسري",
                "emoji": "🕌",
                "base_url": "https://server11.mp3quran.net/yasser/",
                "img": "https://i1.sndcdn.com/artworks-000096282703-s9wldh-t200x200.jpg",
                "total_surahs": 114
            },
            "maher": {
                "id": "maher",
                "name": "🕌 ماهر المعيقلي",
                "emoji": "🕌",
                "base_url": "https://server12.mp3quran.net/maher/",
                "img": "https://i1.sndcdn.com/artworks-000096282703-s9wldh-t200x200.jpg",
                "total_surahs": 114
            },
            "basit": {
                "id": "basit",
                "name": "🕌 عبد الباسط عبد الصمد",
                "emoji": "🕌",
                "base_url": "https://server7.mp3quran.net/basit/",
                "img": "https://i1.sndcdn.com/artworks-000096282703-s9wldh-t200x200.jpg",
                "total_surahs": 114
            },
            "lhdan": {
                "id": "lhdan",
                "name": "🕌 محمد اللحيدان",
                "emoji": "🕌",
                "base_url": "https://server8.mp3quran.net/lhdan/",
                "img": "https://i1.sndcdn.com/artworks-000096282703-s9wldh-t200x200.jpg",
                "total_surahs": 114
            },
            "islam": {
                "id": "islam",
                "name": "🕌 إسلام صبحي",
                "emoji": "🕌",
                "base_url": "https://server14.mp3quran.net/islam/Rewayat-Hafs-A-n-Assem/",
                "img": "https://i1.sndcdn.com/artworks-000096282703-s9wldh-t200x200.jpg",
                "total_surahs": 114
            },
            "ayyoub": {
                "id": "ayyoub",
                "name": "🕌 محمد أيوب",
                "emoji": "🕌",
                "base_url": "https://server16.mp3quran.net/ayyoub2/Rewayat-Hafs-A-n-Assem/",
                "img": "https://i1.sndcdn.com/artworks-000096282703-s9wldh-t200x200.jpg",
                "total_surahs": 114
            }
        }
        
        # ✅ أسماء السور
        self.surah_names = [
            "الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة", "الأنعام", "الأعراف", "الأنفال", "التوبة", "يونس",
            "هود", "يوسف", "الرعد", "إبراهيم", "الحجر", "النحل", "الإسراء", "الكهف", "مريم", "طه",
            "الأنبياء", "الحج", "المؤمنون", "النور", "الفرقان", "الشعراء", "النمل", "القصص", "العنكبوت", "الروم",
            "لقمان", "السجدة", "الأحزاب", "سبأ", "فاطر", "يس", "الصافات", "ص", "الزمر", "غافر",
            "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية", "الأحقاف", "محمد", "الفتح", "الحجرات", "ق",
            "الذاريات", "الطور", "النجم", "القمر", "الرحمن", "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة",
            "الصف", "الجمعة", "المنافقون", "التغابن", "الطلاق", "التحريم", "الملك", "القلم", "الحاقة", "المعارج",
            "نوح", "الجن", "المزمل", "المدثر", "القيامة", "الإنسان", "المرسلات", "النبأ", "النازعات", "عبس",
            "التكوير", "الانفطار", "المطففين", "الانشقاق", "البروج", "الطارق", "الأعلى", "الغاشية", "الفجر", "البلد",
            "الشمس", "الليل", "الضحى", "الشرح", "التين", "العلق", "القدر", "البينة", "الزلزلة", "العاديات",
            "القارعة", "التكاثر", "العصر", "الهمزة", "الفيل", "قريش", "الماعون", "الكوثر", "الكافرون", "النصر",
            "المسد", "الإخلاص", "الفلق", "الناس"
        ]
        
        # ✅ صورة لوحة التحكم
        self.control_image = "https://cdn.discordapp.com/attachments/1462058133835747381/1544855500066131998/ChatGPT_Image_Sep_3_2026_02_42_59_AM.png?ex=6a9a064d&is=6a98b4cd&hm=9a8b3f482de20c29767b5ca9efacf041a3b511dd90845cd868ca92fc3cbba851&"
        
        # ✅ ID المطور
        self.developer_id = 726776467371065407
        
        # ✅ تحميل الحالة السابقة
        self.load_state()

    def save_state(self):
        """حفظ الحالة الحالية"""
        state = {
            "current_mode": self.current_mode,
            "current_radio": self.current_radio,
            "current_surah": self.current_surah,
            "current_reciter": self.current_reciter,
            "is_playing": self.is_playing,
            "control_message_id": self.control_message_id
        }
        save_state(state)

    def load_state(self):
        """تحميل الحالة السابقة"""
        state = load_state()
        if state:
            self.current_mode = state.get("current_mode", "recitation")
            self.current_radio = state.get("current_radio", "cairo")
            self.current_surah = state.get("current_surah", 1)
            self.current_reciter = state.get("current_reciter", "minsh1387")
            self.is_playing = state.get("is_playing", False)
            self.control_message_id = state.get("control_message_id", None)
            print(f"✅ Loaded state: {state}")

    async def create_control_embed(self, interaction: discord.Interaction = None):
        """إنشاء لوحة التحكم مع الصورة"""
        embed = discord.Embed(
            title="🌙 اختر الشيخ أو الإذاعة من القائمة أدناه",
            color=0xFF0000
        )
        
        embed.set_image(url=self.control_image)
        
        if interaction:
            guild = interaction.guild
        else:
            guild = self.bot.guilds[0] if self.bot.guilds else None
        
        developer = None
        if guild:
            developer = guild.get_member(self.developer_id)
        
        dev_avatar = None
        if developer and developer.avatar:
            dev_avatar = developer.avatar.url
        elif developer and developer.default_avatar:
            dev_avatar = developer.default_avatar.url
        
        embed.set_footer(
            text="Copyright © Full Red 2026 | @MOLOTOF 👑",
            icon_url=dev_avatar
        )
        
        return embed

    async def get_or_create_control_message(self, channel):
        """البحث عن الرسالة القديمة أو إنشاء جديدة"""
        if self.control_message_id:
            try:
                msg = await channel.fetch_message(self.control_message_id)
                if msg:
                    return msg
            except discord.NotFound:
                self.control_message_id = None
                self.save_state()
            except Exception as e:
                print(f"⚠️ Error fetching message: {e}")
        
        try:
            async for msg in channel.history(limit=50):
                if msg.author == self.bot.user and msg.embeds:
                    if msg.embeds and msg.embeds[0].title and "اختر الشيخ" in msg.embeds[0].title:
                        self.control_message_id = msg.id
                        self.save_state()
                        return msg
        except Exception as e:
            print(f"⚠️ Error searching history: {e}")
        
        return None

    async def send_control_panel(self, channel, interaction: discord.Interaction = None):
        """إرسال أو تحديث لوحة التحكم (بدون أزرار ⏮️، ▶️، ⏭️)"""
        embed = await self.create_control_embed(interaction)
        
        view = discord.ui.View(timeout=None)
        
        # ✅ Select Menu بالخيارات المباشرة بدون فواصل
        main_select = discord.ui.Select(
            placeholder="📌 اختر الشيخ أو الإذاعة...",
            min_values=1,
            max_values=1,
            custom_id="main_select"
        )
        
        # 1. إذاعة القاهرة
        main_select.add_option(
            label="إذاعة القرآن الكريم - القاهرة",
            value="radio_cairo",
            emoji="📻"
        )
        # 2. إذاعة السعودية
        main_select.add_option(
            label="إذاعة القرآن الكريم - السعودية",
            value="radio_saudi",
            emoji="📻"
        )
        # 3. القراء
        for reciter_id, reciter in self.recitations.items():
            clean_name = reciter["name"].replace("🕌 ", "")
            main_select.add_option(
                label=clean_name[:100],
                value=f"reciter_{reciter_id}",
                emoji="🕌"
            )
        
        view.add_item(main_select)
        
        existing_msg = await self.get_or_create_control_message(channel)
        
        if existing_msg:
            try:
                await existing_msg.edit(embed=embed, view=view)
                self.control_message_id = existing_msg.id
                self.save_state()
                return
            except Exception as e:
                print(f"⚠️ Could not edit existing message: {e}")
        
        msg = await channel.send(embed=embed, view=view)
        self.control_message_id = msg.id
        self.current_embed_message = msg
        self.save_state()

    async def play_radio(self, radio_id: str, interaction: discord.Interaction = None):
        """تشغيل الإذاعة"""
        voice_client = None
        for guild in self.bot.guilds:
            if guild.voice_client:
                voice_client = guild.voice_client
                break
        
        if not voice_client or not voice_client.is_connected():
            return
        
        radio = self.radio_stations.get(radio_id)
        if not radio:
            return
        
        # ✅ تحديث الحالة
        self.current_radio = radio_id
        self.current_mode = "radio"
        self.is_radio_playing = True  # ✅ علامة أن الإذاعة شغالة
        
        if voice_client.is_playing():
            voice_client.stop()
            await asyncio.sleep(0.5)
        
        try:
            source = discord.FFmpegPCMAudio(radio["url"], **self.ffmpeg_options)
            
            def after_playing(error):
                if error:
                    print(f"Radio error: {error}")
                else:
                    self.is_playing = False
                    self.is_radio_playing = False
                    self.save_state()
            
            voice_client.play(source, after=after_playing)
            self.is_playing = True
            
            if self.control_channel_id:
                channel = self.bot.get_channel(self.control_channel_id)
                if channel:
                    await self.send_control_panel(channel, interaction)
            
            self.save_state()
            
        except Exception as e:
            print(f"Error playing radio: {e}")

    async def play_surah(self, surah_number: int, reciter_id: str = None, interaction: discord.Interaction = None):
        """تشغيل سورة معينة من تلاوة قارئ محدد"""
        voice_client = None
        for guild in self.bot.guilds:
            if guild.voice_client:
                voice_client = guild.voice_client
                break
        
        if not voice_client or not voice_client.is_connected():
            return
        
        # ✅ إلغاء حالة الإذاعة
        self.is_radio_playing = False
        
        if reciter_id and reciter_id in self.recitations:
            self.current_reciter = reciter_id
        
        current_reciter = self.recitations.get(self.current_reciter)
        if not current_reciter:
            return
        
        if surah_number < 1 or surah_number > 114:
            surah_number = 1
        
        self.current_surah = surah_number
        self.current_mode = "recitation"
        
        surah_url = f"{current_reciter['base_url']}{surah_number:03d}.mp3"
        
        if voice_client.is_playing():
            voice_client.stop()
            await asyncio.sleep(0.5)
        
        try:
            source = discord.FFmpegPCMAudio(surah_url, **self.ffmpeg_options)
            
            def after_playing(error):
                if error:
                    print(f"Recitation error: {error}")
                else:
                    self.is_playing = False
                    self.save_state()
                    # ✅ تشغيل السورة التالية فقط إذا كنا في وضع التلاوة وليس الإذاعة
                    if self.current_mode == "recitation" and not self.is_radio_playing:
                        asyncio.run_coroutine_threadsafe(
                            self.auto_next_surah(interaction),
                            self.bot.loop
                        )
            
            voice_client.play(source, after=after_playing)
            self.is_playing = True
            
            if self.control_channel_id:
                channel = self.bot.get_channel(self.control_channel_id)
                if channel:
                    await self.send_control_panel(channel, interaction)
            
            self.save_state()
            
        except Exception as e:
            print(f"Error playing surah: {e}")

    async def auto_next_surah(self, interaction: discord.Interaction = None):
        """تشغيل السورة التالية تلقائياً"""
        # ✅ التحقق من أننا في وضع التلاوة وليس الإذاعة
        if self.current_mode != "recitation" or self.is_radio_playing:
            return
        
        next_surah = self.current_surah + 1
        if next_surah > 114:
            next_surah = 1
        await self.play_surah(next_surah, interaction=interaction)

    async def ensure_voice_connection(self):
        """التأكد من اتصال البوت بالروم الصوتي"""
        guild = self.bot.get_guild(self.guild_id) if self.guild_id else None
        if not guild:
            guild = self.bot.guilds[0] if self.bot.guilds else None
            if guild:
                self.guild_id = guild.id
        
        if not guild:
            return False
        
        voice_client = guild.voice_client
        
        if voice_client and voice_client.channel:
            if voice_client.channel.id != self.voice_channel_target_id:
                target_channel = guild.get_channel(self.voice_channel_target_id)
                if target_channel:
                    await voice_client.move_to(target_channel)
            return True
        
        if not voice_client:
            target_channel = guild.get_channel(self.voice_channel_target_id)
            if target_channel:
                try:
                    await target_channel.connect(timeout=20.0, reconnect=True)
                    self.voice_channel_id = target_channel.id
                    return True
                except Exception as e:
                    print(f"⚠️ Could not join voice channel: {e}")
        
        return False

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        
        connected = await self.ensure_voice_connection()
        
        channel = self.bot.get_channel(self.control_channel_id)
        if channel:
            await self.send_control_panel(channel)
        
        if connected and self.current_mode == "recitation":
            await self.play_surah(self.current_surah, self.current_reciter)
        elif connected and self.current_mode == "radio":
            await self.play_radio(self.current_radio)
        elif connected:
            await self.play_surah(1, "minsh1387")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.bot.user.id:
            if after.channel is None:
                self.is_playing = False
                await asyncio.sleep(2)
                await self.ensure_voice_connection()
                if self.current_mode == "recitation":
                    await self.play_surah(self.current_surah, self.current_reciter)
                elif self.current_mode == "radio":
                    await self.play_radio(self.current_radio)
            
            elif before.channel != after.channel and after.channel is not None:
                self.voice_channel_id = after.channel.id

    @commands.command(name="quran")
    async def quran_command(self, ctx):
        """أمر تثبيت لوحة التحكم !quran"""
        channel = self.bot.get_channel(self.control_channel_id)
        if channel:
            await self.send_control_panel(channel)
            await ctx.send("✅ تم تحديث لوحة التحكم!", delete_after=5)
        else:
            await ctx.send("❌ لم يتم العثور على قناة التحكم!", delete_after=5)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """معالجة التفاعلات"""
        if not interaction.data:
            return
        
        if interaction.type == discord.InteractionType.component:
            custom_id = interaction.data.get("custom_id")
            
            if custom_id == "main_select":
                value = interaction.data.get("values")[0]
                
                if value.startswith("reciter_"):
                    reciter_id = value.replace("reciter_", "")
                    if reciter_id in self.recitations:
                        reciter_name = self.recitations[reciter_id]["name"]
                        await interaction.response.send_message(f"🕌 تم التبديل إلى: {reciter_name}", ephemeral=True)
                        await self.play_surah(self.current_surah, reciter_id, interaction)
                        await self.send_control_panel(interaction.channel, interaction)
                    return
                
                if value.startswith("radio_"):
                    radio_id = value.replace("radio_", "")
                    if radio_id in self.radio_stations:
                        radio_name = self.radio_stations[radio_id]["name"]
                        await interaction.response.send_message(f"📻 تم تشغيل: {radio_name}", ephemeral=True)
                        await self.play_radio(radio_id, interaction)
                        await self.send_control_panel(interaction.channel, interaction)
                    return
                
                return

async def setup(bot: commands.Bot):
    await bot.add_cog(QuranRadio(bot))
    print("✅ Quran Radio loaded with Select Menu only successfully!")
