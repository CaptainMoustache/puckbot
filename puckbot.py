import discord
import json
import datetime
from datetime import timedelta
import time
import random
import statsapi
import re
import dateutil.parser
import requests
import commonfunctions

class HockeyBot(discord.Client):
	commonFunctions = commonfunctions.CommonFunctions()
		
	
	async def on_ready(self):
		print('Logged on as', self.user)
		await self.change_presence(activity=discord.Game(name='pond hockey'))
	
	async def on_message(self, message):
		# don't respond to ourselves
		if message.author == self.user:
			return
		else:
			#Split the message at whitespace
			messageArray = message.content.split()
			if len(messageArray) > 0:
				#Bot was called with enough arguments
				if ('PUCKBOT' in messageArray[0].upper() and len(messageArray) > 1) or (self.user.mention in messageArray[0].upper()):
					if 'SCHEDULE' in messageArray[1].upper():
						hockeyEmbed = discord.Embed()
						hockeyEmbed.title = 'Brrr its getting cold in here...'
						hockeyEmbed.type = 'rich'
						hockeyEmbed.color = discord.Color.dark_blue()
						hockeyEmbed.set_image(url='https://i.imgur.com/yn7efui.png')
						
						#Get the NHL schedule
						scheduleResponse = await self.commonFunctions.sendGetRequest('https://statsapi.web.nhl.com/api/v1/schedule')
						
						#Parse the JSON
						scheduleJson = json.loads(scheduleResponse.text)			
						
						games = scheduleJson['dates'][0]['games']
						
						
						for hockeyGame in games:
							gameTimeLocal = self.commonFunctions.get_Local_Time(hockeyGame['gameDate'])
							nameString = hockeyGame['teams']['away']['team']['name'] + ' vs ' + hockeyGame['teams']['home']['team']['name']
							valueString = gameTimeLocal.strftime('%-I:%M%p') + ' EST' + ' @ ' + hockeyGame['venue']['name']
							hockeyEmbed.add_field(name=nameString, value=valueString)
						
						contentString = 'Puckbot hipchecked ' + message.author.mention + ' into the boards! Savage! \n Anyway here are the games for ' + gameTimeLocal.strftime('%m/%d/%Y')
						await message.channel.send(content=contentString, embed=hockeyEmbed)
						
					elif 'SCORES' in messageArray[1].upper():	
						#?expand=schedule.linescore
						
						
						#Get the NHL schedule with linescore
						linescoreResponse = await self.commonFunctions.sendGetRequest('https://statsapi.web.nhl.com/api/v1/schedule?expand=schedule.linescore')
						
						#Parse the JSON
						linescoreJson = json.loads(linescoreResponse.text)
						
						
						#allGames = games = linescoreJson['dates'][0]['games']
						allGames = linescoreJson['dates'][0]['games']
						
						scheduledGamesList = []
						liveGamesList = []
						finalGamesList = []
						
						
						#Loop through all games and append them the appropriate list
						for games in allGames:
							if games['status']['detailedState'] == 'Scheduled':
								scheduledGamesList.append(games)
							elif games['status']['detailedState'] == 'Live':
								liveGamesList.append(games)
							elif games['status']['detailedState'] == 'Final':
								finalGamesList.append(games)
						
						if len(scheduledGamesList) > 0:
							#Create an embed object for each scheduled game
							scheduledScoreEmbed = discord.Embed()
							scheduledScoreEmbed.title = "Scheduled Games"
							scheduledScoreEmbed.type = 'rich'
							scheduledScoreEmbed.color = discord.Color.dark_blue()
							
							for scheduledGame in scheduledGamesList:
								#Get the scheduled time
								gameTimeLocal = self.commonFunctions.get_Local_Time(scheduledGame['gameDate'])
								nameString = scheduledGame['teams']['away']['team']['name'] + ' vs ' + scheduledGame['teams']['home']['team']['name']
								gameTimeString = gameTimeLocal.strftime('%-I:%M%p') + ' EST' + ' @ ' + scheduledGame['venue']['name']
								scheduledScoreEmbed.add_field(name=nameString, value=gameTimeString)
								
							await message.channel.send(embed=scheduledScoreEmbed)	
								
						if len(liveGamesList) > 0:
							#Create an embed object for each live game
							liveScoreEmbed = discord.Embed()
							liveScoreEmbed.title = "Live Games"
							liveScoreEmbed.type = 'rich'
							liveScoreEmbed.color = discord.Color.dark_blue()
							
							for liveGame in liveGamesList:
								nameString = liveGame['teams']['away']['team']['name'] + ' vs ' + liveGame['teams']['home']['team']['name']
								#gameTimeString = gameTimeLocal.strftime('%-I:%M%p') + ' EST' + ' @ ' + games['venue']['name']
								scoreString = str(liveGame['teams']['away']['score']) + " - " + str(liveGame['teams']['home']['score'])
								finalScoreEmbed.add_field(name=nameString, value=scoreString)
							
							await message.channel.send(embed=finalScoreEmbed)
							
						if len(finalGamesList) > 0:
							#Create an embed object for each final game
							finalScoreEmbed = discord.Embed()
							finalScoreEmbed.title = "Final Games"
							finalScoreEmbed.type = 'rich'
							finalScoreEmbed.color = discord.Color.dark_blue()
							
							for finalGame in finalGamesList:
								nameString = finalGame['teams']['away']['team']['name'] + ' vs ' + finalGame['teams']['home']['team']['name']
								#gameTimeString = gameTimeLocal.strftime('%-I:%M%p') + ' EST' + ' @ ' + games['venue']['name']
								scoreString = str(finalGame['teams']['away']['score']) + " - " + str(finalGame['teams']['home']['score'])
								finalScoreEmbed.add_field(name=nameString, value=scoreString)
							
							await message.channel.send(embed=finalScoreEmbed)
						
						
						'''
						#If the game is scheduled
						if games['status']['detailedState'] == 'Scheduled':
							#scheduledScoreEmbed.add_field(name='Scheduled Game:', value=games['teams']['away']['team']['name'] + ' vs ' + games['teams']['home']['team']['name'], inline=False)
							#Get the scheduled time
							gameTimeLocal = self.commonFunctions.get_Local_Time(games['gameDate'])
							nameString = games['teams']['away']['team']['name'] + ' vs ' + games['teams']['home']['team']['name']
							gameTimeString = gameTimeLocal.strftime('%-I:%M%p') + ' EST' + ' @ ' + games['venue']['name']
							scheduledScoreEmbed.add_field(name=nameString, value=gameTimeString)
						
							await message.channel.send(embed=scheduledScoreEmbed)
						
						
						elif games['status']['detailedState'] == 'Final':
							#gameTimeLocal = self.commonFunctions.get_Local_Time(games['gameDate'])
							nameString = games['teams']['away']['team']['name'] + ' vs ' + games['teams']['home']['team']['name']
							#gameTimeString = gameTimeLocal.strftime('%-I:%M%p') + ' EST' + ' @ ' + games['venue']['name']
							scoreString = str(games['teams']['away']['score']) + " - " + str(games['teams']['home']['score'])
							finalScoreEmbed.add_field(name=nameString, value=scoreString)
							
							await message.channel.send(embed=finalScoreEmbed)
							
						elif games['status']['detailedState'] == 'Live':
							#gameTimeLocal = self.commonFunctions.get_Local_Time(games['gameDate'])
							nameString = games['teams']['away']['team']['name'] + ' vs ' + games['teams']['home']['team']['name']
							#gameTimeString = gameTimeLocal.strftime('%-I:%M%p') + ' EST' + ' @ ' + games['venue']['name']
							scoreString = str(games['teams']['away']['score']) + " - " + str(games['teams']['home']['score'])
							finalScoreEmbed.add_field(name=nameString, value=scoreString)
							
							await message.channel.send(embed=finalScoreEmbed)
							
							
							#print('DEBUG: [\'status\'][\'detailedState\'] = %s' % games['status']['detailedState'])
							print('DEBUG: Game Status = %s' % games['status'])
							
							scoreEmbed = discord.Embed()
							scoreEmbed.title = 'gamePk ' + str(games['gamePk'])
							scoreEmbed.type = 'rich'
							scoreEmbed.color = discord.Color.dark_blue()
							
							scoreEmbed.add_field(name='gameDate', value=str(games['gameDate']), inline=False)
							scoreEmbed.add_field(name='teams', value=games['teams']['away']['team']['name'] + ' vs ' + games['teams']['home']['team']['name'], inline=False)
							scoreEmbed.add_field(name='homeScore', value=str(games['teams']['home']['score']), inline=False)
							scoreEmbed.add_field(name='awayScore', value=str(games['teams']['away']['score']), inline=False)
							scoreEmbed.add_field(name='currentPeriod', value=str(games['linescore']['currentPeriod']), inline=False)
							scoreEmbed.add_field(name='homeGoals', value=str(games['linescore']['teams']['home']['goals']), inline=False)
							scoreEmbed.add_field(name='homeShotsOnGoal', value=str(games['linescore']['teams']['home']['shotsOnGoal']), inline=False)
							scoreEmbed.add_field(name='homePowerPlay', value=str(games['linescore']['teams']['home']['powerPlay']), inline=False)
							scoreEmbed.add_field(name='awayGoals', value=str(games['linescore']['teams']['away']['goals']), inline=False)
							scoreEmbed.add_field(name='awayShotsOnGoal', value=str(games['linescore']['teams']['away']['shotsOnGoal']), inline=False)
							scoreEmbed.add_field(name='awayPowerPlay', value=str(games['linescore']['teams']['away']['powerPlay']), inline=False)
							scoreEmbed.add_field(name='hasShootout', value=str(games['linescore']['hasShootout']), inline=False)
							scoreEmbed.add_field(name='inIntermission', value=str(games['linescore']['intermissionInfo']['inIntermission']), inline=False)
							
							await message.channel.send(embed=scoreEmbed)
							#if games['status']['detailedState'] == 'Scheduled':
							#	scheduledGames.append(games)
							#All states are unknown at the moment
							#else
								#print('DEBUG: [\'status\'][\'detailedState\'] = %s' % games['status']['detailedState'])
							'''
						
						
					
					#Display the help message
					elif 'HELP' in messageArray[1].upper():
						
						helpEmbed = discord.Embed()
						helpEmbed.title = 'Puckbot Help'
						helpEmbed.type = 'rich'
						helpEmbed.color = discord.Color.dark_blue()
						helpEmbed.set_image(url='https://i.imgur.com/u7sswGk.jpg')
						
						await message.channel.send(embed=helpEmbed)
					else:
						await message.channel.send('Sorry I don\'t understand, try saying \'Puckbot HELP\' for a list of available commands.')	

def ReadTokenFile(filename):
	#Read the token from a file
	try:
		key_file = open(filename, "r")
		token = key_file.read()
		key_file.close()
		return token
	except:
		print("Error loading %s" % filename)
		sys.exit(1)
	else:
		print("No %s file found!" % filename)

def main():
	client = HockeyBot()
	token = ReadTokenFile('auth')
	
	client.run(token)
	
if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print('Stopping Puckbot')
		pass
