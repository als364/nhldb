class Team:
  def __init__(self, abbr, name, start, conference, division, previous):
    self.abbr = abbr
    self.name = name
    self.start = start
    self.conference = conference
    self.division = division
    self.previous = previous

  def data_by_year(self, year):
    if year > self.start:
      return {
        "abbr": self.abbr,
        "name": self.name
      }
    else:
      for stint in self.previous:
        if stint.start <= year and stint.end >= year:
          return {
            "abbr": stint.abbr,
            "name": stint.name
          }

  def __str__(self):
    string = f"{self.name} ({self.abbr}): {self.start}-present"
    if len(self.previous) > 0:
      string += " ("
      for i in range(1, len(self.previous)):
        string += f"As {self.previous[i].name} ({self.previous[i].abbr}) {self.previous[1].start}-{self.previous[1].end}, "
      string = string[:-2]
      string += ")"
    return string

  def __repr__(self):
    return self.__str__()