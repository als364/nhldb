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
			return "1st"
		if period == 2:
			return "2nd"
		if period == 3:
			return "3rd"

	def __str__(self):
	  string = f"{self.penalized} {self.penalty_type}"
	  if self.drawn_by:
	  	string += f" against {self.drawn_by}"
	  string += f" at {self.period_time} in the {self.stringify_period(self.period)}; {self.minutes} minute {self.severity}"
	  return string

	def __repr__(self):
	  return self.__str__()