from flask import Flask
from flask import render_template
from flask_assets import Environment, Bundle

import constants
import teams

app = Flask(__name__)

assets = Environment(app)
assets.debug=False
less = Bundle("styles/styles.less", filters="less", output="gen/styles.css", extra={'rel': 'stylesheet/less'})
assets.register("less_all", less)

@app.route("/")
def hello():
  teams_by_abbr = teams.teams_by_abbr()
  teams_by_division = {
    "Pacific": [],
    "Central": [],
    "Metropolitan": [],
    "Atlantic": []
  }
  for abbr, team in teams_by_abbr.items():
    teams_by_division[team.division].append(team)

  return render_template(
    'index.html',
    teams_by_division=teams_by_division
  )

if __name__ == "__main__":
  app.run(debug=True)