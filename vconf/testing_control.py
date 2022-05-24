#
# May 24, 2022
#
#

import os
import schedule_maker

ENV_TESTING_SWITCH = "MCC_TESTING"
ENV_TEST_TYPE = "MCC_TEST_TYPE"

def testing_active():
    return (os.environ.get(ENV_TESTING_SWITCH) != None and
            os.environ.get(ENV_TESTING_SWITCH) != "0")

def choose_test():
    test_type = os.environ.get(ENV_TEST_TYPE)
    if (test_type == "MCC_TEST_2TEAM"):
        return schedule_maker.two_team_schedule()
    elif (test_type == "MCC_TEST_2TEAM_HALF_DONE"):
        return schedule_maker.two_team_schedule_half_done()
    elif (test_type == "MCC_TEST_3TEAM_TIE"):
        return schedule_maker.three_team_tie()
    elif (test_type == "MCC_TEST_2TEAM_TIE"):
        return schedule_maker.two_team_tie_one_doormat()
    elif (test_type == "MCC_TEST_FUTURE_SCHEDULE"):
        return schedule_maker.real_life_future_schedule()
    elif (test_type == "MCC_TEST_4TEAM_TIE"):
        return schedule_maker.four_team_tie()
    elif (test_type == "MCC_TEST_3TEAM_CIRCULAR_LOSSES"):
        return schedule_maker.three_team_tie_circular_losses()
    else:
        raise IndexError("no test found for specified type [" + str(test_type) + "]")
    
