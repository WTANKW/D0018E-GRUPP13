from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import threading
import time

sem = threading.Semaphore()
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
        email = request.form['email']
        password = request.form['password']
        fname = request.form['fname']
        lname = request.form['lname']
        adress = request.form['adress']
        
        cur = mysql.connection.cursor()

        #checks if your email is already in use
        cur.execute("SELECT EXISTS(SELECT * FROM User WHERE Email = %s)", (email,))
        emailInUse = cur.fetchall()
   
        if emailInUse[0][0] or password == "" or fname == "" or lname == "" or adress == "" :
            cur.close()
            return render_template('signup.html', signupData = "Signup Failed, Please try again")

        #creates your account
        cur.execute("INSERT INTO User (Email, Password, FName, LName, Adress) VALUES (%s, %s, %s, %s, %s)", (email, password, fname, lname, adress))
        mysql.connection.commit()

        #creates your basket
        cur.execute("INSERT INTO Basket (Customer) VALUES ((SELECT ID FROM User WHERE Email = %s))", (email,))
        mysql.connection.commit()
        
        session['username'] = request.form['email']

        #gets userid
        cur.execute("SELECT ID FROM User WHERE email = %s", (session['username'],))
        userID = cur.fetchall()
        session['userID'] = userID[0][0]

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
        
        
        if loginStatus[0][0]:
            session['username'] = request.form['email']

            cur.execute("SELECT ID FROM User WHERE email = %s", (session['username'],))
            userID = cur.fetchall()
            session['userID'] = userID[0][0]
            cur.close()
            return redirect('/')

        cur.close()
        return render_template('login.html', loginData = "Login Failed, Please try again")

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug = True)


@app.route('/product/<productID>', methods = ['POST', 'GET'])
def product(productID):
    cur = mysql.connection.cursor()
    admin = ()
    #checks if user is admin
    if 'username' in session:
        cur.execute('''SELECT UserID FROM Admin WHERE UserID = %s''', (session['userID'],))
        admin = cur.fetchall()

    if request.method == "POST" and 'username' in session and request.form['addProduct'] != "-1":
        #if the product doesn't exist a new row is created otherwise 1 is added to the amount
        cur.execute('''INSERT INTO BasketProduct (Basket, Product, Amount) 
                        VALUES ((SELECT ID FROM Basket WHERE Customer = %s), %s, 1)
                        ON DUPLICATE KEY UPDATE Amount = Amount + VALUES(Amount)
                        ''', (session['userID'], productID))
        mysql.connection.commit()

    if request.method == "POST" and 'username' in session and request.form['changeStock'] != "-1":
        newStock = request.form['changeStock']
        #updates stock
        cur.execute('''UPDATE Product SET Quantity = %s WHERE ID = %s
                    ''', (newStock, productID))
        mysql.connection.commit()

    if request.method == "POST" and 'username' in session and request.form['grade'] != "-1" and request.form['grade']:
        grade = request.form['grade']
        comment = request.form['comment']
        #posts comment
        cur.execute('''INSERT INTO Comment (UserID, ProductID, text, grade) 
                        VALUES (%s, %s, %s, %s)
                        ''', (session['userID'], productID, comment, grade))
        mysql.connection.commit()

    #fetches the productinfo from the specific product
    cur.execute("SELECT * FROM Product WHERE ID = %s", (productID,))
    productInfo = cur.fetchall()

    #fetches comments
    cur.execute("SELECT * FROM Comment WHERE ProductID = %s", (productID,))
    gradeInfo = cur.fetchall()

    cur.close()

    if 'username' in session:
        username = session['username']
    else:
        username = None

    return render_template('product.html', loginData = username, productData = productInfo, gradeInfo = gradeInfo, admin = admin)

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

    orderStatus = ""

    cur = mysql.connection.cursor()
    if request.method == "POST":
        if request.form['productID'] != "-1":
            productID = request.form['productID']

            #decrements amount by 1
            cur.execute('''UPDATE BasketProduct SET Amount = (Amount - 1) WHERE Basket = 
                        (SELECT ID FROM Basket WHERE Customer = %s) and Product = %s
                        ''', (session['userID'], productID))
            mysql.connection.commit()

            #gets the amount of the BasketProduct
            cur.execute('''SELECT Amount FROM BasketProduct WHERE Basket = 
                        (SELECT ID FROM Basket WHERE Customer = %s) and Product = %s
                        ''', (session['userID'], productID))
            amount = cur.fetchall()

            if(amount[0][0] <= 0):
                #deletes row if the amount is 0
                cur.execute('''DELETE FROM BasketProduct WHERE Basket = 
                            (SELECT ID FROM Basket WHERE Customer = %s) and Product = %s
                            ''', (session['userID'], productID))   
                mysql.connection.commit()

    #fetches all your BasketProducts
    cur.execute('''SELECT Amount, Product FROM BasketProduct WHERE Basket = 
                (SELECT ID FROM Basket WHERE Customer = %s)''', (session['userID'],))
    basketInfo = cur.fetchall()

    cur.execute('''SELECT Name, Price FROM Product WHERE ID IN  
                (SELECT Product FROM BasketProduct WHERE Basket = 
                (SELECT ID FROM Basket WHERE Customer = %s))''', (session['userID'],))
    productInfo = cur.fetchall()

    if request.method == "POST" and request.form['placeOrder'] != "-1":
            enoughInStock = True
            #gets the amount in stock
            cur.execute('''SELECT Quantity FROM Product WHERE ID IN 
                    (SELECT Product FROM BasketProduct WHERE Basket =
                    (SELECT ID FROM Basket WHERE Customer = %s))''', (session['userID'],))
            itemsInStock = cur.fetchall()

            #gets the amount the customer wants to order
            cur.execute('''SELECT Amount, Product FROM BasketProduct WHERE Basket = 
                    (SELECT ID FROM Basket WHERE Customer = %s)''', (session['userID'],))
            itemsInBasket = cur.fetchall()

            for i in range(0, len(itemsInStock)):
                if itemsInBasket[i][0] > itemsInStock[i][0]:
                   enoughInStock = False
                   orderStatus = "Your order could not be made"

            if enoughInStock == True:
                #jobbar på att ta bort items in stock
                for i in range(0, len(itemsInBasket)):
                    #removes items from stock
                    cur.execute('''UPDATE Product SET Quantity = (Quantity - %s) WHERE ID = 
                            %s''', (itemsInBasket[i][0], itemsInBasket[i][1]))
                mysql.connection.commit()
                #creates an order
                cur.execute("INSERT INTO Orders (Customer) VALUES(%s)", (session['userID'],))
                cur.execute("SELECT * FROM Orders WHERE ID = LAST_INSERT_ID()")
                mysql.connection.commit()
                orderID = cur.fetchall()[0][0]

                #creates OrderProducts connected to your order
                for i in range(0, len(basketInfo)):
                    cur.execute("INSERT INTO OrderProduct (Product, OrderID, Price, Amount) VALUES (%s, %s, %s, %s)", (basketInfo[i][1], orderID, productInfo[i][1], basketInfo[i][0]))
                mysql.connection.commit()
                
                #deletes all the products in your basket
                cur.execute('''DELETE FROM BasketProduct WHERE Basket = 
                            (SELECT ID FROM Basket WHERE Customer = %s)
                            ''', (session['userID'],))  
                mysql.connection.commit()

            #fetches all your BasketProducts
            cur.execute('''SELECT Amount, Product FROM BasketProduct WHERE Basket = 
                    (SELECT ID FROM Basket WHERE Customer = %s)''', (session['userID'],))
            basketInfo = cur.fetchall()

            cur.execute('''SELECT Name, Price FROM Product WHERE ID IN  
                    (SELECT Product FROM BasketProduct WHERE Basket = 
                    (SELECT ID FROM Basket WHERE Customer = %s))''', (session['userID'],))
            productInfo = cur.fetchall()

    cur.close()
    return render_template('basket.html', loginData = username, basketData = basketInfo, productData = productInfo, orderStatus = orderStatus)

@app.route('/orders')
def orders():
    cur = mysql.connection.cursor()
    #getting all order IDs from specific customer
    cur.execute('''SELECT ID FROM Orders WHERE Customer = %s''', (session['userID'],))
    orderID = cur.fetchall()

    productInfo = []
    orderProductInfo = []
    orderPrice = []

    for i in range(0, len(orderID)):
        #getting all the products in the different orders
        cur.execute('''SELECT Name FROM Product WHERE ID IN 
                    (SELECT Product FROM OrderProduct WHERE OrderID = %s)''', (orderID[i][0],))
        productInfo.append(cur.fetchall()) 

        #getting the the price and amount of the products in the order
        cur.execute('''SELECT Price, Amount FROM OrderProduct WHERE OrderID = %s''', (orderID[i][0],))
        orderProductInfo.append(cur.fetchall()) 

        #calculating the total price of the order
        curPrice = 0
        for j in range(0, len(orderProductInfo[i])):
            curPrice = curPrice + orderProductInfo[i][j][0] * orderProductInfo[i][j][1]
        orderPrice.append(curPrice) 

    cur.close()
    return (render_template('orders.html', orderData = orderID, productData = productInfo, orderProductData = orderProductInfo, orderPrice = orderPrice))
   
