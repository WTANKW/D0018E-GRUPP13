from flask import Flask, render_template
#source env/bin/activate
#flask run

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/other_page')
def annan_funktion():
    return render_template('other_page.html')

if __name__ == "__main__":
    app.run(debug = True)

