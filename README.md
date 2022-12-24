# Newvie

Newvie is a bot to help you and your friends on Discord create a movie club. Newvie creates a list of 10 movies, creates a poll that users can react to, and once the poll closes, creates a discussion thread for the winning movie.

1. Newvie will create a list of movies and post a poll to the movie voting channel. This poll will have a thread created on it with embeds for each movie.

2. Newvie will close the poll, total the reactions and create a discssion thread in the designated discussion channel. 

3. After a week of inactivity, the thread will close and the process begins again.

# Details 
* Newvie retrieves a user specificed `Number_of_Movies` in `config.ini` from TMDB with the following criteria:
  * Movie has over a 7.0 average rating.  
  * Movie has over 100 votes casted.
  * The movie is not an adult movie.
  * Movie is not a part of the following genres:
    * Comedy
    * Documentary
    * Family
    * Music
    * Romance
    * TV Movie
  * Newvie creates a poll in the designated voting channel.This poll has reactions for each movie added.
![image](https://user-images.githubusercontent.com/65965601/208975830-5fdcf637-5be7-44b6-a5a8-8c294e57aaf5.png)
  * After this poll post is created, the poll will be open for the user specificed `Vote_Time` in `config.ini` (This time is in hours).
  * Users react to which movie they would like to watch. Users are limited to 1 vote per poll, the bot removes all but their latest reaction.
* Newvie posts winning movie's embed message to the discussion channel, and creates a thread on that message.

![image](https://user-images.githubusercontent.com/65965601/208976145-76164712-e368-4b4f-af91-b385931e0742.png)
  * If there is a tie, Newvie will pick a random winner of movies with the most votes.
  * Users can type and discuss the movie in the thread.
  * List of all movie candidates and their votes are saved to `mc.txt`.
  * List of the time and winning movie is saved to `motw.txt`.


# Commands
All commands are part of the /newvie command group.

<ins>All Users</ins>

* **/newvie recommend** [number]: Send a list movies to the user's DMs. Currently uses the criteria that the main recommendation list is using.
  * number: Number of movies to recommend. Must be between 1-10.
 

<ins>Admin only</ins>
* **/newvie ping**: Bot replies with version number, changes and environment set-up.  Used as a health check to see if the bot is online and responding to commands.

* **/newvie create**: Creates the server wide movie list, creates the poll, and starts the timer for the discussion post.  Used as a backup if scheduling fails.

* **/newvie discuss**: Closes the poll and creates the discussion thread.  Used as a backup if scheduling fails.

* **/newvie set_vote_channel** [channel]: Sets the voting channel to the user specified text channel.

* **/newvie set_discussion_channel** [channel]: Sets the discussion channel to the user specified text channel.

* **/newvie set_newvie_role** [role]: Sets the role to be pinged on Newvie posts.

* **/newvie add_admin** [member]: Sets the member as a Newvie admin.

* **/newvie remove_admin** [member]: Removes the member as a Newvie admin. You cannot remove yourself via this command.

* **/newvie ban_voter** [member]: Bans the member from reacting to movie polls.

* **/newvie unban_voter** [member]: Unbans the member form reacting to movie polls.

* **/newvie set_number_of_movies** [number]: Changes the number of movies to added to the weekly poll.
  * number: Number of movies to recommend. Must be between 1-10.

* **/newvie set_poll_post_time** [day] [hour]: Sets the day and time of the weekly poll.
  * day: Day for movie to be posted. Must be 0-6 (0 = Monday, 6 = Sunday)/
  * hour: Hour for the movie to be posted. Must be 0-24.
 
 * **/newvie set_vote_timer** [hours]: Sets the number of hours the poll will be open for.
   * hours: A float. Will be converted to seconds for `asyncio.sleep`.

# Discord Setup
While it is certainly not necessary, I recommend to have 4 text channels and one role for this to work and look nice:

<ins>Role</ins>
* Movie Role
  * Role for members of your Discord that want to be a part of Movie Club.

<ins>Text Channels</ins>
* movie-club-command-spam
  * Channel for users to post commands.
* movie-club-info
  * Channel to give a summary to users of your specfic setup and timing.
* movie-voting
  * Channel for bot to post movie discussion polls and threads.
* movie-discussion
  * Channel for discussion threads to be posted.
  
  
 I recommend making these text channels private to those that have the role, so that they don't get spammed.

# Enviornment Setup
To use the bot, you will need to configure a few variables in `.env` and `config.ini`. All Discord related IDs can be retrieved by right clicking the object after enabling `Developer Mode` in Settings > Advanced.

<ins>.env</ins>
* DISCORD_TOKEN = <Your Bot's Discord Token\>
* TMDB_API = <Your TMDB API Token\>

<ins>config.ini</ins>
* Guild_ID = <id of server the bot will post in\>
* Vote_Channel_ID = <id of channel vote threads will be posted in\>
* Discussion_Channel_ID = <id of channel discussion threads will be posted in\>
* Role_ID = <id of role to be pinged on vote and discussion posts\>
* Admin_IDs = <list of ids of admins capable of using commands, comma separated, example: 118503143762128371,118503143762618331,11850314376261873\>
* Banned_Voters = <list of ids of users whose votes you want removed from the poll, comma separated, example: 118503143762128371,118503143762618331,118503143762618736\>

`sample.env` and `sample-config.ini` are provided in this repository. Take those two files and add your specific information to make the bot work properly. Rename them to `.env` and `config.ini` respectively. Values in either file do not need to be surrounded by quotes.

# Known Issues
* If a user reacts fast to a poll, it can remove all their reactions on the poll. User must wait for the bot to check for all their reactions to be checked/removed before adding an extra reacton. To be safe, users should not vote more than once a minute.
* Event scheduling is not accurate. Due to issues I had with `scheduler`, I did a workaround where the `tasks` module is running a command every hour, that command checks if the day and hour at that time is equal to when the user sets, and will run the process.
  * This creates a scenario where if the system starts/script is ran at 9:43am, `tasks` will check every hour (10:43am, 11:43am... etc). So if the creation of the poll is set to 10:00am on Sunday, it will not be created until 10:43am.
* `config.ini` has two blank lines added to it when being opened by `configparser`.


# To Do
Future changes I want to add, in no particular order.
* Add configurability to the TMDB search parameters.
  * Genres to include.
  * Genres to exclude.
  * Average Score.
  * Number of Votes.
* ~~Add flexibility on the number of movies. Currently hardcoded to be 10.~~
* Add a list of services that the movie is available on streaming/rent.
* Create new poll and discussion once certain number of users react that they have seen the movie.
* Add parameters to /recommend to help change what movie results are returned.
  * ~~Number of movies~~
  * Genres
  * Average rating
* ~~Add configuration to the scheduled time.~~
* Add support to use the users timezone.
* Clean up errors and log more.
* Clean up "Bot did not respond error" that appears in the Discord.
* Add pictures of real bot in Readme.
