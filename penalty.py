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

  def stringify_period(self, period):
    if period == 1:
      return "1st period"
    if period == 2:
      return "2nd period"
    if period == 3:
      return "3rd period"
    if period == 4:
      return "1st overtime"
    if period == 5:
      return "2nd overtime"
    if period == 6:
      return "3rd overtime"
    if period == 7:
      return "4th overtime"
    if period == 8:
      return "5th overtime"
    if period == 9:
      return "6th overtime"
    # there has never been more than 6 overtimes in the NHL. but!
    if period == 10:
      return "7th overtime"


  def __str__(self):
    string = f"{self.penalized} {self.penalty_type}"
    if self.drawn_by:
      string += f" against {self.drawn_by}"
    string += f" at {self.period_time} in the {self.stringify_period(self.period)};"
    if self.minutes:
      string += f" {self.minutes} minute "
    string += f"{self.severity}"
    return string

  def __repr__(self):
    return self.__str__()