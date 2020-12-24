import re
import random
import datetime
import discord

##### AUX #####

def random_emoji():
	emojis = [
		'😏','😎','🤯','🤑','🤬',
		'🥶','👹','👺','👻','☠',
		'👾','👽','💩','🐍','🦑',
		'👁','👀','👅','👣','🦊'
	]
	random.seed()
	return random.choice(emojis)

# s has any of the words in list
def has(s, list):
	return any([x in s for x in list])

# self explanatory, come on
def starts(s, list):
	return any([s.startswith(x) for x in list])

# check if date is like dd/mm and valid
def proper_date(s):
	days = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
	match = re.search("[0-9]{1,2}/[0-9]{1,2}", s)
	if match is None:
		return False
	elif match.group()==s:
		day, month = s.split("/")
		return (1<=int(day)<=(days[int(month)])) and (1<=int(month)<=12)
	return False

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
	random.seed()
	return random.choice(bardear)

# Save message ID to the DB
def save_msg_id(ref, _id, channel, author):
	theChild = ref.child("MSGIDS").child(str(_id))
	if theChild:
		theChild.update({
			"channel": channel,
			"author": author
		})

# Deletes all messages based on the IDs in the DB
# (Only IDs from msgs that triggered beto commands are stored here)
async def wipe_msgs(ref, ctx):
	all_ids = ref.child("MSGIDS").get()
	for msgid, data in all_ids.items():
		if data["channel"]==ctx.channel.id:
			msg = await ctx.channel.fetch_message(msgid)
			await msg.add_reaction('😎')
			await msg.delete()
	ref.child("MSGIDS").set(
		{ msgid: data for msgid,data in all_ids.items() if data["channel"]!=ctx.channel.id}
	)

# Func used in "acordate" command
def save_to_date(ref, date, event, desc, isexam=False):
	d, m = date.split('/')
	level = "EXAMS" if isexam else "OTHERS"
	child = ref.child("calendar").child(m).child(d).child(level)

	if desc is None: desc = ""

	child.update({
		event.replace(".",""): desc # Los puntos no se admiten en nombres de claves, idk
	})

# Func used in "mes" command
def get_month(ref, month_n, start, end):
	return ref.child("calendar").child(month_n).order_by_key().start_at(start).end_at(end).get() # choo choo

# Converts list of EXAMS/OTHERS to pretty string to be sent as one single message
# Used in send_parsed_data()
def list_to_pretty_str(lista):
	out = ""
	for item in lista:
		date, (name, desc) = item # ily Python
		if len(desc)>0:
			out += f"- Día {date}: {name} ({desc})\n"
		else:
			out += f"- Día {date}: {name}\n"

	return out

# Yeets things in a list into an embed as fields
def list_to_embed_field(embed, lista):
	for thing in lista:
		value = thing[1][0]
		if thing[1][1]:
			value += f"\n({thing[1][1]})"
		embed.add_field(
			name=thing[0],
			value = value,
			inline=False
		)

# Builds and sends the EMBED if list is not empty
async def trysend_embed(ctx, lista, title="Embed", colour=discord.Colour.default()):
	if len(lista)>0:
		embed = discord.Embed(title = title, colour = colour)
		list_to_embed_field(embed, lista)
		await ctx.send(embed=embed)

# Send data of EXAMS/OTHERS read from the DB as a single EMBED
async def send_parsed_rta(ctx, rta, month_n):
	clean_exams = []
	clean_others = []
	# Retrieve all exams and others, to first send EXAMS then OTHERS in Discord
	for doc in rta.items():
		day, events = doc # doc = {"num", {"EXAMS"?: list, "OTHERS"?: list}}
		date = f"{day}/{month_n}"

		if "EXAMS" in events.keys():
			exams = events["EXAMS"]
			for exam in exams.items():
				clean_exams.append((date, exam))
		if "OTHERS" in events.keys():
			others = events["OTHERS"]
			for other in others.items():
				clean_others.append((date, other))
	print(clean_exams, clean_others)

	# Build the EMBEDS
	await trysend_embed(
		ctx,
		clean_exams,
		title = f"EXÁMENES mes {month_n}",
		colour = discord.Colour.red()
	)
	await trysend_embed(
		ctx,
		clean_others,
		title = f"Otras cosas en mes {month_n}",
		colour = discord.Colour.green()
	)