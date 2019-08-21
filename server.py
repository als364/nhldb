from flask import Flask
from flask import render_template
from flask import request
from flask_assets import Environment, Bundle

import analyze
import constants
import teams

app = Flask(__name__)

assets = Environment(app)
assets.debug=False
less = Bundle("styles/styles.less", filters="less", output="gen/styles.css")
assets.register("less_all", less)
js = Bundle("js/index.js", output="gen/scripts.js")
assets.register("js_all", js)

@app.route("/")
def serve():
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

@app.route("/calculate", methods=["POST"])
def calculate():
  abbrs = request.get_json()["abbrs"]
  data = {abbr: {} for abbr in abbrs}
  for abbr in abbrs:
    other_abbrs = [other_abbr for other_abbr in abbrs if other_abbr != abbr]
    # us vs the world
    collective = analyze.analyze(abbr, other_abbrs)
    data[abbr] = {"collective": collective}
    individuals = {}
    # us vs everyone else individually
    for other_abbr in other_abbrs:
      individuals[other_abbr] = analyze.analyze(abbr, [other_abbr])
    data[abbr]["individuals"] = individuals
  return render_template(
    "data.html",
    data_by_abbr=data
  )

###############################################################################

if __name__ == "__main__":
  app.run(debug=True)