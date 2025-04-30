import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import os

import recordatorios
import trello

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MiBot(commands.Bot):
    async def setup_hook(self):
        self.loop.create_task(recordatorios.verificar_recordatorios(self))

bot = MiBot(command_prefix="!", intents=intents)

trello.setup(bot)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    recordatorios.cargar_recordatorios()

@bot.command()
async def recordar(ctx, *args):
    await recordatorios.agregar_recordatorio(bot, ctx, args)

@bot.command()
async def ver(ctx):
    await recordatorios.ver_recordatorios(bot, ctx)

@bot.command()
async def editar(ctx, numero: int, *, nueva_actividad):
    await recordatorios.editar_recordatorio(bot, ctx, numero, nueva_actividad)

@bot.command()
async def borrar(ctx, numero: int):
    await recordatorios.borrar_recordatorio(bot, ctx, numero)

@bot.command()
async def trello_cmd(ctx):
    await trello.menu(ctx)

bot.run(DISCORD_TOKEN)
