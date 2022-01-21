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

def create_game(game_id, home_id, home_team, away_id, away_team, home_points, away_points, start_date):
    game = cfbd.Game()
    game.id = game_id
    game.home_id = home_id
    game.home_team = home_team
    game.away_id = away_id
    game.away_team = away_team
    game.home_points = home_points
    game.away_points = away_points
    game.start_date = start_date
    return game

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

# torture test where three teams play each other and split
# everything
def three_team_tie():
    games = {}
    team1 = [ 24, 'Stanford']
    team2 = [ 25, 'California' ]
    team3 = [ 21, 'San Diego State' ]

    # team 1 beats the other two
    games[1] = create_game(1, team1[0], team1[1], team2[0], team2[1], 30, 20, create_date(15))
    games[2] = create_game(2, team1[0], team1[1], team3[0], team3[1], 30, 20, create_date(14))

    # team 2 gets two wins
    games[3] = create_game(3, team2[0], team2[1], team1[0], team1[1], 30, 20, create_date(13))
    games[4] = create_game(4, team2[0], team2[1], team3[0], team3[1], 30, 20, create_date(12))

    # team 3 gets two wins
    games[5] = create_game(5, team3[0], team3[1], team1[0], team1[1], 30, 20, create_date(11))
    games[6] = create_game(6, team3[0], team3[1], team2[0], team2[1], 30, 20, create_date(10))

    return games

# two good teams one bad
#
def two_team_tie_one_doormat():
    games = {}
    team1 = [ 24, 'Stanford']
    team2 = [ 25, 'California' ]
    team3 = [ 21, 'San Diego State' ]

    # team 1 beats the other two
    games[1] = create_game(1, team1[0], team1[1], team2[0], team2[1], 30, 20, create_date(15))
    games[2] = create_game(2, team1[0], team1[1], team3[0], team3[1], 30, 20, create_date(14))

    # team 2 gets two wins
    games[3] = create_game(3, team2[0], team2[1], team1[0], team1[1], 30, 20, create_date(13))
    games[4] = create_game(4, team2[0], team2[1], team3[0], team3[1], 30, 20, create_date(12))

    # team 3 loses to everyone
    games[5] = create_game(5, team3[0], team3[1], team1[0], team1[1], 20, 30, create_date(11))
    games[6] = create_game(6, team3[0], team3[1], team2[0], team2[1], 20, 30, create_date(10))

    return games
