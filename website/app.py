from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
#source env/bin/activate
#flask run

app = Flask(__name__)
app.secret_key = 'monkey'

app.config['MYSQL_HOST'] = 'localhost'
app.config["MYSQL_USER"] = 'root'
app.config["MYSQL_PASSWORD"] = 'r5ZA*sagtrhkä9riuktd3ir6%C'
app.config["MYSQL_DB"] = 'test'

mysql = MySQL(app)

@app.route('/')
def index():
    return redirect("/category/All", code=302)

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == "GET":
        return render_template('signup.html')

    if request.method == "POST":
        #print("test")
        email = request.form['email']
        password = request.form['password']
        fname = request.form['fname']
        lname = request.form['lname']
        adress = request.form['adress']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT EXISTS(SELECT * FROM User WHERE Email = %s)", (email,))
        emailInUse = cur.fetchall()
   
        if emailInUse[0][0] or password == "":
            cur.close()
            return render_template('signup.html', loginData = "Signup Failed, Please try again")

        cur.execute("INSERT INTO User (Email, Password, FName, LName, Adress) VALUES (%s, %s, %s, %s, %s)", (email, password, fname, lname, adress))
        mysql.connection.commit()
        cur.execute("INSERT INTO Basket (Customer) VALUES ((SELECT ID FROM User WHERE Email = %s))", (email,))
        mysql.connection.commit()
        cur.close()

        return redirect("/", code=302)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == "GET":
        return render_template('login.html')

    if request.method == "POST":
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


@app.route('/product/<productID>', methods = ['POST', 'GET'])
def product(productID):

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Product WHERE ID = %s", (productID,))
    productInfo = cur.fetchall()
    
    if request.method == "POST":
        cur.execute("INSERT INTO BasketProduct (Basket, Product) VALUES ((SELECT ID FROM Basket WHERE Customer = (SELECT ID FROM User WHERE Email = %s)), %s)", (session['username'], productID))
        mysql.connection.commit()
    
    cur.close()

    if 'username' in session:
        username = session['username']
    else:
        username = None

    return render_template('product.html', loginData = username, productData = productInfo)

@app.route('/category/<categoryName>')
def category(categoryName):
    cur = mysql.connection.cursor()
    if categoryName == "All":
        cur.execute("SELECT * FROM Product")
    else:
        cur.execute("SELECT * FROM Product WHERE Category = %s", (categoryName,))
    categoryInfo = cur.fetchall()
    cur.close()

    if 'username' in session:
        username = session['username']
    else:
        username = None

    return render_template('category.html', loginData = username, categoryData = categoryInfo)

@app.route('/basket')
def basket():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM BasketProduct WHERE Basket = (SELECT ID FROM Basket WHERE Customer = (SELECT ID FROM User WHERE Email = %s))", (session['username'],))
    basketInfo = cur.fetchall()
    cur.close()

    if 'username' in session:
        username = session['username']
    else:
        username = None

    return render_template('basket.html', loginData = username, basketData = basketInfo)