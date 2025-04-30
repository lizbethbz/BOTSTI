import os
import json
from datetime import datetime
import asyncio

RECORDATORIOS_FILE = "recordatorios.json"
recordatorios = []

def cargar_recordatorios():
    global recordatorios
    if not os.path.exists(RECORDATORIOS_FILE):
        with open(RECORDATORIOS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)
    with open(RECORDATORIOS_FILE, "r", encoding="utf-8") as f:
        try:
            recordatorios = json.load(f)
        except json.JSONDecodeError:
            recordatorios = []

def guardar_recordatorios():
    with open(RECORDATORIOS_FILE, "w", encoding="utf-8") as f:
        json.dump(recordatorios, f, indent=4)

async def agregar_recordatorio(bot, ctx, args):
    if len(args) < 2:
        await ctx.send("Uso correcto: `!recordar 12:00 Actividad` o `!recordar 2025-05-01 12:00 Actividad`")
        return

    if len(args[0]) == 5 and ":" in args[0]:
        fecha = datetime.now().strftime("%d-%m-%Y")
        hora = args[0]
        actividad = " ".join(args[1:])
    else:
        fecha = args[0]
        hora = args[1]
        actividad = " ".join(args[2:])

    try:
        datetime.strptime(f"{fecha} {hora}", "%d-%m-%Y %H:%M")
    except ValueError:
        await ctx.send("Formato inválido. Usa `DD-MM-YYYY HH:MM`.")
        return

    recordatorios.append({
        "fecha": fecha,
        "hora": hora,
        "actividad": actividad,
        "usuario": ctx.author.id,
        "canal": ctx.channel.id
    })
    guardar_recordatorios()
    await ctx.send(f"✅ Recordatorio guardado para {fecha} a las {hora}.")

async def ver_recordatorios(bot, ctx):
    if not recordatorios:
        await ctx.send("No hay recordatorios.")
        return

    mensaje = "**Recordatorios:**\n"

    for i, r in enumerate(recordatorios, start=1):
        usuario = bot.get_user(r["usuario"])
        mensaje += f"**{i}.** {r['fecha']} {r['hora']} - {r['actividad']} (de {usuario.display_name if usuario else 'Desconocido'})\n"
    await ctx.send(mensaje)

async def editar_recordatorio(bot, ctx, numero, nueva_actividad):
    if numero < 1 or numero > len(recordatorios):
        await ctx.send("Número inválido.")
        return

    recordatorios[numero - 1]["actividad"] = nueva_actividad
    guardar_recordatorios()
    await ctx.send(f"Recordatorio {numero} actualizado.")

async def borrar_recordatorio(bot, ctx, numero):
    if numero < 1 or numero > len(recordatorios):
        await ctx.send("Número inválido.")
        return

    eliminado = recordatorios.pop(numero - 1)
    guardar_recordatorios()
    await ctx.send(f"Recordatorio eliminado: {eliminado['actividad']}")

async def verificar_recordatorios(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        ahora = datetime.now()
        fecha_actual = ahora.strftime("%d-%m-%Y")
        hora_actual = ahora.strftime("%H:%M")
        pendientes = [r for r in recordatorios if r["fecha"] <= fecha_actual and r["hora"] <= hora_actual]
        for r in pendientes:
            canal = bot.get_channel(r["canal"])
            try:
                usuario = await bot.fetch_user(r["usuario"])
            except:
                usuario = None
            if canal and usuario:
                await canal.send(f"{usuario.mention}, recordatorio: {r['actividad']}")
                recordatorios.remove(r)
                guardar_recordatorios()
        await asyncio.sleep(30)
