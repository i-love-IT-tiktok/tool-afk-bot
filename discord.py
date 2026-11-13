import discord
from discord.ext import commands, tasks
import os

# ===== CẤU HÌNH =====
BOT_TOKEN = "YOUR_BOT_TOKEN"      # Token bot của bạn
GUILD_ID  = 123456789012345678    # Server ID
VOICE_ID  = 987654321098765432    # Voice Channel ID

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def connect_voice():
    """Kết nối (hoặc reconnect) vào voice channel chỉ định"""
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        print(f"[LỖI] Không tìm thấy server ID {GUILD_ID} — bot đã được mời vào server chưa?")
        return

    channel = guild.get_channel(VOICE_ID)
    if channel is None:
        print(f"[LỖI] Không tìm thấy voice channel ID {VOICE_ID}")
        return

    vc = guild.voice_client
    if vc and vc.is_connected():
        if vc.channel.id == VOICE_ID:
            return  # Đã ở đúng kênh
        await vc.move_to(channel)
        print(f"[OK] Đã chuyển sang kênh: {channel.name}")
    else:
        await channel.connect(self_mute=True, self_deaf=True, timeout=30, reconnect=True)
        print(f"[OK] Đã tham gia kênh: {channel.name} (self-mute + self-deaf)")


@bot.event
async def on_ready():
    print(f"Đã đăng nhập: {bot.user} (ID: {bot.user.id})")
    await connect_voice()
    if not keep_alive.is_running():
        keep_alive.start()


@tasks.loop(seconds=20)
async def keep_alive():
    """Kiểm tra mỗi 20s, nếu rớt voice thì tự vào lại"""
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        return
    vc = guild.voice_client
    if vc is None or not vc.is_connected():
        print("[WARN] Mất kết nối voice, đang thử reconnect...")
        try:
            await connect_voice()
        except Exception as e:
            print(f"[LỖI] Reconnect thất bại: {e}")


@bot.event
async def on_voice_state_update(member, before, after):
    """Nếu bot bị kick khỏi voice hoặc bị chuyển kênh → vào lại ngay"""
    if member.id != bot.user.id:
        return
    if after.channel is None:
        print("[WARN] Bot bị ngắt khỏi voice, đang vào lại...")
        try:
            await connect_voice()
        except Exception as e:
            print(f"[LỖI] Vào lại thất bại: {e}")


# ===== LỆNH THỦ CÔNG =====
@bot.command()
async def join(ctx):
    await connect_voice()
    await ctx.send("Đã vào voice ✅")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Đã rời voice 👋")

@bot.command()
async def status(ctx):
    vc = ctx.guild.voice_client
    if vc and vc.is_connected():
        await ctx.send(f"Đang treo tại: **{vc.channel.name}** | mute={vc.self_mute}, deaf={vc.self_deaf}")
    else:
        await ctx.send("Bot hiện không ở trong voice nào.")


bot.run(BOT_TOKEN)
