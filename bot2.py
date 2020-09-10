###########################
## Guido Dipietro | 2020 ##
###########################

from discord.ext.commands import Bot
import random
import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

##### FIREBASE #####

cred = credentials.Certificate('firebase_adminsdk.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://discord-bot-2ae41.firebaseio.com/'
})
ref = db.reference()

##### DICTS #####

materias = [
	"AM2",
	"Fisica1",
	"AdS",
	"Paradigmas",
	"Sintaxis"
]
habilidades = {
	"setfecha": "Se usa así: ```beto setfecha <recu>? <primero|segundo> <nombremateria> dd/mm```",
	"getfecha": "Se usa así: ```beto getfecha <recu>? <primero|segundo> <nombremateria>```",
	"materias": "Las materias que tengo son estas: " + ", ".join(materias),
	"acordate": 'Se usa así: ```beto acordate "algo" "definicion"``` con las comillas',
	"contame": 'Se usa así: ```beto contame "cosa"``` con las comillas. Si querés saber qué sé sobre vos, decime ```beto contame todo```'
}

##### AUX #####

# starts with (string, list of strings)
def starts(s, list):
	return any([s.startswith(x) for x in list])

# check if date is like dd/mm
def proper_date(s):
	match = re.search("[0-9]{1,2}/[0-9]{1,2}", s)
	return False if (match is None) else match.group()==s

# beto moment
def bardear():
	bardear = [
		"¿Te quedaste sin nasta?",
		"Tomate el palo.",
		"Se te ven las caries desde acá",
		"¿Quién te conoce?",
		"Estás en otras ligas, rubio.",
		"Pronóstico: TORMENTA de facha."
	]
	return random.choice(bardear)

def check_instancia(instancia):
	if instancia in ["primero","primer","1ero","1er","1"]: return 0
	elif instancia in ["segundo","2do","2"]: return 1
	return instancia

# Save date to Firebase + return msg (sent on command function)
# Excuse the Spanglish
def save_fecha(inst, mat, fecha, recu=False):
	recuOrNot = "parcial" if (not recu) else "recu del parcial"
	childRecu = "recus" if recu else "parciales"
	inst = check_instancia(inst)
	# If clean
	if (inst in [0,1]) and (mat in parciales.keys()) and (proper_date(fecha)):
		ref.child("fechas").child(childRecu).child(mat).update({
			str(inst+1): fecha
		})
		return f"Altoke: {recuOrNot} num. #{inst+1} de {mat} el día {fecha}. Así quedamo."
	# If dirty
	else:
		return habilidades["setfecha"]

# Get date from Firebase + return msg (sent on command function)
# Excuse the Spanglish x 2
def retrieve_fecha(inst, mat, recu=False):
	recuOrNot = "recu del " if recu else ""
	childRecu = "recus" if recu else "parciales"
	inst = check_instancia(inst)
	fecha = ref.child("fechas").child(childRecu).child(mat).child(str(inst+1)).get()

	if fecha is None:
		return f"No hay ninguna fecha cargada para el {recuOrNot}parcial num. #{inst+1} de {mat}..."
	else:
		return f"La fecha del {recuOrNot}parcial num. #{inst+1} de {mat} es el día {fecha}."

##### DISCORD #####

client = Bot(command_prefix='beto ')
client.remove_command("help") # to overwrite this command (read on)

# ON MESSAGE #
@client.event
async def on_message(message):
	txt = message.content.strip()
	tks = txt.split()
	# To prevent the dumb
	if message.author == client.user:
		return
	# When ping (cheap solution!)
	if "<@!752961387432509490>" in txt.split():
		await message.channel.send(message.author.mention)
	# When hi
	if ("beto" in txt) and starts(txt, ["hola","buenas","como anda","como va","todo bien"]):
		saludos = [
			"Acá andamo",
			"Re discretos hoy"
		]
		await message.channel.send(random.choice(saludos))
	# To run commands afterwards
	await client.process_commands(message)

############################
######### COMMANDS #########
############################

@client.command()
# beto help <funcname>?
# Lists all functions, or lists func doc
async def help(ctx, arg=None):
	if arg:
		await ctx.send(habilidades[arg])
	else:
		await ctx.send(f"Funciones:\n{', '.join(habilidades.keys())}")
		await ctx.send(f"Si querés ayuda con una función, decime: beto help <nombreFunc>. Y si no... {bardear()}")

@client.command()
# beto setfecha <recu>? <1ero|2do> <materia> <dd>/<mm>
# Sets date for parcial or recu
async def setfecha(ctx, arg1, arg2, arg3, arg4=None):
	recu = False if arg1!="recu" else True
	inst, mat, fecha = arg1, arg2, arg3
	if recu and arg4:
		inst, mat, fecha = arg2, arg3, arg4
	if proper_date(fecha):
		await ctx.send(save_fecha(inst, mat, fecha, recu=recu))
	else:
		await ctx.send("Le pifiaste en algo, master")
		await ctx.send(habilidades["setfecha"])

@client.command()
# beto getfecha <recu>? <1ero|2do> <materia>
# Retrieves date for parcial or recu
async def getfecha(ctx, arg1, arg2, arg3=None):
	recu = False if arg1!="recu" else True
	inst, mat = arg1, arg2
	if recu and arg3:
		inst, mat = arg2, arg3
	await ctx.send(retrieve_fecha(inst, mat, recu=recu))

@client.command()
# beto acordate "cosa" "defin"
# Saves something to the DB with a string key
async def acordate(ctx, cosa, defin):
	cosa = cosa.upper()
	try:
		ref.child("datazos").child(str(ctx.author.id)).update({
			cosa: defin
		})
		await ctx.send("Listo, ya me lo acuerdo.")
	except:
		await ctx.send(habilidades["acordate"])

@client.command()
# beto contame <todo | "cosa">
# Retrieves something from the DB with a string key
async def contame(ctx, arg1):
	if arg1=="todo":
		todo = ref.child("datazos").child(str(ctx.author.id)).get()
		if todo is None:
			await ctx.send(f"No me contaste nada todavía. {bardear()}")
			await ctx.send(f'Contame algo así: ```beto acordate "cosa" "definicion" (con las comillas)```')
		else:
			todo = ", ".join([x.capitalize() for x in todo.keys()])
			await ctx.send("Me contaste sobre todo esto:")
			await ctx.send(f"```{todo}```")
			await ctx.send('Para preguntarme sobre algo de eso, decime ```beto contame "cosa"```')
	else:
		try:
			cosa = arg1.upper()
			defin = ref.child("datazos").child(str(ctx.author.id)).get()[cosa]
			await ctx.send(cosa.capitalize()+":")
			await ctx.send(f"```{defin}```")
		except:
			await ctx.send(habilidades["contame"])

##### RUN #####

# Top-level security !!!!!
with open("bot_key.txt","r+") as f:
	botkey = f.read()

client.run(botkey)
