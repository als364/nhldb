class Team:
  def __init__(self, abbr, name, stints):
    self.abbr = abbr
    self.name = name
    self.stints = stints

  def stint_by_year(self, year):
    for stint in self.stints:
      if stint.start <= year and stint.end >= year:
        return stint

  def __str__(self):
    string = f"{self.name} ({self.abbr}): {self.stints[0].start}-{self.stints[0].end}"
    if len(self.stints) > 1:
      string += " ("
      for i in range(1, len(self.stints)):
        string += f"As {self.stints[i].name} ({self.stints[i].abbr}) {self.stints[1].start}-{self.stints[1].end}, "
      string = string[:-2]
      string += ")"
    return string

  def __repr__(self):
    return self.__str__()