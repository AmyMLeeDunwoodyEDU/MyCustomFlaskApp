from flask import Flask, render_template, request, session, redirect, url_for
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from tzlocal import get_localzone
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = 'top-secret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mycustomflaskapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class player_stats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    namedpet = db.Column(db.String(100), nullable=True)
    username = db.Column(db.String(100), nullable=True, unique=True)
    password = db.Column(db.String(100), nullable=True)
    pickedpet = db.Column(db.String(50), nullable=True)
    datecreated = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    #store hunger, fun, sleep, and health values into here if the person closes the app
    #basically have a save data sort of kind of system
        #have a log-in system so the user can use an old save-file
    
with app.app_context():
    db.create_all()
    
@app.route('/', methods=['GET','POST'])
def pickapet():
    
    pickedpet = None
    namedpet = None
    if request.method == 'POST':
        pickedpet = request.form.get('pickedpet', '').strip()
        namedpet = request.form.get('namedpet', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        form_type = request.form.get('form_name').strip() 
        
        if player_stats.query.filter_by(username=username).count() > 0:
            error = f"Username already exists."
            return render_template("pickapet.html", pickedpet=pickedpet, namedpet=namedpet, error=error)
        
        if form_type == "login":
            pass
            # summary: make it so the player if they are registered already is able to continue their game.
            # pseudocode: if player registered, redirect to yourPet, but with their data at a saved point of the game.
        
        if form_type == "pickingapet":    
            if pickedpet == 'Dog':
                new_player = player_stats(
                    namedpet=namedpet,
                    pickedpet=pickedpet,
                    username=username,
                    password=password
                    )
                db.session.add(new_player)
                db.session.commit()
            if pickedpet == 'Cat':
                new_player = player_stats(
                    namedpet=namedpet,
                    pickedpet=pickedpet,
                    username=username,
                    password=password
                    )
                db.session.add(new_player)
                db.session.commit()
        new_player = player_stats.query.filter_by(username=username).first()
        return render_template("pickapet.html", pickedpet=pickedpet, namedpet=namedpet, player_stats=new_player)
    return render_template("pickapet.html", pickedpet=pickedpet, namedpet=namedpet)

@app.route('/yourPet')
def yourPet():
    now = datetime.now()
    current_year = now.year
    current_month = now.strftime("%B")
    current_day = now.day
    current_time = now.strftime("%I:%M:%S %p")
    
    pickedpet = request.form.get('pickedpet', '').strip()
    
    data = player_stats.query.filter_by(pickedpet=pickedpet).first()
    
    if 'Dog' == 'Cat' != data.type(pickedpet):
        return redirect(url_for('pickapet'))
    
    if 'Cat' == data.type(pickedpet):
        hunger = 100
        sleep = 100
        health = 100
        fun = 100
        
        playerID = request.form.get('playerID', '').strip()
        
        user = player_stats.query.filter_by(id=playerID).first()
        
        while hunger > 0:
            hunger -= 1
            if hunger < 50:
                health -= 2
                if hunger == 0:
                    if health == 0:
                        db.session.delete(user)
                        db.session.commit()
                        return redirect('pickapet.html')
                    # delete the user if the pet has 0 health via hunger

        while sleep > 0:
            sleep -= 2
            if sleep < 50:
                health -= 2
                if sleep == 0:
                    if health == 0:
                        db.session.delete(user)
                        db.session.commit()
                        return redirect('pickapet.html')
                    # delete the user if the pet has 0 health via sleep

        while fun > 0:
            fun -= 2
            if fun == 0:
                db.session.delete(user)
                db.session.commit()
                return redirect('pickapet.html')
            # delete the user if the pet has 0 fun

    return render_template("yourPet.html", newuser=newuser, day=current_day, year=current_year, data=data, month=current_month, time=current_time)

@app.route('/adminView')
def adminView():
    players = player_stats.query.all()
    return render_template('adminView.html', players=players, get_localzone=get_localzone)

@app.route('/adminView/deleteButton', methods=['POST'])
def admin_Player_DeleteButton():
    try:
        playerID = request.form.get('playerID', '').strip()
        
        player_to_delete = player_stats.query.filter_by(id=playerID).first()
        
        if not player_to_delete:
            error = f"No player found with the specific ID found"
            players = player_stats.query.all()
            return render_template('adminView.html', players=players, error=error)
        
        db.session.delete(player_to_delete)
        
        db.session.commit()
        
        return redirect(url_for('adminView'))
    
    except Exception as e:
        error = f"Error deleting profile: {str(e)}"
        players = player_stats.query.all()
        return render_template('adminView.html', players=players, error=error)