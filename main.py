import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from fastapi import FastAPI
import uvicorn

# --- МИНИ-СЕРВЕР ДЛЯ RENDER ---
app = FastAPI()

@app.get("/")
async def root():
    return {"status": "running"}

async def run_web_server():
    # Render автоматически назначает PORT, мы его считываем
    port = int(os.environ.get("PORT", 10000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    await server.serve()

# --- ВАШ ОСНОВНОЙ КОД БОТА ---
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("STRING_SESSION", "")
BOT = "patrickstarsrobot"
INTERVAL = 8 * 60  # 8 минут

async def run_bot():
    if not API_ID or not API_HASH or not SESSION_STRING:
        print("❌ ОШИБКА: Переменные окружения (API_ID, API_HASH, STRING_SESSION) не настроены!")
        return

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
                                if "Кликер" in btn.text:
                                    await msg.click(r_idx, b_idx)
                                    print(f"✅ Нажата: {btn.text}")
                                    clicked = True
                                    break
                            if clicked: break
                    if clicked: break

                await asyncio.sleep(3.5)

                # Проверка капчи (6 попыток)
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
                                                print(f"✅ Капча решена: {btn.text}")
                                                await asyncio.sleep(3)
                                                break
                            except Exception as e:
                                print(f"Ошибка парсинга капчи: {e}")

                        # Нажимаем OK
                        if msg.buttons:
                            for r_idx, row in enumerate(msg.buttons):
                                for b_idx, btn in enumerate(row):
                                    t = btn.text.strip().lower()
                                    if t in ["ok", "ок", "понял", "закрыть", "готово"]:
                                        await msg.click(r_idx, b_idx)
                                        print(f"✅ Нажато: {btn.text}")
                                        await asyncio.sleep(1.5)
                                        break

                print(f"⏳ Цикл завершен. Спим {INTERVAL/60} мин.")
                await asyncio.sleep(INTERVAL)

            except FloodWaitError as e:
                print(f"⚠️ FloodWait: ждем {e.seconds} сек.")
                await asyncio.sleep(e.seconds + 10)
            except Exception as e:
                print(f"🔴 Ошибка: {e}")
                await asyncio.sleep(30)

# --- ЗАПУСК ВСЕГО ВМЕСТЕ ---
async def start():
    # Запускаем бота и веб-сервер параллельно
    await asyncio.gather(
        run_bot(),
        run_web_server()
    )

if __name__ == "__main__":
    asyncio.run(start())
