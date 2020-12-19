class Team_Stint:
  def __init__(self, abbr, name, start, end):
    self.abbr = abbr
    self.name = name
    self.start = start
    self.end = end

  def __str__(self):
    return f"{self.name} ({self.abbr}): {self.start}-{self.end}."

  def __repr__(self):
    return self.__str__()