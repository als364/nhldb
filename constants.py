FIRST_YEAR=1980
PRESENT_YEAR=2019
PRESENT_STRING="present"
BROKEN_YEARS=[2005] # lockout

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