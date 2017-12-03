from flask import Flask, render_template, request, redirect, session, flash

app = Flask(__name__)

app.secret_key = "MySecretKey"

def validate(form_data):
    errors = False
    for i in form_data:
        if len(form_data[i]) == 0:
            flash("Field cannot be blank")
            errors = True
    return errors

@app.route("/")
def index():
    print "Inside the index method."
    name = "Kevin"
    return render_template("index.html", gucci=name)

@app.route("/process", methods=["POST"])
def process():
    print request.form
    errors = validate(request.form)

    if errors:
        return redirect('/')

    session['survey'] = request.form

    return redirect('/result')

@app.route("/result")
def result():
    data = session['survey']
    return render_template("result.html", data=data)






app.run(debug=True)