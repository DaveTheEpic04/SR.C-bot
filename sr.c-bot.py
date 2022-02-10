import requests
from operator import itemgetter
from sys import argv
import sys
SRC_API = "https://www.speedrun.com/api/v1"

def conv_to_time(time):
	hours = int(time / 3600)
	time = time - hours*3600
	minutes = int(time / 60)
	time = round(time - minutes*60, 3)
	seconds = int(time)
	milliseconds = int(round((time - seconds)*1000, 0))
	if len(str(seconds)) == 1:
		seconds = "0" + str(seconds)
	if len(str(milliseconds)) == 1:
		milliseconds = "00" + str(milliseconds)
	elif len(str(milliseconds)) == 2:
		milliseconds = "0" + str(milliseconds)
	if hours == 0:
		if len(str(minutes)) == 1:
			minutes = "0" + str(minutes)
		return str(minutes) + ":" + str(seconds) + "." + str(milliseconds)
	return str(hours) + ":" + str(minutes) + ":" + str(seconds) + "." + str(milliseconds)

def spaces(list):
	len_list = []
	max_len = 0
	for i in list:
		len_list.append(len(i))
		if len(i) > max_len:
			max_len = len(i)
	for j in range(0, len(list)):
		list[j] = list[j] + " "*(max_len - len_list[j])
	return list

def get_player_name(id):
	try:
		return requests.get(f"{SRC_API}/users/{id}").json()['data']['names']['international']
	except KeyError:
		return None

def get_game_name(id):
	try:
		return requests.get(f"{SRC_API}/games/{id}").json()['data']['names']['international']
	except KeyError:
		return None

def get_level_name(id):
	try:
		return requests.get(f"{SRC_API}/levels/{id}").json()['data']['name']
	except KeyError:
		return None

def get_cat_name(id):
	try:
		return requests.get(f"{SRC_API}/categories/{id}").json()['data']['name']
	except KeyError:
		return None

def get_runs(username):
	return requests.get(f"{SRC_API}/runs?user={get_id(username)}").json()['data']

def get_run(id):
	try:
		run = requests.get(f"{SRC_API}/runs/{id}").json()['data']
	except KeyError:	
		print("\nName Error: Could not find run with code \"" + id + "\"")
		sys.exit()
	game = get_game_name(run['game'])
	player = get_player_name(run['players'][0]['id'])
	cat = get_cat_name(run['category'])
	time = conv_to_time(run['times']['primary_t'])
	if run['level'] != None:
		level = get_level_name(run['level'])
		print("\nPlayer:\t\t" + player + "\nGame:\t\t" + game + "\nLevel:\t\t" + level + "\nCategory:\t" + cat + "\nTime:\t\t" + time + "\nLink:\t\t" + run['weblink'])
	else:
		print("\nPlayer:\t\t" + player + "\nGame:\t\t" + game + "\nCategory:\t" + cat + "\nTime:\t\t" + time + "\nLink:\t\t" + run['weblink'])

def get_id(username):
	try:
		return requests.get(f"{SRC_API}/users/{username}").json()['data']['id']
	except KeyError:
		return None

def get_game_id(game):
	try:
		return requests.get(f"{SRC_API}/games/{game}").json()['data']['id']
	except KeyError:
		return None

def get_level_id(game_id, level):
	try:
		runs = requests.get(f"{SRC_API}/games/{game_id}/levels").json()['data']
	except KeyError:
		return None
	count = 0
	while True:
		try:
			if runs[count]['name'] == level or level == None:
				return runs[count]['id']
		except IndexError:
			return None
		count += 1

def get_cat_id(game_id, category):
	try:
		runs = requests.get(f"{SRC_API}/games/{game_id}/categories").json()['data']
	except KeyError:
		input_error(3)
	count = 0
	while True:
		try:
			if (runs[count]['name'] == category or category == None) and runs[count]['type'] == 'per-game':
				return runs[count]['id']
			count += 1
		except (IndexError, KeyError):
			print("\nName Error: Could not find category \"" + category + "\" in", get_game_name(game_id))
			sys.exit()

def get_il_cat_id(game_id, category):
	try:
		runs = requests.get(f"{SRC_API}/games/{game_id}/categories").json()['data']
	except KeyError:
		input_error(3)
	count = 0
	while True:
		try:
			if (runs[count]['name'] == category or category == None) and runs[count]['type'] == 'per-level':
				return runs[count]['id']
			count += 1
		except (IndexError, KeyError):
			print("\nName Error: Could not find category \"" + category + "\" in", get_game_name(game_id))
			sys.exit()

def get_var_list(game):
	try:
		vars = requests.get(f"{SRC_API}/games/{get_game_id(game)}/variables").json()['data']
	except KeyError:
		input_error(2)
	for dict in vars:
		print(f"\nVariable Name:\t{dict['name']}\nType:\t\t{dict['scope']['type']}")
		for value in dict['values']['values'].values():
			print(f"\tVariable:\t{value['label']}")

def get_discord(game):
	if game == "speedrun.com":
		print("\nspeedrun.com:\thttps://discord.gg/0h6sul1ZwHVpXJmK")
		return
	game_id = get_game_id(game)
	if game_id == None:
		input_error(2)
	game = requests.get(f"{SRC_API}/games/{game_id}").json()['data']
	if game['discord'] != "":
		print("\n" + get_game_name(game_id) + ":\t", game['discord'])
	else:
		print("\n" + get_game_name(game_id), "does not have a discord server linked")

def get_following(user):
	user_id = get_id(user)
	if user_id == None:
		input_error(2)
	following = requests.get(f"https://www.speedrun.com/_fedata/user/stats?userId={user_id}").json()['followStats']
	print("")
	for game in following:
		print(game['game']['name'])
	return

def get_run_count(username, game_id):
	offset = 0
	count = 0
	user_id = get_id(username)
	if user_id == None:
		input_error(2)
	while True:
		if game_id != None:
			runs = requests.get(f"{SRC_API}/runs?user={user_id}&max=200&offset={offset}&game={game_id}").json()
			if runs['data'] == [] and offset == 0:
				return 0
			else:
				count += len(runs['data'])
		else:
			runs = requests.get(f"{SRC_API}/runs?user={user_id}&max=200&offset={offset}").json()
			if runs['data'] == [] and offset == 0:
				return 0
			else:
				count += len(runs['data'])
		if count % 200 == 0:
			offset += 200
			if offset == 10000:
				return 10000
			elif runs['data'] == []:
				return count
		else:
			return count

def get_wr_count(username):
	offset = 0
	count = 0
	user_id = get_id(username)
	if user_id == None:
		input_error(2)
	while True:
		runs = requests.get(f"{SRC_API}/users/{user_id}/personal-bests?top=1&max=200&offset={offset}").json()['data']
		count += len(runs)
		if count % 200 == 0:
			offset += 200
			if offset == 10000:
				print("\nPlayer:\t\t", username, "\nWorld Records:\t10000")
			elif runs['data'] == []:
				print("\nPlayer:\t\t", username, "\nWorld Records:\t", count)
		else:
			username = get_player_name(user_id)
			print("\nPlayer:\t\t", username, "\nWorld Records:\t", count)
			return

def get_podium_count(username):
	offset = 0
	count = 0
	user_id = get_id(username)
	if user_id == None:
		input_error(2)
	while True:
		runs = requests.get(f"{SRC_API}/users/{user_id}/personal-bests?top=3&max=200&offset={offset}").json()['data']
		count += len(runs)
		if count % 200 == 0:
			offset += 200
			if offset == 10000:
				print("\nPlayer:\t\t", username, "\nPodiums:\t10000")
			elif runs['data'] == []:
				print("\nPlayer:\t\t", username, "\nPodiums:\t", count)
		else:
			username = get_player_name(user_id)
			print("\nPlayer:\t\t", username, "\nPodiums:\t", count)
			return

def get_num_runs(game_id, cat_id):
	offset = 0
	count = 0
	while True:
		try:
			count += len(requests.get(f"{SRC_API}/leaderboards/{game_id}/category/{cat_id}?max=200&offset={offset}").json()['data']['runs'])
		except KeyError:
			continue
		if count % 200 == 0:
			offset += 200
		else:
			return count

def get_il_num_runs(game_id, level_id, cat_id):
	offset = 0
	count = 0
	if level_id == None and level != None:
		input_error(4)
	if cat_id == None and category != None:
		input_error(5)
	while True:
		try:
			count += len(requests.get(f"{SRC_API}/leaderboards/{game_id}/level/{level_id}/{cat_id}?max=200&offset={offset}").json()['data']['runs'])
		except KeyError:
			continue
		if count % 200 == 0:
			offset += 200
		else:
			return count

def get_wr(game, category):
	game_id = get_game_id(game)
	if game_id == None:
		input_error(3)
	cat_id = get_il_cat_id(game, category)
	try:
		run = requests.get(f"{SRC_API}/leaderboards/{game_id}/category/{cat_id}?top=1").json()['data']['runs'][0]['run']
	except KeyError:
		input_error(4)
	player = get_player_name(run['players'][0]['id'])
	time = run['times']['primary_t']
	time = conv_to_time(time)
	link = run['weblink']
	if cat_id == None or category == None:
		category = requests.get(f"{SRC_API}/games/{game_id}/categories").json()['data'][0]['name']
	game = get_game_name(game_id)
	print("\nGame:\t\t", game, "\nCategory:\t", category, "\nPlayer:\t\t", player, "\nTime:\t\t", time, "\nLink:\t\t", link)

def get_il_wr(game, level, category):
	game_id = get_game_id(game)
	if game_id == None:
		input_error(3)
	level_id = get_level_id(game, level)
	cat_id = get_il_cat_id(game, category)
	try:
		run = requests.get(f"{SRC_API}/leaderboards/{game_id}/level/{level_id}/{cat_id}?top=1").json()['data']['runs'][0]['run']
	except KeyError:
		print("\nIncorrect Variable: Check the level and category variable")
		sys.exit()
	player = get_player_name(run['players'][0]['id'])
	time = run['times']['primary_t']
	time = conv_to_time(time)
	link = run['weblink']
	if cat_id == None or category == None:
		category = requests.get(f"{SRC_API}/games/{game_id}/categories").json()['data'][0]['name']
	if level_id == None or level == None:
		level = requests.get(f"{SRC_API}/games/{game_id}/levels").json()['data'][0]['name']
	game = get_game_name(game_id)
	print("\nGame:\t\t", game, "\nLevel:\t\t", level, "\nCategory:\t", category, "\nPlayer:\t\t", player, "\nTime:\t\t", time, "\nLink:\t\t", link)

def get_pb(username, game, category):
	user_id = get_id(username)
	if user_id == None:
		input_error(3)
	game_id = get_game_id(game)
	if game_id == None:
		input_error(4)
	cat_id = get_cat_id(game_id, category)
	try:
		run = requests.get(f"{SRC_API}/runs?game={game_id}&category={cat_id}&user={user_id}&orderby=date").json()['data']
	except KeyError:
		input_error(4)
	player = get_player_name(user_id)
	time = conv_to_time(run[-1]['times']['primary_t'])
	link = run[-1]['weblink']
	if cat_id == None or category == None:
		category = requests.get(f"{SRC_API}/games/{game_id}/categories").json()['data'][0]['name']
	game = get_game_name(game_id)
	print("\nGame:\t\t", game, "\nCategory:\t", category, "\nPlayer:\t\t", player, "\nTime:\t\t", time, "\nLink:\t\t", link)

def get_il_pb(username, game, level, category):
	user_id = get_id(username)
	if user_id == None:
		input_error(3)
	game_id = get_game_id(game)
	if game_id == None:
		input_error(4)
	level_id = get_level_id(game_id, level)
	cat_id = get_il_cat_id(game_id, category)
	try:
		run = requests.get(f"{SRC_API}/runs?game={game_id}&category={cat_id}&user={user_id}&level={level_id}&orderby=date").json()['data']
	except KeyError:
		print("\nIncorrect Variable: Check the level and category variable")
		sys.exit()
	player = get_player_name(user_id)
	time = conv_to_time(run[-1]['times']['primary_t'])
	link = run[-1]['weblink']
	if cat_id == None or category == None:
		category = requests.get(f"{SRC_API}/games/{game_id}/categories").json()['data'][0]['name']
	if level_id == None or level == None:
		level = requests.get(f"{SRC_API}/games/{game_id}/levels").json()['data'][0]['name']
	game = get_game_name(game_id)
	print("\nGame:\t\t", game, "\nLevel:\t\t", level, "\nCategory:\t", category, "\nPlayer:\t\t", player, "\nTime:\t\t", time, "\nLink:\t\t", link)

def get_verified(username, game):
	offset = 0
	count = 0
	user_id = get_id(username)
	if user_id == None:
		input_error(2)
	game_id = get_game_id(game)
	if game != None and game_id == None:
		input_error(3)
	while True:
		if game != None:
			runs = requests.get(f"{SRC_API}/runs?examiner={user_id}&max=200&offset={offset}&game={game_id}").json()
			try:
				if runs['data'] == [] and offset == 0:
					return 0
				else:
					count += len(runs['data'])
			except KeyError:
				continue
		else:
			runs = requests.get(f"{SRC_API}/runs?examiner={user_id}&max=200&offset={offset}").json()
			try:
				if runs['data'] == [] and offset == 0:		
					return 0
				else:
					count += len(runs['data'])
			except KeyError:
				continue
		if count % 200 == 0:
			offset += 200
			if offset == 10000:
				return 10000
			elif runs['data'] == []:
				return count
		else:
			return count

def get_vlb(game):
	game_id = get_game_id(game)
	if game_id == None:
		input_error(2)
	mod_list = requests.get(f"{SRC_API}/games/{game_id}?embed=moderators").json()['data']['moderators']['data']
	vlb_list = []
	for i in range(0, len(mod_list)):
		user = mod_list[i]['names']['international']
		vlb_list.append({'name':user, 'verified':get_verified(user, game)})
		vlb_list = sorted(vlb_list, key=itemgetter('verified'), reverse=True)
	print("")
	vlb_name = []
	for name in vlb_list:
		vlb_name.append(name['name'])
	vlb_name = spaces(vlb_name)
	for j in range(0, len(vlb_list)):
		print("Moderator:", vlb_name[j], "\tVerified:", vlb_list[j]['verified'])

def get_vpg(user):
	user_id = get_id(user)
	if user_id == None:
		input_error(2)
	mod_games = requests.get(f"{SRC_API}/games?moderator={user_id}&max=200").json()['data']
	vpg_list = []
	for games in mod_games:
		game = games['abbreviation']
		vpg_list.append({'game':game, 'verified':get_verified(user, game)})
		vpg_list = sorted(vpg_list, key=itemgetter('verified'), reverse=True)
	print("")
	vpg_game = []
	for game in vpg_list:
		vpg_game.append(game['game'])
	vpg_game = spaces(vpg_game)
	for j in range(0, len(vpg_list)):
		print("Game:", vpg_game[j], "\tVerified:", vpg_list[j]['verified'])

def get_rpg(username):
	user_id = get_id(username)
	if user_id == None:
		input_error(2)
	games = []
	pbs = requests.get(f"{SRC_API}/users/{user_id}/personal-bests?max=200").json()['data']
	for h in range(0, len(pbs)):
		try:
			games.index(pbs[h]['run']['game'])
		except ValueError:
			games.append(pbs[h]['run']['game'])
	rpg_list = []
	for game_id in games:
		game = get_game_name(game_id)
		rpg_list.append({'game':game, 'runs':get_run_count(username, game_id)})
		rpg_list = sorted(rpg_list, key=itemgetter('runs'), reverse=True)
	print("")
	rpg_game = []
	for game in rpg_list:
		rpg_game.append(game['game'])
	rpg_game = spaces(rpg_game)
	for j in range(0, len(rpg_list)):
		print("Game:", rpg_game[j], "\tRuns:", rpg_list[j]['runs'])

def get_rpc(game):
	game_id = get_game_id(game)
	if game_id == None:
		input_error(2)
	num_runs = []
	cats = requests.get(f"{SRC_API}/games/{game_id}/categories?max=200").json()['data']
	for cat in cats:
		if cat['type'] == 'per-game':
			num_runs.append({'category':cat['name'], 'runs':get_num_runs(game_id, cat['id'])})
	print("\nGame:\t", get_game_name(game_id), "\n")
	rpc_cat = []
	for cat in num_runs:
		rpc_cat.append(cat['category'])
	rpc_cat = spaces(rpc_cat)
	for i in range(0, len(num_runs)):
		print("Category:\t", rpc_cat[i], "\tRuns:\t", num_runs[i]['runs'])

def get_rplc(game, level):
	game_id = get_game_id(game)
	if game_id == None:
		input_error(2)
	level_id = get_level_id(game_id, level)
	if level_id == None and level != None:
		input_error(3)
	num_runs = []
	cats = requests.get(f"{SRC_API}/games/{game_id}/categories?max=200").json()['data']
	for cat in cats:
		if cat['type'] == 'per-level':
			num_runs.append({'category':cat['name'], 'runs':get_il_num_runs(game_id, level_id, cat['id'])})
	print("\nGame:\t", get_game_name(game_id), "\nLevel:\t", get_level_name(level_id), "\n")
	rplc_cat = []
	for cat in num_runs:
		rplc_cat.append(cat['category'])
	rplc_cat = spaces(rplc_cat)
	for i in range(0, len(num_runs)):
		print("Category:\t", rplc_cat[i], "\tRuns:\t", num_runs[i]['runs'])

def input_error(missing):
	if missing == None:
		print("\nIncorrect Variable: Check your variables")
	elif a[missing] == None:
		print("\nMissing Variable: Type help {command} to see the required variables")
		sys.exit()
	elif a[missing] != None:
		print("\nIncorrect Variable: Check", a[missing])
		sys.exit()

a = [None, None, None, None, None, None, None]
for i in range(0, len(argv)):
	a[i] = argv[i]

commands = ['help', 'run', 'user_id', 'game_id', 'level_id', 'runs', 'variables', 'discord', 'following', 'wrs', 'podiums', 'verified', 'vlb', 'vpg', 'rpg', 'rpc', 'rplc', 'category_id', 'wr', 'pb', 'lb_runs']
try:
	commands.index(a[1])
except ValueError:
	print("\nNo Command Found: Type help to see a list of commands")
	sys.exit()

if a[1] == "help":
	commands.remove('help')
	if a[2] == None:
		print("\nType help {command} to find out more about the command\n")
		for command in commands:
			print(command)
		print("\nDue to pagination limitations, all counting commands are capped at 10000")
	elif a[2] == 'run':
		print("\nrun {id}\n\nDisplays info about a run from the id")
	elif a[2] == 'user_id':
		print("\nuser_id {username}\n\nDisplays the id given to a player")
	elif a[2] == 'game_id':
		print("\ngame_id {game}\n\nDisplays the id given to a game")
	elif a[2] == 'level_id':
		print("\nlevel_id {game} {level}\n\nDisplays the id given to a level of a game")
	elif a[2] == 'runs':
		print("\nruns {username} [game]\n\nDisplays the total number of runs done by a player")
	elif a[2] == 'variables':
		print("\nvariables {game}\n\nDisplays the variables of a game and all possible values of that variable")
	elif a[2] == 'discord':
		print("\ndiscord {game}\n\nGives the discord link for a given game")
	elif a[2] == 'following':
		print("\nfollowing {user}\n\nGives a list of games a user is following")
	elif a[2] == 'wrs':
		print("\nwrs {username}\n\nDisplays the total number of world record runs done by a player")
	elif a[2] == 'podiums':
		print("\npodiums {username}\n\nDisplays the total number of top 3 runs done by a player")
	elif a[2] == 'verified':
		print("\nverified {username} [game]\n\nDisplays the number of runs examined by a moderator")
	elif a[2] == 'vlb':
		print("\nvlb {game}\n\nDisplays a leaderboard of the moderators and how many runs each has examined for a game")
	elif a[2] == 'vpg':
		print("\nvpg {username}\n\nDisplays a list of games a user is a moderator for and how many runs they have verified for each")
	elif a[2] == 'rpg':
		print("\nrpg {username}\n\nDisplays the number of runs a player has submitted per game")
	elif a[2] == 'rpc':
		print("\nrpc {game}\n\nDisplays the number of runs in each full game category of a game")
	elif a[2] == 'rplc':
		print("\nrplc {game} {level}\n\nDisplays the number of runs in each category of a level")
	elif a[2] == 'category_id':
		print("\ncategory_id {game/level} {game_id} {category}\n\nDisplays the id given to a category of a game")
	elif a[2] == 'wr':
		print("\nwr {game/level} {game} [level] [category]\n\nDisplays the world record on a given board\n[level] is unused if game is selected")
	elif a[2] == 'pb':
		print("\npb {game/level} {username} {game} [level] [category]\n\nDisplays a players personal best on a given board\n[level] is unused if game is selected")
	elif a[2] == 'lb_runs':
		print("\nlb_runs {game/level} {game} [level] [category]\n\nDisplays the total number of runs on a leaderboard (Does not include obsolete runs)\n[level] is unused if game is selected")
elif a[2] == None:
	print("\nMissing Variable: Type help {command} to see the required variables")
elif a[1] == 'run':
	get_run(a[2])
elif a[1] == 'user_id':
	id = get_id(a[2])
	if id != None:
		print("\n" + get_player_name(id) + ":\t" + id)
	else:
		input_error(2)
elif a[1] == 'game_id':
	id = get_game_id(a[2])
	game = get_game_name(id)
	if id != None:
		print("\n" + game + ":", id)
	else:
		input_error(2)
elif a[1] == 'level_id':
	game_id = get_game_id(a[2])
	id = get_level_id(game_id, a[3])
	game = get_game_name(game_id)
	level = get_level_name(id)
	if id != None:
		print("\n" + game + "\n" + level + ":", id)
	elif game_id == None:
		input_error(2)
	else:
		input_error(3)
elif a[1] == 'runs':
	count = str(get_run_count(a[2], a[3]))
	username = get_player_name(a[2])
	if a[3] != None:
		game = get_game_name(a[3])
		print("\nPlayer:\t", username, "\nGame:\t", game, "\nRuns:\t", count)
	else:
		print("\nPlayer:\t", username, "\nRuns:\t", count)
elif a[1] == 'variables':
	get_var_list(a[2])
elif a[1] == 'discord':
	get_discord(a[2])
elif a[1] == 'following':
	get_following(a[2])
elif a[1] == 'wrs':
	get_wr_count(a[2])
elif a[1] == 'podiums':
	get_podium_count(a[2])
elif a[1] == 'verified':
	count = str(get_verified(a[2], a[3]))
	username = get_player_name(a[2])
	if a[3] != None:
		game = get_game_name(a[3])
		print("\nModerator:\t", username, "\nGame:\t\t", game, "\nVerified:\t", count)
	else:
		print("\nModerator:\t", username, "\nVerified:\t", count)
elif a[1] == 'vlb':
	get_vlb(a[2])
elif a[1] == 'vpg':
	get_vpg(a[2])
elif a[1] == 'rpg':
	get_rpg(a[2])
elif a[1] == 'rpc':
	get_rpc(a[2])
elif a[1] == 'rplc':
	get_rplc(a[2], a[3])
elif a[1] == None:
	print("\nMissing Command: Type help to see a list of commands")
elif a[1] == 'category_id' and a[2] == 'game':
	game_id = get_game_id(a[3])
	id = get_cat_id(game_id, a[4])
	game = get_game_name(game_id)
	category = get_cat_name(id)
	if id != None:
		print("\n" + game + "\n" + category + ":", id)
	elif game_id == None:
		input_error(3)
	else:
		input_error(4)
elif a[1] == 'category_id' and a[2] == 'level':
	game_id = get_game_id(a[3])
	id = get_il_cat_id(game_id, a[4])
	game = get_game_name(game_id)
	category = get_cat_name(id)
	if id != None:
		print("\n" + game + "\n" + category + ":", id)
	elif game_id == None:
		input_error(3)
	else:
		input_error(4)
elif a[1] == 'wr' and a[2] == 'game':
	get_wr(a[3], a[4])
elif a[1] == 'wr' and a[2] == 'level':
	get_il_wr(a[3], a[4], a[5])
elif a[1] == 'pb' and a[2] == 'game':
	get_pb(a[3], a[4], a[5])
elif a[1] == 'pb' and a[2] == 'level':
	get_il_pb(a[3], a[4], a[5], a[6])
elif a[1] == 'lb_runs' and a[2] == 'game':
	game_id = get_game_id(a[3])
	if game_id == None:
		input_error(3)
	cat_id = get_cat_id(game_id, a[4])
	if cat_id != None or a[4] == None:
		count = get_num_runs(game_id, cat_id)
	game = get_game_name(game_id)
	category = get_cat_name(cat_id)
	print("\nGame:\t\t", game, "\nCategory:\t", category, "\nRuns:\t\t", count)
elif a[1] == 'lb_runs' and a[2] == 'level':
	game_id = get_game_id(a[3])
	if game_id == None:
		input_error(3)
	level_id = get_level_id(game_id, a[4])
	cat_id = get_il_cat_id(game_id, a[5])
	count = get_il_num_runs(game_id, level_id, cat_id)
	game = get_game_name(game_id)
	level = get_level_name(level_id)
	category = get_cat_name(cat_id)
	print("\nGame:\t\t", game, "\nLevel:\t\t", level, "\nCategory:\t", category, "\nRuns:\t\t", count)
elif a[2] != None:
	print("\nIncorrect Variable: Type help {command} to see the required variables")
