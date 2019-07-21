class Team_Stint:
  def __init__(self, abbr, name, start, end, next_abbr):
    self.abbr = abbr
    self.name = name
    self.start = start
    self.end = end
    self.next_abbr = next_abbr

  def __str__(self):
    string = f"{self.name} ({self.abbr}): {self.start}-{self.end}."
    if (self.next_abbr is not None):
      string += f" Subsequently {self.next_abbr}"
    return string

  def __repr__(self):
    return self.__str__()