from flask import Flask, render_template
from flask_mysqldb import MySQL
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
    cur.execute("SELECT * FROM Frog")
    fetchdata = cur.fetchall()
    cur.close()
 
    return render_template('index.html', data = fetchdata)

@app.route('/other_page')
def annan_funktion():
    return render_template('other_page.html')

if __name__ == "__main__":
    app.run(debug = True)

