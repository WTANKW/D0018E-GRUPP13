from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
#source env/bin/activate
#flask run

app = Flask(__name__)
app.secret_key = 'monkey'

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

    if 'username' in session:
        username = session['username']
        return render_template('index.html', loginData = "Logged in as: " + username)
    return render_template('index.html', loginData = None)

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
            return render_template('signup.html', loginData = "Signup Failed, Please try again")

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
            session['username'] = request.form['email']
            return redirect('/')

        return redirect("/login", code=302)

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug = True)


@app.route('/product')
def product():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Product")
    productInfo = cur.fetchall()
    cur.close()

    if 'username' in session:
        username = session['username']
    else:
        username = None

    return render_template('product.html', loginData = username, productData = productInfo)