class Season:
  def __init__(self, start_year):
    self.start_year = start_year

  def season_id(self):
    return f"{self.start_year}{self.start_year+1}"

  def __str__(self):
    string = f"{self.start_year}-{self.start_year+1} season"
    return string

  def __repr__(self):
    return self.__str__()