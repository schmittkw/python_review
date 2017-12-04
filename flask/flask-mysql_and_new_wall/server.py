from flask import Flask, render_template, redirect, session, request, flash
# import the Connector function
from mysqlconnection import MySQLConnector
import md5, os, binascii
app = Flask(__name__)
app.secret_key = 'mykeysecret'
# connect and store the connection in "mysql"; note that you pass the database name to the function
mysql = MySQLConnector(app, 'new_wall')
# an example of running a query
def get_current_user():
    user_query = "SELECT * FROM users WHERE users.id = :user_id LIMIT 1"
    query_data = {'user_id': session['id']}
    current_user = mysql.query_db(user_query, query_data)
    return current_user[0]

@app.route('/')
def index():
    print "Inside index method."
    query = "select first_name, last_name, id, email, created_at, password, salt FROM users"

    
    users = mysql.query_db(query)

    return render_template("index.html", data=users)

@app.route('/process', methods=['POST'])
def process():
    salt = binascii.b2a_hex(os.urandom(15))
    password = md5.new(request.form['password'] + salt).hexdigest()

    print "**********************"
    query = """
        insert into users (first_name, last_name, email, salt, password, created_at, updated_at) 
        values (:first_name, :last_name, :email, :salt, :password, now(), now())
    """
    data = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "salt": salt,
        "password": password
    }

    mysql.query_db(query, data)
    print "Created New User"
    email = request.form['email']

    user_query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
    query_data = {'email': email}

    user = mysql.query_db(user_query, query_data)

    session['first_name'] = user[0]['first_name']
    session['last_name'] = user[0]['last_name']
    session['email'] = user[0]['email']
    session['id'] = user[0]['id']
    session['is_logged_in'] = True

    print "Assigned Session values."
    
    return redirect('/dashboard')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user_query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
    query_data = {'email': email}
    user = mysql.query_db(user_query, query_data)
    if len(user) != 0:
        encrypted_password = md5.new(password + user[0]['salt']).hexdigest()
        if user[0]['password'] == encrypted_password:
            # this means we have a successful login!
            session['first_name'] = user[0]['first_name']
            session['last_name'] = user[0]['last_name']
            session['email'] = user[0]['email']
            session['id'] = user[0]['id']
            session['is_logged_in'] = True
            return redirect('/dashboard')
        else:
            # invalid password!
            flash('Invalid Credentials')
            return redirect('/')
    else:
        # invalid email!
        flash('Invalid Credentials')
        return redirect('/')

@app.route('/dashboard')
def dashboard():
    if session['is_logged_in'] != True:
        return redirect('/')
    else:
        # could use current_user function here also
        first_name = session['first_name']
        last_name = session['last_name']
        id = session['id']
        email = session['email']

        return render_template('dashboard.html', first_name=first_name, last_name=last_name, email=email, id=id)

@app.route('/logout')
def logout():
    session.clear()
    session['is_logged_in'] = False
    return redirect("/")






app.run(debug=True)
