import discord
from discord.ext import commands
import sqlite3
import datetime
from googletrans import Translator

# 初始化 bot 和翻譯器
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
translator = Translator()

# 建立 SQLite 資料庫
conn = sqlite3.connect("points.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, points INTEGER, last_time TEXT)")
conn.commit()

# 發言就加點數（限1分鐘1次）
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    user_id = str(message.author.id)
    now = datetime.datetime.now()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        last_time = datetime.datetime.fromisoformat(result[2])
        if (now - last_time).seconds >= 60:
            cursor.execute("UPDATE users SET points = points + 1, last_time = ? WHERE user_id = ?", (now.isoformat(), user_id))
            conn.commit()
    else:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (user_id, 1, now.isoformat()))
        conn.commit()

    await bot.process_commands(message)

# 查詢點數指令
@bot.command()
async def 點數(ctx):
    user_id = str(ctx.author.id)
    cursor.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        await ctx.send(f"{ctx.author.mention} 你目前有 {result[0]} 點！")
    else:
        await ctx.send(f"{ctx.author.mention} 你還沒有點數，快來聊天吧！")

# 翻譯：英 → 中
@bot.command()
async def 翻中(ctx, *, text):
    result = translator.translate(text, dest='zh-tw')
    await ctx.send(f"翻譯（英 → 中）：{result.text}")

# 翻譯：中 → 英
@bot.command()
async def 翻英(ctx, *, text):
    result = translator.translate(text, dest='en')
    await ctx.send(f"翻譯（中 → 英）：{result.text}")

# 啟動 BOT（從環境變數讀取 Token）
import os
TOKEN = os.getenv("BOT_TOKEN")
bot.run(TOKEN)
