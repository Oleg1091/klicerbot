import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

# ================== НАСТРОЙКИ ==================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("STRING_SESSION")
BOT = "patrickstarsrobot"
INTERVAL = 8 * 60  # 8 минут
# ===============================================

async def main():
    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        await client.start()
        bot = await client.get_entity(BOT)
        print("✅ Подключено! Автокликер запущен с обходом капчи")

        while True:
            try:
                await client.send_message(bot, "/start")
                await asyncio.sleep(3)

                # Нажимаем ✨ Кликер
                messages = await client.get_messages(bot, limit=12)
                clicked = False
                for msg in messages:
                    if msg.buttons:
                        for r_idx, row in enumerate(msg.buttons):
                            for b_idx, btn in enumerate(row):
                                if btn.text.strip() == "✨ Кликер" or "Кликер" in btn.text:
                                    await msg.click(r_idx, b_idx)
                                    print(f"✅ Нажата: {btn.text}")
                                    clicked = True
                                    break
                            if clicked: break
                    if clicked: break

                await asyncio.sleep(3.5)

                # Проверяем капчу и OK (6 попыток)
                for _ in range(6):
                    await asyncio.sleep(2)
                    messages = await client.get_messages(bot, limit=8)

                    for msg in messages:
                        text_lower = (msg.message or "").lower()
                        if "посчитай сумму" in text_lower or "сумму чисел" in text_lower:
                            try:
                                task = msg.message.split("чисел:")[1].split("=")[0].strip()
                                left, right = [int(x.strip()) for x in task.split("+")]
                                answer = left + right
                                print(f"🧮 Капча: {left} + {right} = {answer}")

                                if msg.buttons:
                                    for r_idx, row in enumerate(msg.buttons):
                                        for b_idx, btn in enumerate(row):
                                            if btn.text.strip().isdigit() and int(btn.text.strip()) == answer:
                                                await msg.click(r_idx, b_idx)
                                                print(f"✅ Выбрана правильная кнопка: {btn.text}")
                                                await asyncio.sleep(3)
                                                break
                            except: pass

                        # Нажимаем OK / Понял
                        if msg.buttons:
                            for r_idx, row in enumerate(msg.buttons):
                                for b_idx, btn in enumerate(row):
                                    t = btn.text.strip().lower()
                                    if t in ["ok", "ок", "понял", "закрыть", "готово"]:
                                        await msg.click(r_idx, b_idx)
                                        print(f"✅ Нажато: {btn.text}")
                                        await asyncio.sleep(1.5)
                                        break

                await client.send_message(bot, "/start")
                print(f"⏳ Следующий цикл через 8 минут")
                await asyncio.sleep(INTERVAL)

            except FloodWaitError as e:
                await asyncio.sleep(e.seconds + 10)
            except Exception as e:
                print(f"Ошибка: {e}")
                await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
