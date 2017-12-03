from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route("/")
def index():
    name = "Kevin"
    return render_template("index.html", gucci=name)

@app.route("/dashboard")
def dashboard():
    pass

@app.route('/process', methods=['POST'])
def process():
    if int(request.form['number']) == 10:
        print "It equals 10"
    else:
        print "no it don't"

    return redirect("/")





# always the last line for server.py
# must be here
app.run(debug=True)
