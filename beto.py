###########################
## Guido Dipietro | 2020 ##
###########################

import auxf

import keepalive
import discord
from discord.ext.commands import Bot
import random
import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from unidecode import unidecode
import datetime

##### FIREBASE #####

cred = credentials.Certificate('firebase_adminsdk.json')
firebase_admin.initialize_app(cred, {
	'databaseURL': 'https://discord-bot-2ae41.firebaseio.com/'
})
ref = db.reference()

##### DICTS #####

habilidades = {
	"acordate": 'Se usa así: ```beto acordate "algo" "definicion"``` con las comillas',
	"contame": 'Se usa así: ```beto contame "cosa"``` con las comillas. Si querés saber qué sé sobre vos, decime ```beto contame todo```',
	"regex": "Se usa así: ```beto regex REGEX PALABRA``` y yo te digo si la ER que pongas en REGEX anda con PALABRA.",
	"agendate": 'Se usa así: ```beto agendate dd/mm <examen>? "nombreEvento" "descripción"?```',
	"mes": "Se usa así: ```beto mes ([0-9] | 10 | 11 | 12)``` Te muestro todo lo que queda en el mes.\nO si querés todo lo del mes:```beto mes ([0-9] | 10 | 11 | 12) completo```",
	"semana": "Se usa así: ```beto semana (próxima|entera)?``` Te muestro todo lo que queda en la semana, o en la semana entera, o en la próxima, según me digas."
}

##### DISCORD #####

client = Bot(command_prefix='beto ')
client.remove_command("help") # to overwrite this command (read on)

@client.event
async def on_ready():
	await client.change_presence(\
		activity=discord.Activity(\
			type=discord.ActivityType.listening, name="Gauss"))

# ON MESSAGE #
@client.event
async def on_message(message):
	txt = unidecode(message.content.strip()) # Remove trailing spaces + normalize string
	# To prevent the dumb
	if message.author == client.user:
		return

	##### TESTING EMBEDS #####

	# if txt.split()[0]=="pelao":
	# 	embedVar = discord.Embed(
	# 		title = "Testing Embeds",
	# 		colour = discord.Colour.red(),
	# 		description = "This is an Embed I'm using to test my face",
	# 		footer = "What about a footer?",
	# 	)
	# 	embedVar.set_image(url="https://www.worldcubeassociation.org/uploads/user/avatar/2017TUNG13/1579536591.jpeg")
	# 	embedVar.add_field(
	# 		name="Field 1, not inline",
	# 		value="Val 1",
	# 		inline=False
	# 	)
	# 	embedVar.add_field(
	# 		name="Field 2, YES inline",
	# 		value="Val 2",
	# 		inline=True
	# 	)
	# 	await message.channel.send(embed=embedVar)

	######################################

	# When ping (cheap solution!)
	pings = ["<@!752961387432509490>","<@752961387432509490>"]
	if any([x in txt.split() for x in pings]):
		await message.add_reaction(auxf.random_emoji())
		await message.channel.send(message.author.mention)
	# When hi
	if auxf.has(txt, ["beto","betuski"]) and auxf.has(txt, [
		"como andamo",
		"hola",
		"buenas",
		"como anda",
		"como va",
		"todo bien",
		"como andas",
		"todo en orden"
	]):
		saludos = [
			"Acá andamo",
			"Re discretos hoy",
			"Todo en orden parcial?",
			"Buenass...",
			"Copiá y después hablamos."
		]
		random.seed()
		await message.add_reaction('👋')
		await message.channel.send(random.choice(saludos))
	# When thanks
	if auxf.has(txt, ["beto","betuski"]) and auxf.has(txt, [
		"genial",
		"buenisimo",
		"gracias",
		"valeu",
		"obrigado",
		"thanks",
		"ty",
		"sos un capo",
		"excelente",
		"que capo"
	]):
		denada = [
			"A la orden...!",
			"No prob.",
			"Para eso me pagan, querido.",
			"Noo, gracias a vos"
		]
		random.seed()
		await message.add_reaction('👌')
		await message.channel.send(random.choice(denada))
	# To run commands afterwards
	await client.process_commands(message)

############################
######### COMMANDS #########
############################

# Decorador para que guarde los IDs de los MSGs solamente
# cuando son comandos (y que sigan siendo comandos!)
def comando(func):
	@client.command(name=func.__name__)
	async def wrapper(ctx, *args, **kwargs):
		# Save to DB to delete it if prompted to
		auxf.save_msg_id(
			ref,
			_id=ctx.message.id,
			channel=ctx.message.channel.id,
			author=ctx.message.author.id
			)
		# Actually execute the command
		await func(ctx, *args, **kwargs)
	return wrapper

@comando
# beto help <funcname>?
# Lists all functions, or lists func doc
async def help(ctx, arg=None):
	if arg:
		await ctx.send(habilidades[arg])
	else:
		random.seed()
		await ctx.send(f"Funciones: ```{', '.join(habilidades.keys())}```")
		await ctx.send(f"Si querés ayuda con una función, decime: beto help <nombreFunc>. Y si no... {auxf.bardear()}")

@comando
# beto agendate <dd>/<mm> <exam>? <event> <desc>?
async def agendate(ctx, arg1, arg2, arg3=None, arg4=None):
	if auxf.proper_date(arg1):
		if unidecode(arg2).upper()=="EXAMEN":
			date, event, desc = arg1, arg3, arg4
			auxf.save_to_date(ref, date, event, desc, isexam=True)

			devolucion = f'EXAMEN: ```"{event}"```'
			if desc:
				devolucion = f'EXAMEN: ```"{event}": {desc}```'
		else:
			date, event, desc = arg1, arg2, arg3
			auxf.save_to_date(ref, date, event, desc, isexam=False)

			devolucion = f'evento: ```"{event}"```'
			if desc:
				devolucion = f'evento: ```"{event}": {desc}```'

		await ctx.send(f"Agendado para el día {date} el {devolucion}")
	else:
		await ctx.send(habilidades["agendate"])

@comando
# beto mes <number> completo?
# Returns events this month
async def mes(ctx, month_n, completo=None):
	if month_n in [str(x) for x in range(1,13)]: # Comparing strs instead of int to avoid silly bugs
		start = "1"
		if (completo is None) and (month_n == datetime.datetime.today().month):
			start = str(datetime.datetime.today().day)
		rta = auxf.get_month(ref, month_n, start, "32")

		if rta:
			if completo:
				await ctx.send("Todos los eventos del mes:")
			else:
				await ctx.send("Lo que queda del mes:")
			await auxf.send_parsed_rta(ctx, rta, month_n)
		else:
			await ctx.send("Nada para ese mes.")
	else:
		await ctx.send("No existe ese mes XD")

@comando
# beto semana (completa|proxima)?
# Returns events this week
# WEEKS START ON MONDAYS
async def semana(ctx, completa=None):
	today = datetime.datetime.today()
	# Determine period (this week (ALL), this week (REMAINING), next week)
	# Rest of the week
	if completa is None:
		start, end = today.day, (today.day-today.weekday()+6)
		title = "Lo que queda de la semana:"
	# Next week
	elif unidecode(completa).upper() in ["PROXIMA","SIGUIENTE"]:
		today = today + datetime.timedelta(days = 7 - today.weekday())
		print(today)
		start, end = today.day, today.day+6
		title = "Toda la semana que viene:"
	# All of this week
	else:
		start = (today - datetime.timedelta(days=today.weekday())).day # Closest past Monday
		end = start + 6 # Closest future Sunday
		title = "Toda la semana corriente:"

	rta = auxf.get_month(ref, str(today.month), str(start), str(end))
	if rta:
		await ctx.send(title)
		await auxf.send_parsed_rta(ctx, rta, today.month)
	else:
		await ctx.send("Nada para mostrar.")

@comando
# beto acordate "cosa" "defin"
# Saves something to the DB with a string key
async def acordate(ctx, cosa, defin):
	cosa = unidecode(cosa).upper() # Normalize key (all caps and no tildes)
	try:
		ref.child("datazos").child(str(ctx.author.id)).update({
			cosa: defin
		})
		await ctx.send("Listo, ya me lo acuerdo.")
	except:
		await ctx.send(habilidades["acordate"])

@comando
# beto contame <todo | "cosa"> raw
# Retrieves something from the DB with a string key
async def contame(ctx, arg1, raw=None):
	if arg1=="todo":
		todo = ref.child("datazos").child(str(ctx.author.id)).get()
		if todo is None:
			await ctx.send(f"No me contaste nada todavía. {auxf.bardear()}")
			await ctx.send(f'Contame algo así: ```beto acordate "cosa" "definicion" (con las comillas)```')
		else:
			todo = ", ".join([x.capitalize() for x in todo.keys()])
			await ctx.send("Me contaste sobre todo esto:")
			await ctx.send(f"```{todo}```")
			await ctx.send('Para preguntarme sobre algo de eso, decime ```beto contame "cosa"```')
	else:
		try:
			cosa = unidecode(arg1).upper()
			defin = ref.child("datazos").child(str(ctx.author.id)).get()[cosa]
			await ctx.send(cosa.capitalize()+":")
			await ctx.send(f"{defin}") if raw else await ctx.send(f"```{defin}```")
		except:
			await ctx.send(habilidades["contame"])

@comando
# beto regex <regex> <testword>
async def regex(ctx, reg, word):
	await ctx.send(f"Probando ```REGEX: {reg}``` con ```TEST: {word}```")
	match = re.search(reg, word)
	if match and match.group()==word:
		await ctx.send("Sip, anda.")
	else:
		await ctx.send("No anda, mi pana")

@comando
# beto wipecommands
async def wipecommands(ctx):
	await auxf.wipe_msgs(ref, ctx)

##### RUN #####

# Top-level security !!!!!1
with open("bot_key.txt","r+") as f:
	botkey = f.read()

keepalive.keepalive()   # Para que no se cierre
client.run(botkey)      # Run !