#Imports
import os
import discord
import requests
from discord.ext import tasks
import datetime
from datetime import timedelta
from discord.utils import get
import random
from dotenv import load_dotenv
import asyncio


load_dotenv()

#CWD
dir_path = os.path.dirname(os.path.realpath(__file__))




#Dictionaries
MovieCandidates = {}
MovieOfTheWeek = {}
numbers = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']

#Setting Class to bot
bot = discord.Bot()




#Enviornment info
#command channel
vChannel = int(os.getenv('VOTE_CHANNEL_ID'))
vChannel_Name = os.getenv('VOTE_CHANNEL_NAME')
dChannel = int(os.getenv('DISCUSSION_CHANNEL_ID'))
dChannel_Name = os.getenv('DISCUSSION_CHANNEL_NAME')
MovieRole = int(os.getenv('MOVIE_ROLE'))
admin_id = int(os.getenv('ADMIN_ID'))
guild_id = int(os.getenv('GUILD_ID'))
tmdb_api = os.getenv('TMDB_API')
versionnum = '1.1.3'
changes = 'Added banlist \n Added auto discuss of /force creeate'

#Getting Reaction Ban list
banlist = []
banfile = open(os.path.join(dir_path, 'banlist.txt'))
for x in banfile:
    x = x.rstrip('\n')
    x = int(x)
    banlist.append(x)

#Creating Movie Class
class Movie:
    def __init__(self, tmdbid, title, release_date, rating, overview, poster, runtime):
        self.tmdbid = tmdbid
        self.title = title
        self.release_date = release_date
        self.rating = rating
        self.overview = overview
        self.poster = poster
        self.runtime = runtime
        self.msg = 0
        self.votes = 0
        self.msgid = 0

    def __str__(self):
        return f"{self.title} ({self.release_date[0:4]})"    

    def test(self):
        print(self.title)

    def createembed(self):
        #create a discord embed
        embed = discord.Embed(title=self.title + ' (' + self.release_date[0:4] + ')', description=self.overview, color=discord.Color.random())
        #Add the movie ID to the field
        embed.add_field(name='Movie ID', value = self.tmdbid)
        #Get Runtime in xh ym format
        runtime = self.runtime
        h = runtime//60
        m = runtime%60
        #Add runtime to embed
        embed.add_field(name='Runtime', value = str(h) + 'h ' + str(m) + 'm')
        #Add rating to embed
        embed.add_field(name='Rating', value = self.rating)
        #Set image of embed to poster
        embed.set_image(url=self.poster)
        #Set Title to option number
        embed.set_author(name='Movie Club')
        self.msg = embed


#Movie Command group
movies = bot.create_group("newvie", "Commands for Newvie")

#@movies.command(name='create', description='Used to view the create movie candidates.')
#async def create(ctx):
async def create():
    #find_movies()
    r = requests.get('https://api.themoviedb.org/3/discover/movie?api_key=' + tmdb_api + '&include_adult=false&vote_count.gte=100&vote_average.gte=7.0&without_genres=35%2C99%2C10751%2C10402%2C10749%2C10770').json()
    total_pages = r['total_pages']
    useable_pages = total_pages - 1
    for x in range(10):
        #generate random page number
        pagenum = random.randint(1,useable_pages)
        #generate random result number
        resultnum = random.randint(0,19)
        #get results using randum page number
        rl = requests.get('https://api.themoviedb.org/3/discover/movie?api_key=' + tmdb_api + '&include_adult=false&vote_count.gte=100&vote_average.gte=7.0&without_genres=35%2C99%2C10751%2C10402%2C10749%2C10770&page='+ str(pagenum)).json()
        #Use tmdbid to get movie run time
        rmi = requests.get('https://api.themoviedb.org/3/movie/' + str(rl['results'][resultnum]['id']) + '?api_key='+ tmdb_api ).json()
        #Add result into Variables
        rtmdbid = rl['results'][resultnum]['id']
        rtitle = rl['results'][resultnum]['title']
        rrelease_date = rl['results'][resultnum]['release_date']
        rrating = rl['results'][resultnum]['vote_average']
        roverview = rl['results'][resultnum]['overview']
        rposter =  'https://image.tmdb.org/t/p/original/' + rl['results'][resultnum]['poster_path']
        rruntime = rmi['runtime']
        #Create Class from Variables
        movie = Movie(rtmdbid,rtitle,rrelease_date,rrating,roverview,rposter,rruntime)
        #Create embed message
        movie.createembed()
        #Save Movie to dictionary and Nested dictionary
        dict = {'tmdbid': movie.tmdbid,'title': movie.title, 'release_date': movie.release_date, 'rating': movie.rating, 'overview': movie.overview, 'poster': movie.poster, 'msg': movie.msg}
        MovieCandidates[x] = dict
    print('Movies Created')
    #set channel
    channel = bot.get_channel(vChannel)
    guild = bot.get_guild(guild_id)
    global notification
    role = discord.utils.get(guild.roles, id=MovieRole)
    notification = await channel.send(f'{role.mention} New movies for the week:')
    current_day = datetime.date.today() - timedelta(days=1)
    formatted_date = datetime.date.strftime(current_day, "%m/%d/%Y")
    poll = discord.Embed(title='Poll for week of ' + formatted_date,
                        description='Vote for a movie in the thread below.', 
                        color=discord.Color.gold())
    poll.add_field(name='Options', value = numbers[0] + '  ' + MovieCandidates[0]['title'] + ' (' + MovieCandidates[0]['release_date'][0:4] + ')' + '\n\n' 
                                        + numbers[1] + '  ' + MovieCandidates[1]['title'] + ' (' + MovieCandidates[1]['release_date'][0:4] + ')' + '\n\n'
                                        + numbers[2] + '  ' + MovieCandidates[2]['title'] + ' (' + MovieCandidates[2]['release_date'][0:4] + ')' + '\n\n' 
                                        + numbers[3] + '  ' + MovieCandidates[3]['title'] + ' (' + MovieCandidates[3]['release_date'][0:4] + ')' + '\n\n'
                                        + numbers[4] + '  ' + MovieCandidates[4]['title'] + ' (' + MovieCandidates[4]['release_date'][0:4] + ')' + '\n\n'
                                        + numbers[5] + '  ' + MovieCandidates[5]['title'] + ' (' + MovieCandidates[5]['release_date'][0:4] + ')' + '\n\n'
                                        + numbers[6] + '  ' + MovieCandidates[6]['title'] + ' (' + MovieCandidates[6]['release_date'][0:4] + ')' + '\n\n'
                                        + numbers[7] + '  ' + MovieCandidates[7]['title'] + ' (' + MovieCandidates[7]['release_date'][0:4] + ')' + '\n\n'
                                        + numbers[8] + '  ' + MovieCandidates[8]['title'] + ' (' + MovieCandidates[8]['release_date'][0:4] + ')' + '\n\n'
                                        + numbers[9] + '  ' + MovieCandidates[9]['title'] + ' (' + MovieCandidates[9]['release_date'][0:4] + ')' + '\n\n')
    pollpost = await channel.send(embed=poll)
    pollthread = await pollpost.create_thread(name='Poll of the week', auto_archive_duration=1440)
    global pollid
    pollid = pollpost.id
    for x in numbers:
        await pollpost.add_reaction(x)
    i = 1
    for x in MovieCandidates:
        embed = MovieCandidates[x]['msg']
        embed.remove_author()
        embed.set_author(name = 'Option ' + str(i))
        movieinfo = await pollthread.send(embed=embed)
        #Add msgid to the dict
        c_channel = bot.get_channel(vChannel)
        prevmessages = await c_channel.history(limit=1).flatten()
        msgid = prevmessages[0].id
        MovieCandidates[x]['msgid'] = msgid
        i = i + 1
    print('Movies Displayed')

#function to close poll and create discussion thread
async def discuss():
    #set voice and discussion channel
    vchannel = bot.get_channel(vChannel)
    dchannel = bot.get_channel(dChannel)
    #create empty list for winners
    winners = []
    #write movie candidates to file
    mcfile = open(os.path.join(dir_path, 'mc.txt'),'a')
    mcfile.write(str(datetime.datetime.today()) + '\n')
    mcfile.close
    #Count Vote
    pollmessage = await vchannel.fetch_message(pollid)
    i = 0
    for r in pollmessage.reactions:
        rcount  = r.count
        winners.append(rcount)
        MovieCandidates[i]['votes'] = rcount
        mcfile.write('  ' + MovieCandidates[i]['title'] + ' ')
        mcfile.write(str(rcount) + '\n')
        mcfile.close
        i = i+1
    #Find Max, and randomize if tie
    max_ = max(winners)
    index = random.choice([i for i in range(len(winners)) if winners[i] == max_])
    #Set winning candidate to the movie of the week
    global MovieOfTheWeek
    MovieOfTheWeek = MovieCandidates[index]
    #write winning movie to file
    motwfile = open(os.path.join(dir_path, 'motw.txt'),'a')
    motwfile.write(str(datetime.datetime.today()) + ' ' + MovieOfTheWeek['title'] + '\n')
    motwfile.close
    #Post winner to console
    print('And the winner is: ' + MovieOfTheWeek['title'] + ' (' + str(MovieOfTheWeek['release_date'][0:4]) + ')')
    #send notification to discussion channel
    guild = bot.get_guild(guild_id)
    role = discord.utils.get(guild.roles, id=MovieRole)
    await dchannel.send(f'{role.mention} New discussion thread for ' + MovieOfTheWeek['title'] + ' (' + str(MovieOfTheWeek['release_date'][0:4]) + '):')
    discussionpost = await dchannel.send(embed=MovieOfTheWeek['msg'])
    #Create a discussion thread of the winner
    await discussionpost.create_thread(name=MovieOfTheWeek['title'] + ' Discussion', auto_archive_duration=10080)
    print('Discussion post created')

#Remove reactions
@tasks.loop(minutes=1)
async def remove_reacts():
    print(str(datetime.datetime.now()) + ': Checking for banned users reacting.')
    if len(MovieCandidates) > 0:
        channel = bot.get_channel(vChannel)
        message = await channel.fetch_message(pollid)
        for reaction in message.reactions:
            async for user in reaction.users():
                if user.id in banlist:
                    await message.remove_reaction(reaction.emoji,user)
                    print('Removed '+ reaction.emoji + '  from ' + str(user))
    else:
        print('List is not created yet')

@bot.event
async def on_raw_reaction_add(payload):
    user = await bot.fetch_user(payload.user_id)
    channel = await bot.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
     #checks the reactant isn't a bot and the emoji isn't the one they just reacted with
    if (user != bot.user and payload.channel_id == vChannel):        
        for r in message.reactions:
            if (payload.member in await r.users().flatten() and not payload.member.bot): 
                if (str(r) != str(payload.emoji)):
                    print('Removing the reaction' + r.emoji)
                    await message.remove_reaction(r.emoji, payload.member)
                else:
                    print('This is the emoji the user just added')
            else:
                print(str(datetime.datetime.now()) + r.emoji + ': not removing')

#Tasks that start on script start, and check every so often
#Task to create movie candidates and vote messages on Sunday, 10AM EST
@tasks.loop(minutes=60)
async def schedulecreate():
    current_time = datetime.datetime.now()
    if(datetime.datetime.today().weekday() == 6 and current_time.hour == 15):
        print('Create starting at: ' + str(datetime.datetime.now()))
        await create()

#Task to close poll and create discussion thread on Sunday, 10PM EST.
@tasks.loop(minutes=60)
async def schedulediscuss():
    current_time = datetime.datetime.now()
    if(datetime.datetime.today().weekday() == 0 and current_time.hour == 3):
        print('Discuss starting at: ' + str(datetime.datetime.now()))
        await discuss()


#admin commands to manually call stuff in case scheduling fails
@movies.command(name='ping',description='Admin only. Used as a health check to see if the bot is online and responding to commands.')
async def ping(ctx):
    if ctx.author.id == admin_id:
        await ctx.channel.send('Newive Version: ' + str(versionnum) + '\n' + changes)
    else:
        print ('You can\'t do that')


#admin commands to manually call stuff in case scheduling fails
"""
@movies.command(name='test',description='Admin only. Used to quickly test functionality.')
async def test(ctx):
"""


@movies.command(name='recommend',description='Send a list of 10 movies to your DMs. Uses the criteria that the main recommendation list is using')
async def recommend(ctx):
    #find_movies()
    embedrecs = []
    r = requests.get('https://api.themoviedb.org/3/discover/movie?api_key=' + tmdb_api + '&include_adult=false&vote_count.gte=100&vote_average.gte=7.0&without_genres=35%2C99%2C10751%2C10402%2C10749%2C10770').json()
    total_pages = r['total_pages']
    useable_pages = total_pages - 1
    for x in range(10):
        #generate random page number
        pagenum = random.randint(1,useable_pages)
        #generate random result number
        resultnum = random.randint(0,19)
        #get results using randum page number
        rl = requests.get('https://api.themoviedb.org/3/discover/movie?api_key=' + tmdb_api + '&include_adult=false&vote_count.gte=100&vote_average.gte=7.0&without_genres=35%2C99%2C10751%2C10402%2C10749%2C10770&page='+ str(pagenum)).json()
        #Use tmdbid to get movie run time
        rmi = requests.get('https://api.themoviedb.org/3/movie/' + str(rl['results'][resultnum]['id']) + '?api_key='+ tmdb_api ).json()
        #Add result into Variables
        rtmdbid = rl['results'][resultnum]['id']
        rtitle = rl['results'][resultnum]['title']
        rrelease_date = rl['results'][resultnum]['release_date']
        rrating = rl['results'][resultnum]['vote_average']
        roverview = rl['results'][resultnum]['overview']
        rposter =  'https://image.tmdb.org/t/p/original/' + rl['results'][resultnum]['poster_path']
        rruntime = rmi['runtime']
        #Create Class from Variables
        movie = Movie(rtmdbid,rtitle,rrelease_date,rrating,roverview,rposter,rruntime)
        #Create embed message
        movie.createembed()
        #Save Movie to dictionary and Nested dictionary
        embedrecs.append(movie.msg)
        #dict = {'tmdbid': movie.tmdbid,'title': movie.title, 'release_date': movie.release_date, 'rating': movie.rating, 'overview': movie.overview, 'poster': movie.poster, 'msg': movie.msg}
        #MovieCandidates[x] = dict
    print('Movies Created')
    channel = await ctx.author.create_dm()
    await channel.send(embeds=embedrecs)
    
@movies.command(description='Admin only. Used as a backup if server wide recommendation and poll scheduling fails.')
async def force_create(message):
    if message.author.id == admin_id:
        await create()
        await asyncio.sleep(43200)
        await discuss()
    else:
        print ('You can\'t do that')


@movies.command(description='Admin only. Used as a backup if server wide poll close and creation of discussion thread fails.')
async def force_discuss(message):
    if message.author.id == admin_id:
        await discuss()
    else:
        print ('You can\'t do that')

#Setting Discord Bot to ready
@bot.event
async def on_ready():
    #set channel
    print(f'We have logged in as {bot.user}')
    print('Newive Version: ', versionnum)
    print('Current time: ', datetime.datetime.now())
    #Schedule commands that loop
    schedulecreate.start()
    schedulediscuss.start()
    remove_reacts.start()


#Connect Bot
bot.run(os.getenv('DISCORD_TOKEN'))
