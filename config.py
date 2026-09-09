"""
config.py - ملف الإعدادات
"""

import base64

# توكن البوت
BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"

# معرفات القنوات
AZKAR_CHANNEL_ID = 1471987981299749004
QURAN_CONTROL_CHANNEL_ID = 1471987630399819908
QURAN_VOICE_CHANNEL_ID = 1471987630399819908

# الفاصل بين الأذكار بالدقائق
AZKAR_INTERVAL = 60

# الألوان
COLOR_MAIN = 0xFF0000

# روابط الصور
AZKAR_IMAGE = "https://cdn.discordapp.com/attachments/1462058133835747381/1543349993082200224/Gemini_Generated_Image_kcocpakcocpakcoc.png?ex=6a948c30&is=6a933ab0&hm=0470ff7a199da81de3a4ce512ba616c7431fe5e1bfd46d1e53091865a71d49e0&"

QURAN_IMAGE = "https://cdn.discordapp.com/attachments/1462058133835747381/1544855500066131998/ChatGPT_Image_Sep_3_2026_02_42_59_AM.png?ex=6a9a064d&is=6a98b4cd&hm=9a8b3f482de20c29767b5ca9efacf041a3b511dd90845cd868ca92fc3cbba851&"

# إعدادات الصوت
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -vn',
    'options': '-b:a 128k'
}

# النص
_HIDDEN = "Q29weXJpZ2h0ICBATU9MT1RPRiDwn5Cp"
FOOTER_TEXT = base64.b64decode(_HIDDEN).decode('utf-8')

if FOOTER_TEXT != "Copyright  @MOLOTOF 👑":
    FOOTER_TEXT = "Copyright  @MOLOTOF 👑"
