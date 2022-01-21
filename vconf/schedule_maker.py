##
# January 20, 2022
#
# Create schedules of CFB games for testing different scenarios.
#
#
import time
from datetime import date
from datetime import timedelta
import constants
import cfbd

# fake a date in the CFBD format.
# negative past means date is in the future.
#
def create_date(days_in_past):
    today = date.today()
    delta = timedelta(days=days_in_past)
    gameday = today - delta
    return gameday.strftime(constants.CFBD_DATE_FMT)

def two_team_schedule():
    games = {}
    team1 = [ 24, 'Stanford']
    team2 = [ 25, 'California' ]
    for game_id in range(1, 14):
        cur_game = cfbd.Game()
        cur_game.id = game_id
        cur_game.start_date = create_date(100 - game_id)
        cur_game.home_id = team1[0]
        cur_game.home_team = team1[1]
        cur_game.home_points = 24
        cur_game.away_id = team2[0]
        cur_game.away_team = team2[1]
        cur_game.away_points = 7
        games[game_id] = cur_game
    return games

def two_team_schedule_half_done():
    games = {}
    team1 = [ 24, 'Stanford']
    team2 = [ 25, 'California' ]
    for game_id in range(1, 15):
        cur_game = cfbd.Game()
        cur_game.id = game_id
        cur_game.home_id = team1[0]
        cur_game.home_team = team1[1]
        cur_game.away_id = team2[0]
        cur_game.away_team = team2[1]
        if (game_id < 7):
            cur_game.start_date = create_date(100 - game_id)
            cur_game.home_points = 24
            cur_game.away_points = 7
        else:
            cur_game.start_date = create_date(0 - game_id)
        games[game_id] = cur_game
    return games
