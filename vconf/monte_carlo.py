#
# November 16, 2021
#
import secrets

class MC_Predictor:

    def predict_game(self, game):
        pass

    def random_decimal(self):
        three_digit = secrets.randbelow(1000)
        return (three_digit / 1000)


class Home_Team_Predictor(MC_Predictor):

    def predict_game(self, game):
        raw_p = self.random_decimal()
        if (raw_p > .550):
            game.home_points = 21
            game.away_points = 24
        else:
            game.home_points = 24
            game.away_points = 21

