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
				if 'PUCKBOT' in messageArray[0].upper() and len(messageArray) > 1:
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
