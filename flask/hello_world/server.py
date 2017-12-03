from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    name = "Kevin"
    return render_template("index.html", gucci=name)

@app.route("/dashboard")
def dashboard():
    pass







# always the last line for server.py
# must be here
app.run(debug=True)
