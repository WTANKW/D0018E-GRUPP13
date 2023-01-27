from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from flask_login import UserMixin
#source env/bin/activate
#flask run

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config["MYSQL_USER"] = 'root'
app.config["MYSQL_PASSWORD"] = '123456789'
app.config["MYSQL_DB"] = 'test'

mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM User")
    fetchdata = cur.fetchall()
    cur.close()
 
    return render_template('index.html', data = fetchdata)

@app.route('/other_page')
def annan_funktion():
    return render_template('other_page.html')

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == "GET":
        return render_template('signup.html')

    if request.method == "POST":
        #print("test")
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT EXISTS(SELECT * FROM User WHERE email = %s)", (email,))
        emailInUse = cur.fetchall()
   
        if emailInUse[0][0] or password == "":
            cur.close()
            return render_template('signup.html', data = "Signup Failed, Please try again")

        cur.execute("INSERT INTO User (email, password) VALUES (%s, %s)", (email, password))
        mysql.connection.commit()
        cur.close()

        return redirect("/", code=302)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == "GET":
        return render_template('login.html')

    if request.method == "POST":
        #print("test")
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT EXISTS(SELECT * FROM User WHERE email = %s AND password = %s)", (email, password))
        loginStatus = cur.fetchall()
        print(loginStatus[0][0])
        cur.close()

        if loginStatus[0][0]:
            return redirect('/')

        return redirect("/login", code=302)

if __name__ == "__main__":
    app.run(debug = True)

