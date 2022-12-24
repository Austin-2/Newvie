#Imports
import sys
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
import configparser
import calendar


load_dotenv()

#CWD
dir_path = os.path.dirname(os.path.realpath(__file__))

#Your TMDB API
tmdb_api = os.getenv('TMDB_API')

#Dictionaries/Lists
MovieCandidates = {}
MovieOfTheWeek = {}
numbers = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']

#Setting Class to bot
bot = discord.Bot()

#Set configparser to cfg
cfg = configparser.ConfigParser()

async def LoadConfig():
    #Set variables to global
    global configfile
    global vote_channel_id
    global discussion_channel_id
    global role_id
    global admin_ids
    global guild_id
    global ban_list
    global num_of_movies
    global poll_day
    global poll_hour
    global vote_time

    #Load Config file
    configfile = cfg.read((os.path.join(dir_path, 'config.ini')))

    #Channel for voting related posts to be made:
    vote_channel_id = int(cfg['DISCORD']['Vote_Channel_ID'])

    #Channel id for discussion related posts to be made:
    discussion_channel_id = int(cfg['DISCORD']['Discussion_Channel_ID'])

    #Role ID for the role you want to be tagged when posts are made.
    role_id = int(cfg['DISCORD']['Role_ID'])

    #List of users that are able to use the Admin commands
    admin_ids = cfg['DISCORD']['Admin_IDs'].split(',')
    admin_ids = [ int(x) for x in admin_ids]

    #guild this is beig ran in:
    guild_id = int(cfg['DISCORD']['Guild_ID'])

    #Banned users
    ban_list = cfg['DISCORD']['Banned_Voters'].split(',')
    ban_list = [ int(x) for x in ban_list]

    #Number of movies, must be less than 10 
    num_of_movies = int(cfg['NEWVIE']['Number_of_Movies'])
    if num_of_movies > 10:
        sys.exit('Please provide a number of movies less than 10.')
    else:
        print('Movie count less than 10')

    #Day that you would like the poll to be posted:
    poll_day = int(cfg['NEWVIE']['Poll_Day'])

    #Hour you would like the poll to be posted:
    poll_hour = int(cfg['NEWVIE']['Poll_Hour'])

    #Day that you would like the poll to be posted:
    vote_time = float(cfg['NEWVIE']['Vote_Time'])
    vote_time = vote_time*3600

#Version Number
versionnum = '2.0'

#Recent Changes
changes = 'Changed configuration to config.ini. \nAdded commands to edit config. \nChanged creation of poll to call discussion after set amount of configured time.'

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
async def create():
    #find_movies()
    r = requests.get('https://api.themoviedb.org/3/discover/movie?api_key=' + tmdb_api + '&include_adult=false&vote_count.gte=100&vote_average.gte=7.0&without_genres=35%2C99%2C10751%2C10402%2C10749%2C10770').json()
    total_pages = r['total_pages']
    useable_pages = total_pages - 1
    for x in range(num_of_movies):
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
    channel = bot.get_channel(vote_channel_id)
    guild = bot.get_guild(guild_id)
    global notification
    role = discord.utils.get(guild.roles, id=role_id)
    notification = await channel.send(f'{role.mention} New movies for the week:')
    current_day = datetime.date.today() - timedelta(days=1)
    formatted_date = datetime.date.strftime(current_day, "%m/%d/%Y")
    poll = discord.Embed(title='Poll for week of ' + formatted_date,
                        description='Vote for a movie in the thread below.', 
                        color=discord.Color.gold())
    for x in range(num_of_movies):
         poll.add_field(name='Option ' + str(x+1) + ':', value = numbers[x] + '   ' + MovieCandidates[x]['title'] + ' (' + MovieCandidates[x]['release_date'][0:4] + ')' + '\n\n\n', inline=False)
    pollpost = await channel.send(embed=poll)
    pollthread = await pollpost.create_thread(name='Poll of the week', auto_archive_duration=1440)
    global pollid
    pollid = pollpost.id
    for x in range(num_of_movies):
        await pollpost.add_reaction(numbers[x])
    i = 1
    for x in range(num_of_movies):
        embed = MovieCandidates[x]['msg']
        embed.remove_author()
        embed.set_author(name = 'Option ' + str(i))
        movieinfo = await pollthread.send(embed=embed)
        #Add msgid to the dict
        c_channel = bot.get_channel(vote_channel_id)
        prevmessages = await c_channel.history(limit=1).flatten()
        msgid = prevmessages[0].id
        MovieCandidates[x]['msgid'] = msgid
        i = i + 1
    print('Movies Displayed')
    print('Poll will close in ' + str(vote_time) + ' seconds')
    await asyncio.sleep(vote_time)
    await discuss()

#function to close poll and create discussion thread
async def discuss():
    #set voice and discussion channel
    vote_channel = bot.get_channel(vote_channel_id)
    discussion_channel = bot.get_channel(discussion_channel_id)
    #create empty list for winners
    winners = []
    #write movie candidates to file
    mcfile = open(os.path.join(dir_path, 'mc.txt'),'a')
    mcfile.write(str(datetime.datetime.today()) + '\n')
    mcfile.close
    #Count Vote
    pollmessage = await vote_channel.fetch_message(pollid)
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
    role = discord.utils.get(guild.roles, id=role_id)
    await discussion_channel.send(f'{role.mention} New discussion thread for ' + MovieOfTheWeek['title'] + ' (' + str(MovieOfTheWeek['release_date'][0:4]) + '):') 
    discussionpost = await discussion_channel.send(embed=MovieOfTheWeek['msg'])
    #Create a discussion thread of the winner
    await discussionpost.create_thread(name=MovieOfTheWeek['title'] +  ' (' + MovieOfTheWeek['release_date'][0:4] + ')' + ' Discussion', auto_archive_duration=10080)
    print('Discussion post created')

#Remove reactions
@tasks.loop(minutes=1)
async def remove_reacts():
    print(str(datetime.datetime.now()) + ': Checking for banned users reacting.')
    if len(MovieCandidates) > 0:
        channel = bot.get_channel(vote_channel_id)
        message = await channel.fetch_message(pollid)
        for reaction in message.reactions:
            async for user in reaction.users():
                if user.id in ban_list:
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
    if (user != bot.user and payload.channel_id == vote_channel_id):        
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
    if(datetime.datetime.today().weekday() == poll_day and current_time.hour == poll_hour):
        print('Create starting at: ' + str(datetime.datetime.now()))
        await create()

#admin commands to manually call stuff in case scheduling fails
@movies.command(name='test',description='Admin only. Used to quickly test functionality.')
async def test(ctx):
    if ctx.author.id in admin_ids:
        print('vote_channel_id: ',vote_channel_id, '\n')
        print('discussion_channel_id: ', discussion_channel_id,'\n')
        print('role id: ', role_id, '\n')
        print('admin_ids: ',admin_ids, '\n')
        print('guild_id: ',guild_id, '\n')
        print('ban_list: ',ban_list, '\n')
        print('num_of_movies: ',num_of_movies, '\n')
        print('poll_day: ',poll_day, '\n')
        print('poll_hour: ',poll_hour, '\n')
        print('vote_time: ',vote_time, '\n')
    else:
        print ('You can\'t do that')


@movies.command(name='recommend', description='Send a list of movies to your DMs. Uses the criteria that the main recommendation list is using')
async def recommend(ctx, num: int):
    if 0 < num <= 10:
        #find_movies()
        embedrecs = []
        r = requests.get('https://api.themoviedb.org/3/discover/movie?api_key=' + tmdb_api + '&include_adult=false&vote_count.gte=100&vote_average.gte=7.0&without_genres=35%2C99%2C10751%2C10402%2C10749%2C10770').json()
        total_pages = r['total_pages']
        useable_pages = total_pages - 1
        for x in range(num):
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
        await ctx.respond('Check your DMs for ' + str(num) + ' movie recommendations!')
    else:
        await ctx.respond('Please enter a number between 0 and 10.')
    
@movies.command(name='create', description='Admin only. Used as a backup if server wide recommendation and poll scheduling fails.')
async def force_create(message):
    if message.author.id in admin_ids:
        await create()
    else:
        print ('You can\'t do that')

@movies.command(name='discuss', description='Admin only. Used as a backup if server wide poll close and creation of discussion thread fails.')
async def force_discuss(message):
    if message.author.id in admin_ids:
        await discuss()
    else:
        print ('You can\'t do that')

#admin commands to manually call stuff in case scheduling fails
@movies.command(name='ping',description='Admin only. Used as a health check to see if the bot is online and responding to commands.')
async def ping(ctx):
    if ctx.author.id in admin_ids:
        await ctx.channel.send('Newive Version: ' + str(versionnum) + '\n' + changes)
    else:
        print ('You can\'t do that')


#Config Changing Settings
#Change voting channel
@movies.command(name='set_vote_channel',description='Admin only. Used to set the channel vote threads are posted to.')
async def set_vote_channel(ctx, channel: discord.TextChannel):
    if ctx.author.id in admin_ids:
        channel_id = str(channel.id)
        cfg.read((os.path.join(dir_path, 'config.ini')))
        cfg.set('DISCORD','vote_channel_id', channel_id)
        with open((os.path.join(dir_path, 'config.ini')), 'w') as cfgfile:
            cfg.write(cfgfile)
        await LoadConfig()
        await ctx.respond('Vote channel changed to ' + channel.name + '.')
    else:
        print ('You can\'t do that')

#Change discusion channel
@movies.command(name='set_discussion_channel',description='Admin only. Used to set the channel discussion threads are posted to.')
async def set_discussion_channel(ctx, channel: discord.TextChannel):
    if ctx.author.id in admin_ids:
        channel_id = str(channel.id)
        cfg.read((os.path.join(dir_path, 'config.ini')))
        cfg.set('DISCORD','discussion_channel_id', channel_id)
        with open((os.path.join(dir_path, 'config.ini')), 'w') as cfgfile:
            cfg.write(cfgfile)
        await LoadConfig()
        await ctx.respond('Vote channel changed to ' + channel.name + '.')
    else:
        print ('You can\'t do that')

#Change mentioned role
@movies.command(name='set_newvie_role',description='Admin only. Used to set the role mentioned on Newvie posts.')
async def set_newvie_role(ctx, role: discord.Role):
    if ctx.author.id in admin_ids:
        role_id = str(role.id)
        cfg.read((os.path.join(dir_path, 'config.ini')))
        cfg.set('DISCORD','role_id', role_id)
        with open((os.path.join(dir_path, 'config.ini')), 'w') as cfgfile:
            cfg.write(cfgfile)
        await LoadConfig()
        await ctx.respond('Newvie role changed to ' + role.name + '.')
    else:
        print ('You can\'t do that')

#Change number of movies
@movies.command(name='set_number_of_movies',description='Admin only. Used to set the number of movies.')
async def set_discussion_channel(ctx, number: int):
    if ctx.author.id in admin_ids:
        if (0 < number <= 10):
            num = str(number)
            cfg.read((os.path.join(dir_path, 'config.ini')))
            cfg.set('NEWVIE','number_of_movies', num)
            with open((os.path.join(dir_path, 'config.ini')), 'w') as cfgfile:
                cfg.write(cfgfile)
            await LoadConfig()
            await ctx.respond('Number of movies changed to ' + num + '.')
        else:
            await ctx.respond('Please enter a value between 0 and 10.')
    else:
        print ('You can\'t do that')

#Change poll post time
@movies.command(name='set_poll_post_time',description='Admin only. Used to set when the weekly poll is posted.')
async def set_poll_post_time(ctx, day: int, hour: int):
    if ctx.author.id in admin_ids:
        if (0 <= day <= 6):
            if (0 <= hour <= 24):
                user_day = str(day)
                user_hour = str(hour)
                cfg.read((os.path.join(dir_path, 'config.ini')))
                cfg.set('NEWVIE','poll_day', user_day)
                with open((os.path.join(dir_path, 'config.ini')), 'w') as cfgfile:
                    cfg.write(cfgfile)
                cfg.set('NEWVIE','poll_hour', user_hour)
                with open((os.path.join(dir_path, 'config.ini')), 'w') as cfgfile:
                    cfg.write(cfgfile)
                await LoadConfig()
                await ctx.respond('Poll post time changed to ' + calendar.day_name[day] + ' at ' + user_hour + ':00.')
            else:
                await ctx.respond('Please enter an hour value between 0 and 24.')
        else:
            await ctx.respond('Please enter a day value between 0 and 6.')
    else:
        print ('You can\'t do that')

#Change how long poll is open for
@movies.command(name='set_vote_timer',description='Admin only. Used to set how long a vote is open for.')
async def set_vote_timer(ctx, hours: float):
    if ctx.author.id in admin_ids:
        user_time = str(hours)
        cfg.read((os.path.join(dir_path, 'config.ini')))
        cfg.set('NEWVIE','vote_time', user_time)
        with open((os.path.join(dir_path, 'config.ini')), 'w') as cfgfile:
            cfg.write(cfgfile)
        await LoadConfig()
        await ctx.respond('Voting time changed to ' + user_time + 'hours.')
    else:
        print ('You can\'t do that')

#Add admin to the admin list
@movies.command(name='add_admin',description='Admin only. Used to add an admin to newvie')
async def add_admin(ctx, member: discord.Member):
    if ctx.author.id in admin_ids:
        cfg.read((os.path.join(dir_path, 'config.ini')))
        admin_id_list = cfg['DISCORD']['admin_ids'].split(',')
        if str(member.id) not in admin_id_list:   
            user_id = str(member.id)
            admin_id_list.append(user_id)
            admin_id_list_string = ','.join(admin_id_list)
            cfg.set('DISCORD','admin_ids', admin_id_list_string)
            with open((os.path.join(dir_path, 'config.ini')), 'w') as cfgfile:
                cfg.write(cfgfile)
            await LoadConfig()
            await ctx.respond(member.name + ' is now a Newvie admin.')
        else:
            await ctx.respond(member.name + ' is already a Newvie admin.')
    else:
        print ('You can\'t do that')

#Remove admin from the admin list
@movies.command(name='remove_admin', description='Admin only. Used to remove an admin from newvie.')
async def remove_admin(ctx, member: discord.Member):
    if ctx.author.id in admin_ids:
        cfg.read((os.path.join(dir_path, 'config.ini')))
        admin_id_list = cfg['DISCORD']['admin_ids'].split(',')
        if str(member.id) in admin_id_list:    
            user_id = str(member.id)
            admin_id_list.remove(user_id)
            admin_id_list_string = ','.join(admin_id_list)
            cfg.set('DISCORD','admin_ids', admin_id_list_string)
            with open((os.path.join(dir_path, 'config.ini')), 'w') as cfgfile:
                cfg.write(cfgfile)
            await LoadConfig()
            await ctx.respond(member.name + ' is no longer a Newvie admin.')
        else:
            await ctx.respond(member.name + ' is not a Newvie admin.')
    else:
        print ('You can\'t do that')

#Ban Voter
@movies.command(name='ban_voter',description='Admin only. Used to add a voter to the ban list.')
async def ban_voter(ctx, member: discord.Member):
    if ctx.author.id in admin_ids:
        cfg.read((os.path.join(dir_path, 'config.ini')))
        ban_list = cfg['DISCORD']['banned_voters'].split(',')
        if str(member.id) not in ban_list:
            user_id = str(member.id)
            ban_list.append(user_id)
            ban_list_string = ','.join(ban_list)
            cfg.set('DISCORD','banned_voters', ban_list_string)
            with open((os.path.join(dir_path, 'config.ini')), 'w') as cfgfile:
                cfg.write(cfgfile)
            await LoadConfig()
            await ctx.respond(member.name + ' is banned from voting on movies.')
        else:
            await ctx.respond(member.name + ' is already banned from voting on movies.')
    else:
        print ('You can\'t do that')

#Unban Voter
@movies.command(name='unban_voter', description='Admin only. Used to add a voter to the ban list.')
async def unban_voter(ctx, member: discord.Member):
    if ctx.author.id in admin_ids:
        cfg.read((os.path.join(dir_path, 'config.ini')))
        ban_list = cfg['DISCORD']['banned_voters'].split(',')
        if str(member.id) in ban_list:
            ban_list = [ str(x) for x in ban_list]
            user_id = str(member.id)
            ban_list.remove(user_id)
            ban_list_string = ','.join(ban_list)
            cfg.set('DISCORD','banned_voters', ban_list_string)
            with open((os.path.join(dir_path, 'config.ini')), 'w') as cfgfile:
                cfg.write(cfgfile)
            await LoadConfig()
            await ctx.respond(member.name + ' is unbanned from voting on movies.')
        else: await ctx.respond(member.name + ' is not banned from voting.')
    else:
        print ('You can\'t do that')

#Setting Discord Bot to ready
@bot.event
async def on_ready():
    #set channel
    print(f'We have logged in as {bot.user}')
    print('Newive Version: ', versionnum)
    print('Current time: ', datetime.datetime.now())
    await LoadConfig()
    #Schedule commands that loop
    schedulecreate.start()
    remove_reacts.start()
    


#Connect Bot
bot.run(os.getenv('DISCORD_TOKEN'))
