from flask import Flask, render_template, redirect, session, request, flash
# import the Connector function
from mysqlconnection import MySQLConnector
import md5, os, binascii
app = Flask(__name__)
app.secret_key = 'mykeysecret'
# connect and store the connection in "mysql"; note that you pass the database name to the function
mysql = MySQLConnector(app, 'newer_wall')
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

        query = "SELECT users.id as message_user_pk, users.first_name as message_user_first_name, users.last_name as message_user_last_name, messages.id as message_pk, messages.message, messages.updated_at as message_timestamp, comments.id as comment_pk, comments.message_id, comments.comment, comments.updated_at as comment_timestamp, users2.id as comment_user_pk, users2.first_name as comment_user_first_name, users2.last_name as comment_user_last_name FROM users LEFT JOIN messages ON users.id = messages.user_id LEFT JOIN comments ON messages.id = comments.message_id LEFT JOIN users as users2 ON users2.id = comments.user_id;"

        messages = mysql.query_db(query)
        new_messages = []

        message_ids = []
        
        for message in messages:
            if message['message_pk'] not in message_ids:
                message_ids.append(message['message_pk'])
                myMsgObj = {
                    'pk': message['message_pk'],
                    'message': message['message'],
                    'user_first_name': message['message_user_first_name'],
                    'user_last_name': message['message_user_last_name'],
                    'timestamp': message['message_timestamp'],
                    'comments': []
                }
                if message['comment_pk'] != None:
                    #create a comment obj
                    myCommentObj = {
                        'pk' : message['comment_pk'],
                        'user_first_name' : message['comment_user_first_name'],
                        'user_last_name' : message['comment_user_last_name'],
                        'comment' : message['comment'],
                        'timestamp' : message['comment_timestamp']
                    }
                    myMsgObj['comments'].append(myCommentObj)
                new_messages.append(myMsgObj)
            else:
                #just want to extract the comment                
                myCommentObj = {
                    'pk' : message['comment_pk'],
                    'user_first_name' : message['comment_user_first_name'],
                    'user_last_name' : message['comment_user_last_name'],
                    'comment' : message['comment'],
                    'timestamp' : message['comment_timestamp']
                }
                new_messages[-1]['comments'].append(myCommentObj)


        # message = {
        #     'pk': 1,
        #     'user_name': 'Cody',
        #     'message' : 'my Message',
        #     'comments': [
        #         {
        #             'pk' : 1,
        #             'user_name', 'Cody'
        #             'comment': 'My first Comment'
        #         },
        #         {
        #             'pk' : 2,
        #             'user_name', 'Cody'
        #             'comment': 'My second Comment'
        #         },
        #     ]
        # }

        return render_template('dashboard.html', messages=new_messages, first_name=first_name, last_name=last_name, email=email, id=id)

@app.route('/logout')
def logout():
    session.clear()
    session['is_logged_in'] = False
    return redirect("/")

@app.route('/messages', methods=['POST'])
def messages():
    if request.form['message'] == '':
        flash('Message cannot be blank')
        return redirect('/dashboard')
    else:
        query = 'insert into messages (message, user_id, created_at, updated_at) values (:message, :user_id, now(), now())'
        data = {
            'message': request.form['message'],
            'user_id': session['id']
        }
        mysql.query_db(query, data)
        return redirect('/dashboard')

@app.route('/comments', methods=['POST'])
def comment():
    if request.form['comment'] == '':
        flash('Comment cannot be blank')
        return redirect('/dashboard')
    query = 'INSERT INTO comments (comment, message_id, user_id, created_at, updated_at) VALUES (:comment, :message_id, :user_id, NOW(), NOW())'
    data = {
        'comment' : request.form['comment'],
        'message_id' : request.form['message_id'],
        'user_id' : session['id']
    }
    mysql.query_db(query, data)
    return redirect('/dashboard')






app.run(debug=True)
