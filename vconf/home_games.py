import os
import cfbd
from virtualconf import StandingsRecord

# This code assumes you set your secrey key in the env variable CFBD_API_KEY
# example for bash shells
# export CFBD_API_KEY='my_long_secret_here'
#

configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = os.environ.get('CFBD_API_KEY')
configuration.api_key_prefix['Authorization'] = 'Bearer'

class HomeAwaySplit:
    def __init__(self, team_name):
        self.home = 0
        self.away = 0
        self.neutral = 0
        self.team_name = team_name
        
    def __str__(self):
        return self.team_name + " " + str(self.home) + ", " + str(self.away) + ", " + str(self.neutral)

def homebias_sort(splitr):
    return (splitr.home - splitr.away)

cur_year = 2021
cur_team = 'Stanford'

teams_dict = { }
api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
#all_games = api_instance.get_games(year=cur_year, team = cur_team)
all_games = api_instance.get_games(year=cur_year)

# get all the games for a year

# build a team -> games dict for all true home games

for cur_game in all_games:
    if cur_game.home_id not in teams_dict:
        home_split = HomeAwaySplit(team_name = cur_game.home_team)
        teams_dict[cur_game.home_id] = home_split
    else:
        home_split = teams_dict[cur_game.home_id]
        
    if (cur_game.neutral_site) :
        home_split.neutral += 1
    else :
        home_split.home += 1

    if cur_game.away_id not in teams_dict:
        away_split = HomeAwaySplit(team_name = cur_game.away_team)
        teams_dict[cur_game.away_id] = away_split
    else :
        away_split = teams_dict[cur_game.away_id]

    if (cur_game.neutral_site) :
        away_split.neutral += 1
    else :
        away_split.away += 1


home_ordered_games = sorted(teams_dict.values(), reverse = True, key = homebias_sort)

i = 0

for team in home_ordered_games:
    print(team)
    i += 1
    if (i > 11):
        break
