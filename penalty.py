import constants

class Penalty:
  def __init__(self, penalized, drawn_by, penalty_type, severity, minutes, team, period, period_time):
    self.penalized = penalized
    self.drawn_by = drawn_by
    self.penalty_type = penalty_type
    self.severity = severity
    self.minutes = minutes
    self.team = team
    self.period = period
    self.period_time = period_time

  def __str__(self):
    string = f"{self.penalized} {self.penalty_type}"
    if self.drawn_by:
      string += f" against {self.drawn_by}"
    string += f" at {self.period_time} in the {constants.stringify_period(self.period)};"
    if self.minutes:
      string += f" {self.minutes} minute "
    string += f"{self.severity}"
    return string

  def __repr__(self):
    return self.__str__()