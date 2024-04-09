import os
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sklearn
import joblib

model = joblib.load('liner_pikel.pkl')
db_username = os.environ['DB_USERNAME']
db_password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_NAME']
db_host = os.environ['DB_HOST']
db_port = os.environ['DB_PORT']
db_uri = f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
print(f"Connecting db @{db_uri}")
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy()
db.init_app(app)
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        self.name = name

@app.route("/")
def home():
    return "Hello from my Containerized Server"

@app.route('/users', methods=['POST'])
def add_user():
    request_data = request.get_json()
    u_name = request_data['name']
    new_user = User(
        name=u_name)
    db.session.add(new_user)
    db.session.commit()
    return "User added successfully"

@app.route('/users')
def show_users():
    users = User.query.all()
    user_list = {}
    for user in users:
        user_list[user.id] = user.name
    return user_list


@app.route('/add_predict', methods=['POST', 'GEt'])
def add_predict():
    if request.method == 'POST':
        OSLG = float(request.form['OSLG'])
        OOBP = float(request.form['OOBP'])
        Playoffs = float(request.form['Playoffs'])
        OBP = float(request.form['OBP'])
        SLG = float(request.form['SLG'])
        Year = float(request.form['Year'])
        G = float(request.form['G'])
        League_NL = float(request.form['League_NL'])
        BA = float(request.form['BA'])

        res = model.predict([[Year,OBP,SLG,BA,Playoffs,G,OOBP,OSLG,League_NL]])
        return render_template('add_predict.html', res = res)
    return render_template('add_predict.html', res = '')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5555)