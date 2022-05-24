##
# January 20, 2022
#
# Create schedules of CFB games for testing different scenarios.
#
#
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import constants
import cfbd

TEST_GAME_TIMESTAMP = 1653368232

# fake a date in the CFBD format.
# negative past means date is in the future.
#
def create_date(days_in_past):
    today = date.today()
    delta = timedelta(days=days_in_past)
    gameday = today - delta
    return gameday.strftime(constants.CFBD_DATE_FMT)

# deterministic version that creates dates based on a defined constant
# useful for deterministic testing output
#
def create_fixed_date(days_in_past):
    baseline = datetime.fromtimestamp(TEST_GAME_TIMESTAMP)
    utc_timez = timezone(timedelta(hours = 0))
    baseline.replace(tzinfo = utc_timez)
    delta = timedelta(days = days_in_past)
    gameday = baseline - delta
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

# two teams, one teams wins everything.
# team 1 should be the winner
#
def two_team_schedule():
    games = {}
    team1 = [ 24, 'Stanford']
    team2 = [ 25, 'California' ]
    for game_id in range(1, 14):
        cur_game = cfbd.Game()
        cur_game.id = game_id
        cur_game.start_date = create_fixed_date(100 - game_id)
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
# everything. no winner possible
#
def three_team_tie():
    games = {}
    team1 = [ 24, 'Stanford']
    team2 = [ 25, 'California' ]
    team3 = [ 21, 'San Diego State' ]

    # team 1 beats the other two
    games[1] = create_game(1, team1[0], team1[1], team2[0], team2[1], 30, 20, create_fixed_date(15))
    games[2] = create_game(2, team1[0], team1[1], team3[0], team3[1], 30, 20, create_fixed_date(14))

    # team 2 gets two wins
    games[3] = create_game(3, team2[0], team2[1], team1[0], team1[1], 30, 20, create_fixed_date(13))
    games[4] = create_game(4, team2[0], team2[1], team3[0], team3[1], 30, 20, create_fixed_date(12))

    # team 3 gets two wins
    games[5] = create_game(5, team3[0], team3[1], team1[0], team1[1], 30, 20, create_fixed_date(11))
    games[6] = create_game(6, team3[0], team3[1], team2[0], team2[1], 30, 20, create_fixed_date(10))

    return games

# two good teams one bad
# should result in unresolveable two team tie
#
def two_team_tie_one_doormat():
    games = {}
    team1 = [ 24, 'Stanford']
    team2 = [ 25, 'California' ]
    team3 = [ 21, 'San Diego State' ]

    # team 1 beats the other two
    games[1] = create_game(1, team1[0], team1[1], team2[0], team2[1], 30, 20, create_fixed_date(15))
    games[2] = create_game(2, team1[0], team1[1], team3[0], team3[1], 30, 20, create_fixed_date(14))

    # team 2 gets two wins
    games[3] = create_game(3, team2[0], team2[1], team1[0], team1[1], 30, 20, create_fixed_date(13))
    games[4] = create_game(4, team2[0], team2[1], team3[0], team3[1], 30, 20, create_fixed_date(12))

    # team 3 loses to everyone
    games[5] = create_game(5, team3[0], team3[1], team1[0], team1[1], 20, 30, create_fixed_date(11))
    games[6] = create_game(6, team3[0], team3[1], team2[0], team2[1], 20, 30, create_fixed_date(10))

    return games

def real_life_future_schedule():
    stanford = [ 24, 'Stanford']
    cal = [ 25, 'California' ]
    sdst = [ 21, 'San Diego State' ]
    ucla = [ 26, 'UCLA']
    usc =  [ 30, 'USC' ]
    sjst = [ 23, 'San José State']
    fresno = [ 278, 'Fresno State' ]

    games = {}
    games[1] = create_game(1, ucla[0], ucla[1], stanford[0], stanford[1], None, None, create_date(-100))
    games[2] = create_game(2, ucla[0], ucla[1], usc[0], usc[1], None, None, create_date(-101))
    games[3] = create_game(3, cal[0], cal[1], ucla[0], ucla[1], None, None, create_date(-102))
    games[4] = create_game(4, usc[0], usc[1], cal[0], cal[1], None, None, create_date(-103))
    games[5] = create_game(5, cal[0], cal[1], stanford[0], stanford[1], None, None, create_date(-105))
    games[6] = create_game(6, usc[0], usc[1], stanford[0], stanford[1], None, None, create_date(-106))
    games[7] = create_game(7, fresno[0], fresno[1], sjst[0], sjst[1], None, None, create_date(-107))
    games[8] = create_game(8, usc[0], usc[1], fresno[0], fresno[1], None, None, create_date(-108))
    games[9] = create_game(9, fresno[0], fresno[1], sdst[0], sdst[1], None, None, create_date(-109))
    games[10] = create_game(10, sdst[0], sdst[1], sjst[0], sjst[1], None, None, create_date(-110))
    
    return games

# 4 teams end up with identical record.
# should short circuit as a 4 team tie is not handled.
#
def four_team_tie():
    stanford = [ 24, 'Stanford']
    cal = [ 25, 'California' ]
    sdst = [ 21, 'San Diego State' ]
    ucla = [ 26, 'UCLA']
    usc =  [ 30, 'USC' ]
    sjst = [ 23, 'San José State']
    fresno = [ 278, 'Fresno State' ]

    games = {}
    games[1] = create_game(1, ucla[0], ucla[1], stanford[0], stanford[1], 30, 14, create_fixed_date(100))
    games[2] = create_game(2, ucla[0], ucla[1], usc[0], usc[1], 31, 28, create_fixed_date(101))
    games[3] = create_game(3, cal[0], cal[1], ucla[0], ucla[1], 24, 15, create_fixed_date(102))
    games[4] = create_game(4, usc[0], usc[1], cal[0], cal[1], 8, 33, create_fixed_date(103))
    games[5] = create_game(5, cal[0], cal[1], stanford[0], stanford[1], 12, 24, create_fixed_date(105))
    games[6] = create_game(6, usc[0], usc[1], stanford[0], stanford[1], 20, 30, create_fixed_date(106))
    games[7] = create_game(7, fresno[0], fresno[1], sjst[0], sjst[1], 40, 2, create_fixed_date(107))
    games[8] = create_game(8, usc[0], usc[1], fresno[0], fresno[1], 8, 33, create_fixed_date(108))
    games[9] = create_game(9, fresno[0], fresno[1], sdst[0], sdst[1], 18, 21, create_fixed_date(109))
    games[10] = create_game(10, sdst[0], sdst[1], sjst[0], sjst[1], 20, 34, create_fixed_date(110))
    return games

# 3 teams each lose one of the others in circular fashion
# right now this produces a winner but should it?
#
def three_team_tie_circular_losses():
    stanford = [ 24, 'Stanford']
    cal = [ 25, 'California' ]
    sdst = [ 21, 'San Diego State' ]
    ucla = [ 26, 'UCLA']
    usc =  [ 30, 'USC' ]
    sjst = [ 23, 'San José State']
    fresno = [ 278, 'Fresno State' ]

    games = {}
    games[1] = create_game(1, ucla[0], ucla[1], stanford[0], stanford[1], 30, 14, create_fixed_date(100))
    games[2] = create_game(2, ucla[0], ucla[1], usc[0], usc[1], 31, 28, create_fixed_date(101))
    games[3] = create_game(3, cal[0], cal[1], ucla[0], ucla[1], 24, 15, create_fixed_date(102))
    games[4] = create_game(4, usc[0], usc[1], cal[0], cal[1], 8, 33, create_fixed_date(103))
    games[5] = create_game(5, cal[0], cal[1], stanford[0], stanford[1], 12, 24, create_fixed_date(105))
    games[6] = create_game(6, usc[0], usc[1], stanford[0], stanford[1], 20, 30, create_fixed_date(106))
    games[7] = create_game(7, fresno[0], fresno[1], sjst[0], sjst[1], 40, 2, create_fixed_date(107))
    games[8] = create_game(8, usc[0], usc[1], fresno[0], fresno[1], 33, 23, create_fixed_date(108))
    games[9] = create_game(9, fresno[0], fresno[1], sdst[0], sdst[1], 18, 21, create_fixed_date(109))
    games[10] = create_game(10, sdst[0], sdst[1], sjst[0], sjst[1], 20, 34, create_fixed_date(110))
    return games
