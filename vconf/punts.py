#
# punts.
# sadness score idea is by https://twitter.com/surrender_index?lang=en Jon Bois, etc
# implementation is tuned to the cfbd data model
#
from datetime import datetime

# using "official" formula from here:
# https://github.com/andrew-shackelford/Surrender-Index/blob/master/surrender_index_bot.py
#
def field_pos_score(yards_to_goal):
    retval = 1.0
    if (yards_to_goal >= 60) :
        pass
    else:
        # 10% compounded penalty for the yards from 60-50
        # then 20% compounded penalty therafter
        yards_in_own_territory = min(10, 60 - yards_to_goal)
        retval = 1.1 ** yards_in_own_territory
        if (yards_to_goal < 50) :
            yards_in_oppo_territory = 50 - yards_to_goal
            retval *= (1.2 ** yards_in_oppo_territory)
    return retval


def calc_yds_to_go_multiplier(dist):
    if dist >= 10:
        return 0.2
    elif dist >= 7:
        return 0.4
    elif dist >= 4:
        return 0.6
    elif dist >= 2:
        return 0.8
    else:
        return 1.
    
def sadness_score(punt):
    if (punt.yards_to_goal <= 0):
        # going to assume these are errors
        return 0
    
    if (punt.distance == 0 and punt.yards_to_goal == 35):
        return 0
    
    retval = field_pos_score(punt.yards_to_goal)

    retval *= calc_yds_to_go_multiplier(punt.distance)

    if (punt.offense_score == punt.defense_score) :
        retval *= 2.0
    elif (punt.offense_score > punt.defense_score) :
        pass
    elif (punt.defense_score - punt.offense_score > 8) :
        retval *= 3.0
    else :
        # one score diff is max pain
        retval *= 4.0

    # If team is leading or it's the first half we don't do a time adjustment
    if (punt.offense_score > punt.defense_score or punt.period < 3) :
        pass
    else :
        seconds_since_halftime = (punt.period - 3) * 60 * 15
        full_minutes = 14 - punt.clock.minutes
        seconds = 60 - punt.clock.seconds
        seconds_since_halftime += (full_minutes * 60) + seconds
        time_factor = ((seconds_since_halftime * .001) ** 3) + 1
        retval *= time_factor

    return retval


def print_punt(punt, game_dates):
    # Format the game date
    game_date = game_dates.get(punt.game_id).astimezone()  # Convert to local timezone
    pretty_date = game_date.strftime("%b %d, %Y")
    
    retval = pretty_date + " " + punt.offense + " versus " + punt.defense + " with 4th and " + str(punt.distance) + ", " + str(punt.yards_to_goal) + " yards to goal, gameclock " + str(punt.clock.minutes) + ":" + "{:0>2d}".format(punt.clock.seconds) + " in Q" + str(punt.period) + " (score " + str(punt.offense_score) + "-" + str(punt.defense_score) + ")"
    #retval = f"{pretty_date} {punt.offense} with 4th and {str(punt.distance)}, {str(punt.yards_to_goal)} yards to goal, gameclock {str(punt.clock.minutes)}:{{:0>2d}".format(punt.clock.seconds) + " in Q" + str(punt.period) + " (score " + str(punt.offense_score) + "-" + str(punt.defense_score) + ")"
    
    return retval
