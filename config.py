import base64

# توكن البوت
BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"

# معرفات القنوات
AZKAR_CHANNEL_ID = 12345678 حط الايدي بتاع الشات بتاع الاذكار
QURAN_CONTROL_CHANNEL_ID = 12345678 حط الايدي بتاع الفويس 
QURAN_VOICE_CHANNEL_ID = 12345678 حط الايدي بتاع الفويس

# الفاصل بين الأذكار بالدقائق
AZKAR_INTERVAL = 60

# الألوان
COLOR_MAIN = 0xFF0000 هنا الالوان

# روابط الصور
AZKAR_IMAGE = "حط الرابط بتاع الصوره الي انت عايزها تتبعت مع الاذكار"

QURAN_IMAGE = "حط الرابط للصوره اللي انت عايزها هنا الصوره الي هتكون موجوده في لوحه التححكم بتاعت القران"

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
