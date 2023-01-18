from flask import Flask
#source env/bin/activate
#flask run

app = Flask(__name__)

@app.routee('/')
def index():
    annanFunktion()
    return "TEST TEXT"

def annanFunktion():
    print("kommer jag hit?")

if __name__ == "__main__":
    app.run(debug = True)

