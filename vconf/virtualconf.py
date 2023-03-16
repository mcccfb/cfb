##
# September 1, 2021
#
# Tools for "virtual conferences" of intramural results
#
import sys
import cfbd
import copy
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from monte_carlo import *
import constants
import testing_control

MAX_TEAM_LENGTH = 24

# knocks out the non-FBS teams for the given year from
# the byref param teams
def remove_fcs_teams(configuration, teams, cur_year):
    api_instance = cfbd.TeamsApi(cfbd.ApiClient(configuration))
    year = cur_year
    fcs_teams = []

    fbs_teams = api_instance.get_fbs_teams(year=year)
    for team_id in teams:
        found = False
        for cur_team in fbs_teams:
            if (cur_team.id == team_id) :
                found = True
                break
        if (not found) :
            fcs_teams.append(team_id)
            #print(teams[team_id] + " is an FCS team")

    for fcs_team in fcs_teams :
        del teams[fcs_team]

# teams = a dictionary of id->team_name of the teams we want in our conference
#
def find_mcc_games(api_instance, teams, cur_year) :
    if (testing_control.testing_active()):
        return testing_control.choose_test()
    else:
        return games_db_query(api_instance, teams, cur_year)

def games_db_query(api_instance, teams, cur_year):
    mcc_games = {}
    for team_id in teams :
        #print("looking for " + teams[team_id])
        all_teams_games = api_instance.get_games(year=cur_year, team = teams[team_id])
        for cur_game in all_teams_games :
            #print(cur_game)
            other_team_id = -1
            if (cur_game.away_id == team_id) :
                other_team_id = cur_game.home_id
            else :
                other_team_id = cur_game.away_id
                if other_team_id in teams :
                    other_team = teams[other_team_id]
                    #print("This was a MCC game " + teams[team_id] + " versus " + other_team)
                    mcc_games[cur_game.id] = cur_game
    return mcc_games

def timesortfunc(mcc_game) :
    return datetime.strptime(mcc_game.start_date, constants.CFBD_DATE_FMT)

class StandingsRecord:
    def __init__(self, wins, losses, team_name):
        self.wins = wins
        self.losses = losses
        self.ties = 0
        self.team_name = team_name

    def record_string(self):
        s = str(self.wins) + "-" + str(self.losses)
        if (self.ties == 0):
            return s
        else:
            return s + "-" + str(self.ties)

    def __str__(self):
        return self.team_name.ljust(MAX_TEAM_LENGTH) + self.record_string()

# returns a dictionary of team name -> StandingsRecord
#
def build_standings(mcc_games) :
    standings = {}
    for cur_mcc_game in mcc_games :
        if (cur_mcc_game.away_points is None or cur_mcc_game.home_points is None) :
            pass
            # print("This game doesn't have a score")
        elif (cur_mcc_game.away_points == cur_mcc_game.home_points) :
            if (cur_mcc_game.away_id not in standings) :
                standings[cur_mcc_game.away_id] = StandingsRecord(0, 0, cur_mcc_game.away_team)
            if (cur_mcc_game.home_id not in standings) :
                standings[cur_mcc_game.home_id] = StandingsRecord(0, 0, cur_mcc_game.home_team)
            standings[cur_mcc_game.away_id].ties += 1
            standings[cur_mcc_game.home_id].ties += 1
        elif (cur_mcc_game.away_points > cur_mcc_game.home_points) :
            if (cur_mcc_game.away_id in standings) :
                standings[cur_mcc_game.away_id].wins += 1
            else :
                standings[cur_mcc_game.away_id] = StandingsRecord(1, 0, cur_mcc_game.away_team)
            if (cur_mcc_game.home_id in standings) :
                standings[cur_mcc_game.home_id].losses += 1
            else :
                standings[cur_mcc_game.home_id] = StandingsRecord(0, 1, cur_mcc_game.home_team)
        else :
            # home team won
            if (cur_mcc_game.home_id in standings) :
                standings[cur_mcc_game.home_id].wins += 1
            else :
                standings[cur_mcc_game.home_id] = StandingsRecord(1, 0, cur_mcc_game.home_team)
            if (cur_mcc_game.away_id in standings) :
                standings[cur_mcc_game.away_id].losses += 1
            else :
                standings[cur_mcc_game.away_id] = StandingsRecord(0, 1, cur_mcc_game.away_team)
    return standings

def standings_sortfunc(sr) :
    return (((sr.wins * 1000) + (sr.ties * 500)) / (sr.losses + sr.wins + sr.ties)) - sr.losses + sr.wins

# enforce win minimum
def check_minimum_wins(ordered_standings, log_q):
    while(True) :
        if (len(ordered_standings) < 1) :
            return False
        first_place = ordered_standings[0];
        if (first_place.wins <= 1) :
            ls = "MIN: disqualifying insufficient wins (" +  str(first_place.wins) \
                + ") from "  + first_place.team_name
            log_q.append(ls)
            ordered_standings.pop(0)
        else:
            return True

# return -1 if team 1 is winner, 1 if team2, 0 if tie    
def head_to_head_winner(team1, team2, all_games):
    retval = 0
    for cur_mcc_game in all_games :
        if (cur_mcc_game.home_team == team1 and cur_mcc_game.away_team == team2) :
            if (cur_mcc_game.home_points > cur_mcc_game.away_points) :
                # team1 was the home team and home team won
                retval -= 1
            else:
                # team1 was the home team and the home team lost
                retval += 1
        elif (cur_mcc_game.away_team == team1 and cur_mcc_game.home_team == team2) :
            if (cur_mcc_game.away_points > cur_mcc_game.home_points) :
                # team1 was the away team and the away team won
                retval -= 1
            else:
                retval += 1
        else:
            # this game was not head to head
            pass
    return retval

# returns a dict of opponent->gross margin
#
def margins_by_opponent(all_games, team_id):
    oppos = {}

    for cur_mcc_game in all_games :
        if (cur_mcc_game.home_team == team_id) :
            if (cur_mcc_game.away_id not in oppos):
                oppos[cur_mcc_game.away_id] = 0
            oppos[cur_mcc_game.away_id] += (cur_mcc_game.home_points - cur_mcc_game.away_points)
        elif (cur_mcc_game.away_team == team_id) :
            if (cur_mcc_game.home_id not in oppos):
                oppos[cur_mcc_game.home_id] = 0
            oppos[cur_mcc_game.home_id] += (cur_mcc_game.away_points - cur_mcc_game.home_points)
        else:
            # team_id was not involved in this game
            pass
    return oppos

# return -1 if team 1 is winner, 1 if team2, 0 if tie
def common_opp_margin(team1, team2, all_games, log_q):
    oppos = {}
    gross_margin_team1 = 0

    t1_oppos = margins_by_opponent(all_games, team1)
    t2_oppos = margins_by_opponent(all_games, team2)

    # find intersections and total up
    for t1_op in t1_oppos:
        if (t1_op in t2_oppos):
            gross_margin_team1 += (t1_oppos[t1_op] - t2_oppos[t1_op])

    # log_q.append("gross margin for " + team1 + " vs " + team2 + " is " + str(gross_margin_team1))

    if (gross_margin_team1 < 0):
        return 1
    elif (gross_margin_team1 > 0):
        return -1
    else:
        return 0

# return -1 if team 1 is winner, 1 if team2, 0 if tie
def total_margin(team1, team2, all_games, log_q):
    team1_margin = 0
    team2_margin = 0

    log_q.append("TBRK total margin for " + team1 + " and " + team2)
    # first find all team1's margins
    for cur_mcc_game in all_games :
        if (cur_mcc_game.home_team == team1) :
            team1_margin += (cur_mcc_game.home_points - cur_mcc_game.away_points)
        elif (cur_mcc_game.away_team == team1) :
            team1_margin += (cur_mcc_game.away_points - cur_mcc_game.home_points)
        else:
            # team1 was not involved in this game
            pass

        if (cur_mcc_game.home_team == team2) :
            team2_margin += (cur_mcc_game.home_points - cur_mcc_game.away_points)
        elif (cur_mcc_game.away_team == team2) :
            team2_margin += (cur_mcc_game.away_points - cur_mcc_game.home_points)
        else:
            # team2 was not involved in this game
            pass

    if (team1_margin > team2_margin) :
        return -1
    elif (team2_margin > team1_margin) :
        return 1
    else:
        return 0

# take the old leader off and switch it with a promote_index
#
def promote_standings(ordered_standings, promote_index):
    old_leader = ordered_standings.pop(0)
    new_leader = ordered_standings.pop(promote_index - 1)    
    ordered_standings.insert(0, new_leader)
    ordered_standings.insert(promote_index, old_leader)
    
# return True if we could break the tie
#
def break_ties(ordered_standings, mcc_games, log_q):
    count_tied_teams = 1
    total_teams = len(ordered_standings)
    if (total_teams <= 1):
        return True

    for i in range(1, total_teams):
        if (standings_sortfunc(ordered_standings[0]) == standings_sortfunc(ordered_standings[i])):
            count_tied_teams += 1
        else:
            break

    if (count_tied_teams <= 1):
        return True

    if (count_tied_teams > 3):
        log_q.append("TBRK " + str(count_tied_teams) + " is too many tied teams for us.")
        return False

    if (count_tied_teams == 3):
        log_q.append("TBRK 3-team tie")
        res = break_three_team_tie(ordered_standings, mcc_games, log_q)
        if (not res):
            return False
        
    log_q.append("TBRK 2-team tie")
    return break_two_team_tie(ordered_standings, mcc_games, log_q)

# Shallow check of tiebreakers on the possible dyads within the three teams.
# Any observed tie break on any dyad is a short circuit to "success" because
# the result will still be passed through the two-team tiebreak filter.
# I.e. we don't have to worry about being unfair because we're not picking a
# winner yet, we're just weeding out one loser.
#
def break_three_team_tie(ordered_standings, mcc_games, log_q):
    dyads = [ [0,1], [0,2], [1,2]]
    test_team1 = None
    test_team2 = None

    for dyad in dyads:
        test_team1 = ordered_standings[dyad[0]].team_name
        test_team2 = ordered_standings[dyad[1]].team_name
        h2h = head_to_head_winner(test_team1, test_team2, mcc_games)
        broken = interpret_dyad_result(h2h, dyad, ordered_standings, log_q)
        if (broken):
            log_q.append("TBRK 3-team tie broken by H2H for " + test_team1 +
                         " vs " + test_team2)
            return True

    for dyad in dyads:
        test_team1 = ordered_standings[dyad[0]].team_name
        test_team2 = ordered_standings[dyad[1]].team_name
        oppo_check = common_opp_margin(test_team1, test_team2, mcc_games, log_q)
        broken = interpret_dyad_result(oppo_check, dyad, ordered_standings, log_q)
        if (broken):
            log_q.append("TBRK 3-team tie broken by common oppo for " + test_team1 +
                         " vs " + test_team2)
            return True

    for dyad in dyads:
        test_team1 = ordered_standings[dyad[0]].team_name
        test_team2 = ordered_standings[dyad[1]].team_name
        total_check = total_margin(test_team1, test_team2, mcc_games, log_q)
        broken = interpret_dyad_result(total_check, dyad, ordered_standings, log_q)
        if (broken):
            log_q.append("TBRK 3-team tie broken by total margin for " + test_team1 +
                         " vs " + team_team2)
            return True

    return False

def interpret_dyad_result(result, dyad, ordered_standings, log_q):
    if (result == 0):
        return False

    # if we have an actual result we want to demote the loser to
    # third place and return true
    if (result < 0):
        # dyad[0] won, so dyad[1] should be in third.
        demotion_index = dyad[1]
    else:
        demotion_index = dyad[0]

    # array surgery... take out the demoted and put it in third
    element = ordered_standings.pop(demotion_index)
    ordered_standings.insert(2, element)
    return True
        
def break_two_team_tie(ordered_standings, mcc_games, log_q):
    # find head to head
    h2h = head_to_head_winner(ordered_standings[0].team_name,
                              ordered_standings[1].team_name, mcc_games)
    if (h2h < 0) :
        log_q.append("TBRK tie broken by head-to-head")
        # proper team is in first
        return True
    elif (h2h > 0) :
        log_q.append("TBRK tie broken by head-to-head")
        # promote second
        promote_standings(ordered_standings, 1)
        return True
    else:
        log_q.append("TBRK head-to-head didn't resolve anything")
        oppo_check = common_opp_margin(ordered_standings[0].team_name,
                                       ordered_standings[1].team_name,
                                       mcc_games, log_q)
        if (oppo_check < 0) :
            # proper team is in first
            log_q.append("TBRK tie broken by common opponent margin")
            return True
        elif (oppo_check > 0) :
            # promote second
            log_q.append("TBRK tie broken by common opponent margin")
            promote_standings(ordered_standings, 1)
            return True
        else:
            log_q.append("TBRK common opponent margin didn't resolve anything")

            total_check = total_margin(ordered_standings[0].team_name,
                                       ordered_standings[1].team_name,
                                       mcc_games, log_q)
            if (total_check < 0) :
                return True
            elif (total_check > 0) :
                promote_standings(ordered_standings, 1)
                return True
            else:
                log_q.append("TBRK total margin didn't resolve anything")
                return False

class PossibilityScoreboard:
    def __init__(self, name):
        self.name = name
        self.teams = {}
        self.total_trials = 0
        self.no_winner = 0

    def record_winner(self, winning_team):
        if (winning_team in self.teams):
            self.teams[winning_team] += 1
        else:
            self.teams[winning_team] = 1
        self.total_trials += 1

    def record_no_winner(self):
        self.total_trials += 1
        self.no_winner += 1

    def readable_percent(self, sample_count):
        return(str(int(round(sample_count * 100.0 / self.total_trials, 0))))

    def __str__(self):
        s = self.name + " Simulation:\n"
        sorted_teams = sorted(self.teams.keys(), reverse = True, key = self.teams.__getitem__)
        for team in sorted_teams :
            s += team + " " + str(self.teams[team]) + " [" + self.readable_percent(self.teams[team]) + "%]\n"
        if (self.no_winner > 0):
            print("total trials for no winner: " + str(self.total_trials))
            s += "No Winner " + str(self.no_winner) + " [" + self.readable_percent(self.no_winner) + "%]\n"
        return s
    
def recursive_schedule_fill(time_sorted_games, cur_index, scoreboard):
    if (cur_index >= len(time_sorted_games)) :
        # every time we get to the end of the recursion calculate a winner and
        # add it to the scoreboard
        standings = build_standings(time_sorted_games)
        ordered_standings = sorted(standings.values(), reverse = True, key = standings_sortfunc)
        if (check_minimum_wins(ordered_standings, [])):
            if (break_ties(ordered_standings, time_sorted_games, [])):
                scoreboard.record_winner(ordered_standings[0].team_name)
                return
        scoreboard.record_no_winner()
    else :
        # jump to the node in question and first fill in a home team win
        cur_mcc_game = time_sorted_games[cur_index]
        cur_mcc_game.away_points = 4
        cur_mcc_game.home_points = 55
        recursive_schedule_fill(time_sorted_games, cur_index + 1, scoreboard)
        # then do a road team win
        cur_mcc_game.away_points = 55
        cur_mcc_game.home_points = 4
        recursive_schedule_fill(time_sorted_games, cur_index + 1, scoreboard)
            
def find_possibilities(time_sorted_games):
    cur_index = 0
    future_index_start = -1
    local_games_copy = []
    for cur_mcc_game in time_sorted_games:
        if (cur_mcc_game.away_points is None) :
            if (future_index_start == -1):
                future_index_start = cur_index
        local_games_copy.append(copy.copy(cur_mcc_game))
        cur_index += 1
        
    scoreboard = PossibilityScoreboard("Full Enumeration")
    recursive_schedule_fill(local_games_copy, future_index_start, scoreboard)
    print(str(scoreboard))

def monte_carlo_simulation(time_sorted_games, predictor):
    scoreboard = PossibilityScoreboard("Monte Carlo [" + str(predictor) + "]")
    for run_id in range(0, 10000):
        # make a clean copy of the games
        local_games_copy = []
        for cur_source_game in time_sorted_games:
            local_games_copy.append(copy.copy(cur_source_game))
        for cur_mcc_game in local_games_copy:
            if (cur_mcc_game.away_points is None) :
                try:
                    predictor.predict_game(cur_mcc_game)
                except IndexError as e:
                    print("At least one missing element error prevents " + str(predictor) + " from finishing: ")
                    print(e)
                    return
        standings = build_standings(local_games_copy)
        ordered_standings = sorted(standings.values(), reverse = True, key = standings_sortfunc)
        if (check_minimum_wins(ordered_standings, [])):
            if (break_ties(ordered_standings, local_games_copy, [])):
                scoreboard.record_winner(ordered_standings[0].team_name)
                continue
        scoreboard.record_no_winner()
    print(str(scoreboard))

def find_coach(configuration, team_name, year):
    api_instance = cfbd.CoachesApi(cfbd.ApiClient(configuration))
    coach_list = api_instance.get_coaches(team=team_name, year=year)
    if (len(coach_list) >= 1):
        res = coach_list[0].first_name + ' ' + coach_list[0].last_name
        return res
    else:
        return "No coach found"

def log_stderr_and_clear(log_q):
    for logline in log_q:
        print(logline, file = sys.stderr)
    log_q.clear()

def find_vconf_games(configuration, teams, year, verbose, show_coach):

    curyear_teams = teams.copy()
    if (not testing_control.testing_active()):
        remove_fcs_teams(configuration, curyear_teams, year)
    
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    
    today = datetime.utcnow()
    log_q = []

    pac_timez = timezone(timedelta(hours = -8))
    utc_timez = timezone(timedelta(hours = 0))

    mcc_games = find_mcc_games(api_instance, curyear_teams, year)
    time_ordered_games = sorted(mcc_games.values(), reverse = False, key = timesortfunc)
    any_games_in_future = False
    for cur_mcc_game in time_ordered_games:
        game_time = datetime.strptime(cur_mcc_game.start_date, constants.CFBD_DATE_FMT)
        # the printed stamp is in UTC but strptime reads it as local, so we need to
        # surgically replace it at first and then re-interpret as local.
        #
        pac_game_time = game_time.replace(tzinfo = utc_timez).astimezone(pac_timez)
        pretty_date = datetime.strftime(pac_game_time, "%b %d, %Y")
        if (game_time > today) :
            any_games_in_future = True
            if (verbose) :
                print (cur_mcc_game.away_team + " at " +
                       cur_mcc_game.home_team + " on " +
                       pretty_date)
        else :
            if (verbose) :
                print (cur_mcc_game.away_team + " " + str(cur_mcc_game.away_points) + " at " +
                       cur_mcc_game.home_team + " " + str(cur_mcc_game.home_points) + " on " +
                       pretty_date)
    if (verbose) :
        print()

    if (verbose and any_games_in_future):
        find_possibilities(time_ordered_games)
        monte_carlo_simulation(time_ordered_games, Sampled_Margin_Predictor())
        monte_carlo_simulation(time_ordered_games, Elo_Predictor(configuration))

    standings = build_standings(mcc_games.values())
    if (len(standings) == 0):
        print("There are no standings, possibly because no games were completed.", file = sys.stderr)
        print(str(year) + ", " + str(len(mcc_games)) + ", ,")
        return False

    ordered_standings = sorted(standings.values(), reverse = True, key = standings_sortfunc)
    if (any_games_in_future) :
        if (verbose) :
            for line in ordered_standings:
                print(line)
        print(str(year) + ", " + str(len(mcc_games)) + ", ,")
        return False

    wins_ok = check_minimum_wins(ordered_standings, log_q)
    log_stderr_and_clear(log_q)
    if not wins_ok:
        print("No team has enough wins", file = sys.stderr)
        print(str(year) + ", " + str(len(mcc_games)) + ", ,")
        return False

    ties_ok = break_ties(ordered_standings, mcc_games.values(), log_q)
    log_stderr_and_clear(log_q)
    if (verbose) :
        print(str(year) + " final standings")
        print()
        for line in ordered_standings:
            print(line)
        print()
    if (ties_ok) :
        final_log_line = str(year) + ", " + str(len(mcc_games)) + ", " + \
            ordered_standings[0].team_name + ", " + ordered_standings[0].record_string()
        if (show_coach):
            coach = find_coach(configuration, ordered_standings[0].team_name, year)
            final_log_line += ", " + coach
        print(final_log_line)
        return True
    else:
        print("could not resolve a winner for " + str(year), file = sys.stderr)
        print(str(year) + ", " + str(len(mcc_games)) + ", ,")
        return False
