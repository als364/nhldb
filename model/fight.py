import constants


class Fight:
    def __init__(self, participant_a, participant_b, date, period, period_time, winner):
        self.participant_a = participant_a
        self.participant_b = participant_b
        self.date = date
        self.period = period
        self.period_time = period_time
        self.winner = winner

    def __str__(self):
        string = (
            f"{self.participant_a} vs. {self.participant_b}; "
            f"{self.period_time} in the {constants.stringify_period(self.period)} on {self.date}."
        )
        if self.winner is None:
            string += "Fight was a draw."
        else:
            string += f"Fight won by {self.winner}"

    def __repr__(self):
        return self.__str__()
