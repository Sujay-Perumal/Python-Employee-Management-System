from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import stripe
app = Flask(__name__)

app.secret_key = 'Crapone1!'

STRIPE_PUBLISHABLE_KEY = '  '
STRIPE_SECRET_KEY = 'sk_test_ZZREzlsEn37u4cc4Jr9CSbaL00n7zZOhbN'

stripe.api_key = STRIPE_SECRET_KEY

# database connection details 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Crapone1!'
app.config['MYSQL_DB'] = 'pythonlogin'

# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/pythonlogin/ - this will be the login page, need to use both GET and POST requests
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in the database
        if account:
            # Create session data, can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg='')
    

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))
     
# http://localhost:5000/pythonlogin/register - this will be the registration page, need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        birth = request.form['birth']
        title = request.form['title']
        phone = request.form['Num']
        access = request.form['access']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', [username])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z]+', username):
            msg = 'Username must contain only characters!'
        elif not re.match(r'[0-9]+',phone):
            msg = 'Phone number must only contain numbers!'
        elif not re.match(r'(3[01]|[12][0-9]|0[1-9])/(1[0-2]|0[1-9])/[0-9]{4}$',birth):
            msg = 'Date of birth not in correct format!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)', ([username], [password], [email], [birth],[title],[phone],[access]))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythonlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythonlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythonlogin/payments - this will be the payment page, only accessible for loggedin users
@app.route('/pythonlogin/payments')
def payments():
    msg =''
    #Check if user is loggedin
    if 'loggedin' in session:
        # Amount in cents
        amount = 750000
        #Create a customer template to be used for payments
        customer = stripe.Customer.create(
            email= 'test@test.com',
            source= 'tok_mastercard',
        )
        #Authorize the payment to the customer
        charge = stripe.Charge.create(
            amount=amount,
            currency='gbp',
            customer=customer.id,
            description='employee monthly payment'
        )
    #User is loggedin show them the payment page
        return render_template('payments.html',msg=msg)
    #User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythonlogin/verify - this will be the verification page, only accessible for loggedin users, need both GET and POST requests
@app.route('/pythonlogin/verify',methods =['GET','POST'])
def verify():
    msg = ''
    #Check if user is loggedin
    if 'loggedin' in session:
        #Check if user has entered details into the form
        if request.method == 'POST' and 'username' in request.form:
            username = request.form['username']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            #Search for user in the database
            cursor.execute('SELECT * FROM accounts WHERE username = %s',[username])
            account = cursor.fetchone()
            #Check if account exists in the database
            if account:
                session['loggedin'] = True
                session['username'] = account['username']
                session['id'] = account['id']
                global confirm
                confirm = session['id']
                #Redirect user to the editing page
                return redirect(url_for('edit'))
            else:   
                #User doesn't exist in the database
                msg = 'user does not exist'
        return render_template('verify.html',msg=msg)
    #User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythonlogin/edit - this will be the editing details page, only accessible for loggedin users, need both GET and POST requests
@app.route('/pythonlogin/edit', methods = ['GET','POST'])
def edit():
    msg = ''
    #Check if user is loggedin
    if 'loggedin' in session:
        # Give shoices for databases to select
        choices = ['accounts','payments']
        # Give choices from the first database (accounts)
        choices2 = ['username','password','email','birth','title','Num','access']
        #Check what database is selected
        if choices == 'accounts':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            #Search for account in the database
            cursor.execute('SELECT * FROM accounts WHERE id = %s',confirm)
            account = cursor.fetchone()
            #Check account exists in the database
            if account:
                #Get details from the database
                session['loggedin'] = True
                session['username'] = account['username']
                session['password'] = account['password']
                session['email'] = account['email']
                session['birth'] = account['birth']
                session['title'] = account['title']
                session['Num'] = account['Num']
                session['access'] = account['access']
                #Give user choices from the database
                if choices2 == 'username':
                    username = input("enter the user's new username")
                    #Update values in the database with the details entered
                    query = 'UPDATE accounts SET username = %s WHERE username = %s'
                    values = (username,session['username'])
                    cursor.execute(query,values)
                    mysql.commit()
                    msg = 'User details updated'
                    return render_template('edit.html',msg=msg)
                if choices2 == 'password':
                    password = input("enter the user's new password")
                    #Update values in the database with the details entered
                    query = 'UPDATE accounts SET password = %s WHERE password = %s'
                    values = (password,session['password'])
                    cursor.execute(query,values)
                    mysql.commit()
                    msg = 'User details updated'
                    return render_template('edit.html',msg=msg)
                if choices2 == 'email':
                    email = input("enter the user's new email")
                    #Update values in the database with the details entered
                    query = 'UPDATE accounts SET email = %s WHERE email = %s'
                    values = (email,session['email'])
                    cursor.execute(query,values)
                    mysql.commit()
                    msg = 'User details updated'
                    return render_template('edit.html',msg=msg)
                if choices2 == 'birth':
                    birth = input("enter the user's new birth date")
                    #Update values in the database with the details entered
                    query = 'UPDATE accounts SET birth = %s WHERE birth = %s'
                    values = (birth,session['birth'])
                    cursor.execute(query,values)
                    mysql.commit()
                    msg = 'User details updated'
                    return render_template('edit.html',msg=msg)
                if choices2 == 'title':
                    title = input("enter the user's new job title")
                    #Update values in the database with the details entered
                    query = 'UPDATE accounts SET title = %s WHERE title = %s'
                    values = (title,session['title'])
                    cursor.execute(query,values)
                    mysql.commit()
                    msg = 'User details updated'
                    return render_template('edit.html',msg=msg)
                if choices2 == 'Num':
                    Num = input("enter the user's new Phone number")
                    #Update values in the database with the details entered
                    query = 'UPDATE accounts SET Num = %s WHERE Num = %s'
                    values = (Num,session['Num'])
                    cursor.execute(query,values)
                    mysql.commit()
                    msg = 'User details updated'
                    return render_template('edit.html',msg=msg)
                if choices2 == 'access':
                    access = input("enter the user's new access level (Yes or No)")
                    #Update values in the database with the details entered
                    query = 'UPDATE accounts SET access = %s WHERE access = %s'
                    values = (access,session['access'])
                    cursor.execute(query,values)
                    mysql.commit()
                    msg = 'User details updated'
                    return render_template('edit.html',msg=msg)
            else:
                #User not in database
                msg = 'User does not exist in database'
                return render_template('edit.html',msg=msg)
        #Check what database is selected
        if choices == 'payments':
            cursor = mysql.connection.cursor(MySQLdb.cursors.Dictcursor)
            #Search for account in database
            cursor.execute('SELECT*FROM payments WHERE id = %s',confirm)
            payment = cursor.fetchone()
            if account:
                #Get details from the database
                session['loggedin'] = True
                session['AccNum'] = payment['AccNum']
                session['SortCode'] = payment['SortCode']
                choices2 = ['AccNum','SortCode']
                #Give user choices from the database
                if choices2 == 'AccNum':
                    AccNum = input("Enter the user's new account number")
                    #Update values in the database with the details entered
                    query = 'UPDATE payments SET AccNum = %s WHERE AccNum = %s'
                    values = (AccNum,session['AccNum'])
                    cursor.execute(query,values)
                    mysql.commit()
                    msg = 'User details updated'
                    return render_template('edit.html',msg=msg)
                if choices2 == 'SortCode':
                    SortCode = input("Enter the user's new sort code")
                    #Update values in the database with the details entered
                    query = 'UPDATE payments SET SortCode = % WHERE SortCode = %s'
                    valuse = (SortCode,session['SortCode'])
                    cursor.execute(query,values)
                    mysql.commit()
                    msg = 'User details updated'
                    return render_template('edit.html',msg=msg)
            else:
                #User not in database
                msg = 'User does not exist in database'
                return render_template('edit.html',msg=msg)
        #User is loggedin show them the edit page
        return render_template('edit.html',choices=choices, choices2=choices2)
    #User is not loggedin redirect to login page
    return redirect(url_for('login')

                                     
