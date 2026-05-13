import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from tqdm import tqdm

# خواندن متغیرهای محیطی
api_id      = int(os.getenv('API_ID'))
api_hash    = os.getenv('API_HASH')
session_str = os.getenv('TELETHON_SESSION')
links_raw   = os.getenv('TEL_LINKS', '')
split_mb    = int(os.getenv('SPLIT_THRESH_MB', '0'))
subfolder   = os.getenv('SUBFOLDER', '').strip()
prefix      = os.getenv('CUSTOM_FILENAME', '').strip()

# آماده‌سازی پوشه خروجی
base_out = 'downloads'
out_dir = os.path.join(base_out, subfolder) if subfolder else base_out
os.makedirs(out_dir, exist_ok=True)

async def main():
    # لاگین غیرتعاملی با StringSession
    client = TelegramClient(StringSession(session_str), api_id, api_hash)
    await client.start()

    # فهرست لینک‌ها
    links = [l.strip() for l in links_raw.split() if l.strip()]
    total = len(links)
    for idx, link in enumerate(links, start=1):
        print(f"[{idx}/{total}] Processing: {link}")
        try:
            msgs = await client.get_messages(link, limit=1)
            if not msgs or not msgs[0].media:
                print("  ⚠️ No media found.")
                continue

            media = msgs[0].media
            # تعیین نام فایل
            orig_name = getattr(msgs[0].file, 'name', None) or f'media_{idx}'
            filename = prefix + orig_name
            dest = os.path.join(out_dir, filename)

            # دانلود
            print(f"  ⬇️ Downloading to {dest}")
            await client.download_media(media, file=dest)

            # در صورت نیاز به تقسیم فایل:
            if split_mb > 0 and os.path.getsize(dest) > split_mb * 1024**2:
                print(f"  🔀 File exceeds {split_mb} MB – split not implemented.")
                # <در اینجا می‌توانید منطق split را اضافه کنید>
        except Exception as e:
            print("  ❌ Error:", e)

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
