import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TRELLO_API_KEY")
TOKEN = os.getenv("TRELLO_TOKEN")

async def obtener_tableros(session):
    url = "https://api.trello.com/1/members/me/boards"
    params = {'key': API_KEY, 'token': TOKEN, 'fields': 'name,url'}
    async with session.get(url, params=params) as response:
        return await response.json()

async def obtener_listas(tablero_id, session):
    url = f"https://api.trello.com/1/boards/{tablero_id}/lists"
    params = {'key': API_KEY, 'token': TOKEN}
    async with session.get(url, params=params) as response:
        return await response.json()

async def obtener_tarjetas(lista_id, session):
    url = f"https://api.trello.com/1/lists/{lista_id}/cards"
    params = {'key': API_KEY, 'token': TOKEN}
    async with session.get(url, params=params) as response:
        return await response.json()

async def obtener_checklist(tarjeta_id, session):
    url = f"https://api.trello.com/1/cards/{tarjeta_id}/checklists"
    params = {'key': API_KEY, 'token': TOKEN}
    async with session.get(url, params=params) as response:
        return await response.json()
    
async def menu(ctx):
    def check(m): return m.author == ctx.author and m.channel == ctx.channel

    tablero_actual = None
    lista_actual = None
    tarjeta_actual = None

    async with aiohttp.ClientSession() as session:
        while True:
            await ctx.send(
                "**¿Qué quieres hacer?**\n"
                "1️⃣ Ver tableros\n"
                "2️⃣ Ver listas de un tablero\n"
                "3️⃣ Ver tarjetas de una lista\n"
                "4️⃣ Ver checklist de una tarjeta\n"
                "🔄 Escribe `reset` para borrar selección actual\n"
                "❌ Escribe `salir` para terminar."
            )

            try:
                respuesta = await ctx.bot.wait_for('message', timeout=60, check=check)
            except:
                await ctx.send("Tiempo agotado. Sesión cerrada.")
                return

            opcion = respuesta.content.strip().lower()

            if opcion == "salir":
                await ctx.send("Sesión cerrada.")
                break

            if opcion == "reset":
                tablero_actual = lista_actual = tarjeta_actual = None
                await ctx.send("Selección actual reiniciada.")
                continue

            if opcion == "1":
                tableros = await obtener_tableros(session)
                mensaje = "**Tableros disponibles:**\n" + "\n".join(f"- [{t['name']}]({t['url']})" for t in tableros)
                await ctx.send(mensaje)

            elif opcion == "2":
                if not tablero_actual:
                    await ctx.send("Escribe el nombre del tablero:")
                    respuesta = await ctx.bot.wait_for('message', timeout=60, check=check)
                    nombre_tablero = respuesta.content.strip()

                    tableros = await obtener_tableros(session)
                    tablero_actual = next((t for t in tableros if t['name'].lower() == nombre_tablero.lower()), None)

                    if not tablero_actual:
                        await ctx.send("Tablero no encontrado.")
                        continue

                listas = await obtener_listas(tablero_actual['id'], session)
                mensaje = f"**Listas en {tablero_actual['name']}:**\n" + "\n".join(f"- {l['name']}" for l in listas)
                await ctx.send(mensaje)

            elif opcion == "3":
                if not tablero_actual:
                    await ctx.send("Primero selecciona un tablero usando la opción 2.")
                    continue

                if not lista_actual:
                    listas = await obtener_listas(tablero_actual['id'], session)
                    await ctx.send("Escribe el nombre de la lista:")
                    respuesta = await ctx.bot.wait_for('message', timeout=60, check=check)
                    nombre_lista = respuesta.content.strip()

                    lista_actual = next((l for l in listas if l['name'].lower() == nombre_lista.lower()), None)
                    if not lista_actual:
                        await ctx.send("Lista no encontrada.")
                        continue

                tarjetas = await obtener_tarjetas(lista_actual['id'], session)
                mensaje = "**Tarjetas en la lista:**\n" + "\n".join(f"- {t['name']}" for t in tarjetas)
                await ctx.send(mensaje)

            elif opcion == "4":
                if not lista_actual:
                    await ctx.send("Primero selecciona una lista usando la opción 3.")
                    continue

                if not tarjeta_actual:
                    tarjetas = await obtener_tarjetas(lista_actual['id'], session)
                    await ctx.send("Escribe el nombre de la tarjeta:")
                    respuesta = await ctx.bot.wait_for('message', timeout=60, check=check)
                    nombre_tarjeta = respuesta.content.strip()

                    tarjeta_actual = next((t for t in tarjetas if t['name'].lower() == nombre_tarjeta.lower()), None)
                    if not tarjeta_actual:
                        await ctx.send("Tarjeta no encontrada.")
                        continue

                checklist = await obtener_checklist(tarjeta_actual['id'], session)
                if not checklist:
                    await ctx.send("Esta tarjeta no tiene checklist.")
                    continue

                mensaje = "**Checklist:**\n"
                for item in checklist[0]['checkItems']:
                    estado = "✔️" if item['state'] == 'complete' else "❌"
                    mensaje += f"- {estado} {item['name']}\n"
                await ctx.send(mensaje)

            else:
                await ctx.send("Opción inválida.")


from discord.ext import commands

@commands.command()
async def trello(ctx):
    await menu(ctx)

def setup(bot):
    bot.add_command(trello)

