###################
# Created by Jonatan Waern
# 7/5 2016
#
# Automated role managing bot for the Nordic Melee Netplay discord group
###################

import discord
import discord.utils as utils
from discord import Member
from credentials import token
import circuit_interactions
client = discord.Client()

#List of the proper names (case sensitive) of the roles that are managed
listofmains=["Ice Climbers","Sheik","Fox","Falco","Marth","Mario","Luigi","Yoshi","Donkey Kong","Link","Samus","Kirby","Pikachu","Jigglypuff","Captain Falcon","Ness","Peach","Bowser","Dr.Mario","Zelda","Ganondorf","Young Link","Falco","Mewtwo","Pichu","Game and Watch","Roy"]

main_requestchannel="mainrequesting"
game_requestchannel="friendlies"
watched_servers=[main_requestchannel, game_requestchannel]
requestserver="Nordic Melee Netplay"

#Here you can add common nicknames of characters and map them to their proper role names
#Note that nicknames will be converted to camelcase before handling (E.g. : "that-fucking-sword.dude fuck" -> "That-Fucking-Sword.Dude Fuck" -> "Marth")
#Note that the "Game And Watch" entry is NOT an example but rather necessary since the "Game and Watch" roles breaks the camelcase naming convention 
propernamemap={"Game And Watch" : "Game and Watch"}

#Returns exactly one role if the name specified can be translated into a proper role used on the server matching a role in the listofmains above
def obtainRoleFromName(name,isMain,server):
	#Convert the string in such a way that it keeps the same naming convention as proper roles (Camel Case)
	propername=name.title()
	#Translate through the nickname map
	if (propername in propernamemap):
		propername=propernamemap[propername]
	if (not propername in listofmains):
		return None
	toReturn=[role for role in server.roles if role.name == propername and role.hoist==isMain]
	if (len(toReturn) > 1):
		print("ERROR: The specification for the " + ("main" if isMain else "secondary") + " role " + name + " matched more than one proper role")
		print("Roles matched:")
		for role in toReturn:
			print ("  " + ("Main: " if role.hoist else "Secondary: "))
	if (len(toReturn) == 0):
		return None
	return toReturn[0]
	
#Assumes the role_name given is a canonical role name
def obtainRoleFromServer(role_name, server):
	toReturn = [role for role in server.roles if role.name == role_name]
	if (len(toReturn) != 1):
		print("ERROR: The specification for the role " + name + " matched more or less than one proper role")
		print("Roles matched:")
		for role in toReturn:
			print(role.name)
		return None
	return toReturn[0]
	
#Returns the number of mains/secondaries that a particular user has on their role list.
def countProperRoles(server,user,countOnlyMains):
	#Obtain the roles to count
	roles=[]
	for name in listofmains:
		roles.extend([role for role in server.roles if role.name == name and role.hoist == countOnlyMains])
	numroles=0
	for role in user.roles:
		if (role in roles):
			numroles+=1
	return numroles
	
#Returns the number of mains/secondaries that a particular user has on their role list with a particular name
def countSpecificRole(server,user,name):
	#Obtain the roles to count
	roles=[role for role in server.roles if role.name == name]
	numroles=0
	for role in user.roles:
		if (role in roles):
			numroles+=1
	return numroles

#Adds the "Main:" role to a user	
async def addMainRoles(server,user):
	main=[role for role in server.roles if role.name == "Main:"]
	if (len(main) != 1):
		print('ERROR: Problem with the "Main:" flairs on the server')
		return
	await client.add_roles(user,main[0])


#Adds the "Main:" and "Secondary:" roles to a user
async def addFlairRoles(server,user):
	main=[role for role in server.roles if role.name == "Main:"]
	secondary=[role for role in server.roles if role.name == "Secondary:"]
	if (len(main) != 1 or len(secondary) != 1):
		print('ERROR: Problem with the "Main:" and "Secondary:" flairs on the server')
		return
	await client.add_roles(user,main[0],secondary[0])
	
#Removes the "Main:" and "Secondary:" roles from a user	
async def removeFlairRoles(server,user):
	main=[role for role in server.roles if role.name == "Main:"]
	secondary=[role for role in server.roles if role.name == "Secondary:"]
	if (len(main) != 1 or len(secondary) != 1):
		print('ERROR: Problem with the "Main:" and "Secondary:" flairs on the server')
		return
	await client.remove_roles(user,main[0],secondary[0])

#Removes the "Secondary:" role from a user	
async def removeSecondaryRoles(server,user):
	secondary=[role for role in server.roles if role.name == "Secondary:"]
	if (len(secondary) != 1):
		print('ERROR: Problem with the "Secondary:" flair on the server')
		return
	await client.remove_roles(user,secondary[0])

#hack, store all public messages from the bot where it says someone is looing
#for games
playersearchdict = {}

@client.event
async def on_message(message):
	if  (not isinstance(message.author,Member) and not message.channel.is_private):
		print ("Detected non-private message with non-member author")

	if message.channel.is_private:
		return
	#Reply only to messages in the channel on the correct server not made by this bot
	if message.server.name != requestserver:
		return
	if not message.content.startswith('!'):
		return
	#Obtain the command as a list of strings, command[0] is the command, and the following items are the arguments
	command=message.content.partition(" ")
	command=[command[0],command[2]]

	# if message.author != client.user:
		# return
	#Don't concern ourselves with messages not starting with !
        
        if command[0] == '!score':
                if command[1] == "":
                        await client.send_message(message.channel, '{0}, the "!score" command takes exactly one argument'.format(message.author.mention))
                        return
                else:
                        matches = circuit_interactions.obtain_score(command[1])
                        if len(matches == 0):
                                await client.send_message(message.author,
                                                          "Did not find any tracked player with that name/tag")
                                return
                        else:
                                toomany_disclaimer = "{0}, ".format(message.author.mention)
                                if len(matches > 1):
                                        toomany_disclaimer += "Found several matches for that ID/TAG\n"
                                to_format = [(tag, str(rank), str(score)) for tag, rank, score in matches]
                                joined = "\n".join(["\t{0} has score {2} putting them at rank {1}".format(*tpl)
                                                    for tpl in to_format])
                                await client.send_message(message.author, toomany_disclaimer + joined)
                                return
        if command[0] == '!leaderboard':
                leaderboard_snippet = circuit_interactions.leaderboard[0:10]
                leaderboard_message = "{0}, Here's the current top 10 of the NMN tournament circuit!\n".format(message.author.mention)
                players = "\n".join(["\t{1} : {0} with {2} points".format(*tpl) for tpl in leaderboard_snippet])
                await client.send_message(message.channel, leadboard_message + players)
                return
        if not message.channel.name in watched_servers:
                if command[0] == 'help':
                        if command[1] == "":
                                await client.send_message(message.author,
                                                         "Hello! This is the Nordic Melee Netplay Bot! You have typed !help "
                                                         "in a channel that is not the 'friendlies' or 'mainrequesting' channel!\n"
                                                         "Outside of those channels, the only supported commands are: '!score' and '!leaderboard'\n"
                                                         "For information on the command in those channels, type '!help' on those channels, for help for a specific "
                                                         "command, type '!help <COMMAND'")
                                return
                        elif command[1] == "score" or command[1] == "!score" :
                                await client_send_message(message.channel,
                                                          "{0}, Usage: '!score <NAME|ID>'\n"
                                                          "Prints the score of the player with the selected tag or ID in the NMN tournament circuit".format(message.author.mention))
                                return
                        elif command[2] == "leaderboard" or command[2] == "!leaderboard":
                                await client_send_message(message.channel,
                                                          "{0}, Usage: '!leaderboard'\n"
                                                          "Sends you the list of the top ten players in the NMN tournament circuit".format(message.author.mention))
                                return
                        else:
                                await client_send_message(message.channel,
                                                          "{0}, You seem to have typed help for a command not supported in this channel. Try '!help' to see available"
                                                          "commands".format(message.author.mention))
                                return

	if message.channel.name == main_requestchannel:
		if command[0]=='!replacemain':
			#If we have the wrong number of arguments, exit
			if command[1]=="":
				await client.send_message(message.channel, '{0}, the "!replacemain" command takes exactly one argument'.format(message.author.mention))
				return
			roletoadd=obtainRoleFromName(command[1],True,message.server)
			#If we found no roles, print friendly error message
			if (roletoadd == None):
				await client.send_message(message.channel, '{0}, did not find a main with that name, try contacting an admin'.format(message.author.mention))
				return
			#If the user already has that char as a secondary, remind them of this
			if (countSpecificRole(message.server,message.author,roletoadd.name) > 0):
				await client.send_message(message.channel, '{0}, you already have that character as a main or secondary. Remove it before adding it as a main'.format(message.author.mention))
				return
			#If the user already has a main, remove it
			if (countProperRoles(message.server,message.author,True) > 0):
				for role in message.author.roles:
					if (role.name in listofmains and role.hoist == True and role in message.server.roles):
						await client.remove_roles(message.author,role)
						#hack to make role changes in-place
						message.author.roles = [oldrole for oldrole in message.author.roles if oldrole.id != role.id]
						await client.send_message(message.channel, '{0}, {1.name} is no longer your main'.format(message.author.mention,role))
			#Add the main
			await client.add_roles(message.author,roletoadd)
			#hack to make role changes in-place
			message.author.roles.append(roletoadd)
			#Since you cannot have duplicate roles, we can indiscriminately add flair roles here
			await addMainRoles(message.server,message.author)
			await client.send_message(message.channel, '{0}, added the character {1.name} as your main'.format(message.author.mention,roletoadd))
			return
		if command[0]=='!addmain':
			#If we have the wrong number of arguments, exit
			if command[1]=="":
				await client.send_message(message.channel, '{0}, the "!addmain" command takes exactly one argument'.format(message.author.mention))
				return
			roletoadd=obtainRoleFromName(command[1],True,message.server)
			#If we found no roles, print friendly error message
			if (roletoadd == None):
				await client.send_message(message.channel, '{0}, did not find a main with that name, try contacting an admin'.format(message.author.mention))
				return
			#If the user already has a main, remind them there can be only one
			if (countProperRoles(message.server,message.author,True) > 0):
				await client.send_message(message.channel, '{0}, you already have a main. Remove that main before adding a new one'.format(message.author.mention))
				return
			#If the user already has that char as a secondary, remind them of this
			if (countSpecificRole(message.server,message.author,roletoadd.name) > 0):
				await client.send_message(message.channel, '{0}, you already have that character as a secondary. Remove it before adding it as a main'.format(message.author.mention))
				return
			#Otherwise, add the main
			await client.add_roles(message.author,roletoadd)
			#hack to make role changes in-place
			message.author.roles.append(roletoadd)
			#Since you cannot have duplicate roles, we can indiscriminately add flair roles here
			await addMainRoles(message.server,message.author)
			await client.send_message(message.channel, '{0}, added the character {1.name} as your main'.format(message.author.mention,roletoadd))
			return
		if command[0]=='!removemain':
			#If we have the wrong number of arguments, exit
			if command[1]!="":
				await client.send_message(message.channel, '{0}, the "!removemain" command takes no arguments, but I will try to remove your main anyways'.format(message.author.mention))
			#If the user does not already have a main, remind them of this
			if (countProperRoles(message.server,message.author,True) == 0):
				await client.send_message(message.channel, '{0}, you do not currently have a main'.format(message.author.mention))
				return
			#Otherwise, find the main and remove it
			for role in message.author.roles:
				if (role.name in listofmains and role.hoist == True and role in message.server.roles):
					await client.remove_roles(message.author,role)
					#hack to make role changes in-place
					message.author.roles = [oldrole for oldrole in message.author.roles if oldrole.id != role.id]
					#If the user now has no mains and no secondaries, remove the flairs
					if (countProperRoles(message.server,message.author,True)+countProperRoles(message.server,message.author,False) == 0):
						await removeFlairRoles(message.server,message.author)
					await client.send_message(message.channel, '{0}, {1.name} is no longer your main'.format(message.author.mention,role))

			return
		if command[0]=='!addsecondary':
			#If we have the wrong number of arguments, exit
			if command[1]=="":
				await client.send_message(message.channel, '{0}, the "!addsecondary" command takes exactly one argument'.format(message.author.mention))
				return
			roletoadd=obtainRoleFromName(command[1],False,message.server)
			#If we found no roles, print friendly error message
			if (roletoadd == None):
				await client.send_message(message.channel, '{0}, did not find a secondary with that name, try contacting an admin'.format(message.author.mention))
				return
			#If the user already has two secondaries, remind them that three's a crows
			if (countProperRoles(message.server,message.author,False) > 1):
				await client.send_message(message.channel, '{0}, you already have two secondaries. Remove one of them before adding a new one'.format(message.author.mention))
				return
			#If the user already has that char as a main or secondary, remind them of this
			if (countSpecificRole(message.server,message.author,roletoadd.name) > 0):
				await client.send_message(message.channel, '{0}, you already have that character as a main or secondary. Remove it before adding it as a secondary'.format(message.author.mention))
				return
			#Otherwise, add the secondary
			await client.add_roles(message.author,roletoadd)
			#hack to make role changes in-place
			message.author.roles.append(roletoadd)
			#Since you cannot have duplicate roles, we can indiscriminately add flair roles here
			await addFlairRoles(message.server,message.author)
			await client.send_message(message.channel, '{0}, added the character {1.name} as one of your secondaries'.format(message.author.mention,roletoadd))
			return
		if command[0]=='!removesecondary':
			#If we have the wrong number of arguments, exit
			if command[1]=="":
				await client.send_message(message.channel, '{0}, the "!removesecondary" command takes exactly one argument'.format(message.author.mention))
				return
			roletoremove=obtainRoleFromName(command[1],False,message.server)
			#If we found no roles, print friendly error message
			if (roletoremove == None):
				await client.send_message(message.channel, '{0}, did not find a character with that name, try contacting an admin or checking your role list'.format(message.author.mention))
				return
			#If the user does not already have any secondaries, remind them of this
			if (countProperRoles(message.server,message.author,False) == 0):
				await client.send_message(message.channel, '{0}, you do not currently have any secondaries'.format(message.author.mention))
				return
			#Otherwise, remove the secondary if we have it
			if (roletoremove in message.author.roles):
				await client.remove_roles(message.author,roletoremove)
				#hack to make role changes in-place
				message.author.roles = [oldrole for oldrole in message.author.roles if oldrole.id != roletoremove.id]
				#If the user now has no mains and no secondaries, remove the flairs
				if ((countProperRoles(message.server,message.author,True)+countProperRoles(message.server,message.author,False)) == 0):
					await removeFlairRoles(message.server,message.author)
				else:
					if (countProperRoles(message.server,message.author,False) == 0):
						await removeSecondaryRoles(message.server,message.author)
				await client.send_message(message.channel, '{0}, {1.name} is no longer on of your secondaries'.format(message.author.mention,roletoremove))
			else:
				await client.send_message(message.channel, '{0}, you do not have that character as a secondary, try adding it first if you want to remove it'.format(message.author.mention))
	
			return
		if command[0]=='!help':
			if (command[1]=="roles"):
				s=", "
				await client.send_message(message.channel, 'This bot knows about the canonical role names: {0}'.format(s.join(listofmains)))
				return
			if (command[1]=="!addmain" or command[1]=="addmain"):
				await client.send_message(message.channel, 'Usage "!addmain <character>". Adds the selected character as your main. You can only have one main at a time. For a list of canonical role names type "!help roles"')
				return
			if (command[1]=="!replacemain" or command[1]=="replacemain"):
				await client.send_message(message.channel, 'Usage "!replacemain <character>". Removes your previous main and adds the selected character as your main. For a list of canonical role names type "!help roles"')
				return
			if (command[1]=="!removemain" or command[1]=="removemain"):
				await client.send_message(message.channel, 'Usage "!removemain". Removes your current main')
				return
			if (command[1]=="!addsecondary" or command[1]=="addsecondary"):
				await client.send_message(message.channel, 'Usage "!addsecondary <character>". Adds the selected character as one of your secondaries. You can have at most two secondaries at a time. For a list of canonical role names type "!help roles"')
				return
			if (command[1]=="!removesecondary" or command[1]=="removesecondary"):
				await client.send_message(message.channel, 'Usage "!removesecondary <character>". Removes the selected character from your secondaries. For a list of canonical role names type "!help roles"')
				return
                        elif command[1] == "score" or command[1] == "!score" :
                                await client_send_message(message.channel,
                                                          "{0}, Usage: '!score <NAME|ID>'\n"
                                                          "Prints the score of the player with the selected tag or ID in the NMN tournament circuit".format(message.author.mention))
                                return
                        elif command[2] == "leaderboard" or command[2] == "!leaderboard":
                                await client_send_message(message.channel,
                                                          "{0}, Usage: '!leaderboard'\n"
                                                          "Sends you the list of the top ten players in the NMN tournament circuit".format(message.author.mention))
                                return
			if (command[1]==""):
				await client.send_message(message.channel, 'This is the Nordic Melee Netplay Community role-managing bot!\nCommands are; "!addmain", "!removemain", "!addsecondary", "!removesecondary", "!replacemain" and "!help". Type "!help <command>" to see help for specific commands.\nIf the bot does not reply to a command, it probably did it anyways, check your roles to make sure')
				return
			await client.send_message(message.channel, 'Commands are; "!addmain", "!removemain", "!addsecondary", "!removesecondary", "!replacemain" and "!help". Type "!help <command>" to see help for specific commands')
			return
		await client.send_message(message.channel, 'Commands are; "!addmain", "!removemain", "!addsecondary", "!removesecondary", "!replacemain" and "!help". Type "!help <command>" to see help for specific commands')
	if message.channel.name == game_requestchannel:
		if command[0]=='!lfs':
			singles_role = obtainRoleFromServer('LF Singles',message.server)
			await client.add_roles(message.author, singles_role)
			message.author.roles.append(singles_role)
			mess = await client.send_message(message.channel, '{0} is looking for singles games! {1}'.format(message.author.name, singles_role.mention))
			if message.author in playersearchdict:
				playersearchdict[message.author].add(mess)
			else:
				playersearchdict[message.author] = set([mess])
			await client.delete_message(message)
			return
		if command[0]=='!lfd':
			doubles_role = obtainRoleFromServer('LF Doubles',message.server)
			await client.add_roles(message.author, doubles_role)
			message.author.roles.append(doubles_role)
			mess = await client.send_message(message.channel, '{0} is looking for doubles games! {1}'.format(message.author.name, doubles_role.mention))
			if message.author in playersearchdict:
				playersearchdict[message.author].add(mess)
			else:
				playersearchdict[message.author] = set([mess])
			await client.delete_message(message)
			return
		if command[0]=='!lfg':
			singles_role = obtainRoleFromServer('LF Singles',message.server)
			doubles_role = obtainRoleFromServer('LF Doubles',message.server)
			mess = await client.add_roles(message.author, singles_role, doubles_role)
			if message.author in playersearchdict:
				playersearchdict[message.author].add(mess)
			else:
				playersearchdict[message.author] = set([mess])
			message.author.roles.append(singles_role)
			message.author.roles.append(doubles_role)	
			await client.send_message(message.channel, '{0} is looking for singles and doubles games! {1} {2}'.format(message.author.name, singles_role.mention, doubles_role.mention))
			await client.delete_message(message)
			return
		if command[0]=='!stop':
			singles_role = obtainRoleFromServer('LF Singles',message.server)
			doubles_role = obtainRoleFromServer('LF Doubles',message.server)
			await client.remove_roles(message.author,singles_role,doubles_role)
			message.author.roles = [oldrole for oldrole in message.author.roles if oldrole.id != singles_role.id or oldrole.id != doubles_role.id]
			await client.send_message(message.author, '{0}, you are no longer looking for any games'.format(message.author.mention))
			if message.author in playersearchdict:
				for mess in playersearchdict[message.author]:
					await client.delete_message(mess)
				del playersearchdict[message.author]
			await client.delete_message(message)
			return
		if command[0]=='!help':
			await client.delete_message(message)
			if (command[1]==""):
				await client.send_message(message.author, 'This is the Nordic Melee Netplay Community role-managing bot!\nCommands are; "!lfs", "!lfd", "!lfg", "!stop", and "!help". Type "!help <command>" to see help for specific command')
				return
			if command[1]=='lfs':
				await client.send_message(message.authro, 'Usage "!lfs". Adds the LF Singles role to you and pings everyone with that role.')
				return
			if command[1]=='lfd':
				await client.send_message(message.author, 'Usage "!lfd". Adds the LF Doubles role to you and pings everyone with that role.')
				return
			if command[1]=='lfg':
				await client.send_message(message.author, 'Usage "!lfg". Adds both the LF Doubles and the LF Singles role to you and pings everyone with those role.')
				return	
			if command[1]=='stop':
				await client.send_message(message.author, 'Usage "!stop". Removes the LF Doubles and the LF Singles role from you, if you have either one.')
				return
                        if command[1] == "score" or command[1] == "!score" :
                                await client_send_message(message.channel,
                                                          "{0}, Usage: '!score <NAME|ID>'\n"
                                                          "Prints the score of the player with the selected tag or ID in the NMN tournament circuit".format(message.author.mention))
                                return
                        if command[2] == "leaderboard" or command[2] == "!leaderboard":
                                await client_send_message(message.channel,
                                                          "{0}, Usage: '!leaderboard'\n"
                                                          "Sends you the list of the top ten players in the NMN tournament circuit".format(message.author.mention))
                                return
			await client.send_message(message.author, 'Commands are; "!lfs", "!lfd", "!lfg", "!stop", and "!help". Type "!help <command>" to see help for specific commands')
			return
		await client.send_message(message.author, 'Commands are; "!lfs", "!lfd", "!lfg", "!stop", and "!help". Type "!help <command>" to see help for specific commands')

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

circuit_interactions.calculate_leaderboard()
client.run(token)
