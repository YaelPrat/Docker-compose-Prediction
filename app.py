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


class ModelPrediction(db.Model):
    __tablename__ = 'predict'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    oslg = db.Column(db.Float)
    oobp = db.Column(db.Float)
    playoffs = db.Column(db.Float)
    obp = db.Column(db.Float)
    slg = db.Column(db.Float)
    year = db.Column(db.Float)
    g = db.Column(db.Float)
    league_nl = db.Column(db.Float)
    ba = db.Column(db.Float)
    predict = db.Column(db.Float)

    # def __init__(self, OOBP, Playoffs, OBP, SLG, Year, G, League_NL, OSLG, BA, predict):
    #     self.OOBP = float(OOBP)
    #     self.OSLG = float(OSLG)
    #     self.Playoffs = float(Playoffs)
    #     self.OBP = float(OBP)
    #     self.SLG = float(SLG)
    #     self.Year = float(Year)
    #     self.G = float(G)
    #     self.League_NL = float(League_NL)
    #     self.BA = float(BA)
    #     self.predict = float(predict)


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
        oslg = float(request.form['OSLG'])
        oobp = float(request.form['OOBP'])
        playoffs = float(request.form['Playoffs'])
        obp = float(request.form['OBP'])
        slg = float(request.form['SLG'])
        year = float(request.form['Year'])
        g = float(request.form['G'])
        league_nl = float(request.form['League_NL'])
        ba = float(request.form['BA'])

        res = model.predict([[year, obp, slg, ba, playoffs, g, oobp, oslg, league_nl]])
        db_lst = [year, obp, slg, ba, playoffs, g, oobp, oslg, league_nl, res[0]]
        save_db(db_lst)
        return render_template('add_predict.html', res=res[0])
    return render_template('add_predict.html', res='')


def save_db(db_lst):
    new_prediction = ModelPrediction(
        year=db_lst[0],
        obp=db_lst[1],
        slg=db_lst[2],
        ba=db_lst[3],
        playoffs=db_lst[4],
        g=db_lst[5],
        oobp=db_lst[6],
        oslg=db_lst[7],
        league_nl=db_lst[8],
        predict=db_lst[9])

    db.session.add(new_prediction)
    db.session.commit()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5555)
