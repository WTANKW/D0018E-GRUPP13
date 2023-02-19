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

        #checks if your email is already in use
        cur.execute("SELECT EXISTS(SELECT * FROM User WHERE Email = %s)", (email,))
        emailInUse = cur.fetchall()
   
        if emailInUse[0][0] or password == "":
            cur.close()
            return render_template('signup.html', loginData = "Signup Failed, Please try again")

        #creates your account
        cur.execute("INSERT INTO User (Email, Password, FName, LName, Adress) VALUES (%s, %s, %s, %s, %s)", (email, password, fname, lname, adress))
        mysql.connection.commit()

        #creates your basket
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

        #checks if your account exists
        cur.execute("SELECT EXISTS(SELECT * FROM User WHERE email = %s AND password = %s)", (email, password))
        loginStatus = cur.fetchall()
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
    
    #fetches the productinfo from the specific product
    cur.execute("SELECT * FROM Product WHERE ID = %s", (productID,))
    productInfo = cur.fetchall()
    
    if request.method == "POST":
        #to check if the product already exists in the basket
        cur.execute('''SELECT EXISTS(SELECT * FROM BasketProduct WHERE Basket = 
                    (SELECT ID FROM Basket WHERE Customer = 
                    (SELECT ID FROM User WHERE Email = %s)) and Product = %s)
                    ''', (session['username'], productID))

        productExistsInBasket = cur.fetchall()

        if productExistsInBasket[0][0] == 0:
            #if the product doesn't exist a new row is created
            cur.execute('''INSERT INTO BasketProduct (Basket, Product, Amount) 
                        VALUES ((SELECT ID FROM Basket WHERE Customer = 
                        (SELECT ID FROM User WHERE Email = %s)), %s, 1)
                        ''', (session['username'], productID))
        else:
            #if the product exists 1 is added to the current amout
            cur.execute('''UPDATE BasketProduct SET Amount = (Amount + 1) WHERE Basket = 
                    (SELECT ID FROM Basket WHERE Customer = 
                    (SELECT ID FROM User WHERE Email = %s)) and Product = %s
                    ''', (session['username'], productID))

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
        #fetches data from all products
        cur.execute("SELECT * FROM Product")
    else:
        #fetches data from the products in the specific category
        cur.execute("SELECT * FROM Product WHERE Category = %s", (categoryName,))
    categoryInfo = cur.fetchall()
    cur.close()

    if 'username' in session:
        username = session['username']
    else:
        username = None

    return render_template('category.html', loginData = username, categoryData = categoryInfo)

@app.route('/basket', methods = ['POST', 'GET'])
def basket():
    if 'username' in session:
        username = session['username']
    else:
        username = None

    cur = mysql.connection.cursor()
    if request.method == "POST":
        productID = request.form['productID']

        #decrements amount by 1
        cur.execute('''UPDATE BasketProduct SET Amount = (Amount - 1) WHERE Basket = 
                        (SELECT ID FROM Basket WHERE Customer = 
                        (SELECT ID FROM User WHERE Email = %s)) and Product = %s
                        ''', (session['username'], productID))
        mysql.connection.commit()

        #gets the amount of the BasketProduct
        cur.execute('''SELECT Amount FROM BasketProduct WHERE Basket = 
                    (SELECT ID FROM Basket WHERE Customer = 
                    (SELECT ID FROM User WHERE Email = %s)) and Product = %s
                    ''', (session['username'], productID))

        amount = cur.fetchall()

        if(amount[0][0] <= 0):
            #deletes row if the amount is 0
            cur.execute('''DELETE FROM BasketProduct WHERE Basket = 
                        (SELECT ID FROM Basket WHERE Customer = 
                        (SELECT ID FROM User WHERE Email = %s)) and Product = %s
                        ''', (session['username'], productID))   
            mysql.connection.commit()

    #fetches all your BasketProducts
    cur.execute('''SELECT * FROM BasketProduct WHERE Basket = 
                (SELECT ID FROM Basket WHERE Customer = 
                (SELECT ID FROM User WHERE Email = %s))''', (session['username'],))
    basketInfo = cur.fetchall()
    cur.close()
    
    return render_template('basket.html', loginData = username, basketData = basketInfo)