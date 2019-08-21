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
  return render_template(
    'index.html',
    teams=teams.teams_by_abbr().keys()
  )

if __name__ == "__main__":
  app.run(debug=True)