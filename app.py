from flask import Flask, render_template, request, session, redirect, url_for
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from tzlocal import get_localzone

app = Flask(__name__)

app.secret_key = 'top-secret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mycustomflaskapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class player_stats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    namedpet = db.Column(db.String(100), nullable=True)
    pickedpet = db.Column(db.String(50), nullable=True)
    datecreated = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    #store hunger, fun, sleep, and health values into here if the person closes the app
    #basically have a save data sort of kind of system i dont know anymore im tired
    
with app.app_context():
    db.create_all()
    
@app.route('/', methods=['GET','POST'])
def pickapet():
    
    pickedpet = None
    namedpet = None
    
    if 'visited' in session:
        return redirect('/yourPet')
    else:
        if request.method == 'POST':
            pickedpet = request.form.get('pickedpet', '').strip()
            namedpet = request.form.get('namedpet', '').strip()
            
            if pickedpet == 'Dog':
                new_player = player_stats(
                    namedpet=namedpet,
                    pickedpet=pickedpet,
                )
                db.session.add(new_player)
                db.session.commit()
            if pickedpet == 'Cat':
                new_player = player_stats(
                    namedpet=namedpet,
                    pickedpet=pickedpet
                )
                db.session.add(new_player)
                db.session.commit()
    return render_template("pickapet.html", pickedpet=pickedpet, namedpet=namedpet, player_stats=player_stats)

@app.route('/yourPet')
def yourPet():
    now = datetime.now()
    current_year = now.year
    current_month = now.strftime("%B")
    current_day = now.day
    current_time = now.strftime("%I:%M:%S %p")
    
    data = player_stats.query.all()
    
    if 'Dog' and 'Cat' != player_stats:
        return redirect(url_for('pickapet'))
    
    if 'visited' not in session:
        session['visited'] = True
        newuser = (f"To take care of your pet, you must complete your tasks. Every time you complete a task, you get currency to buy your pet the things it needs to survive.")
    
    if 'cat' in data:
        hunger = 100
        sleep = 100
        health = 100
        fun = 100
        
        user = player_stats.query.get(id)
        
        while hunger > 0:
            hunger -= 1
            if hunger < 50:
                health -= 2
                if hunger == 0:
                    if health == 0:
                        db.session.delete(user)
                        db.session.commit()
                        return redirect('pickapet.html')

        while sleep > 0:
            sleep -= 2
            if sleep < 50:
                health -= 2
                if sleep == 0:
                    if health == 0:
                        db.session.delete(user)
                        db.session.commit()
                        return redirect('pickapet.html')

        while fun > 0:
            fun -= 2
            if fun == 0:
                db.session.delete(user)
                db.session.commit()
                return redirect('pickapet.html')

    return render_template("yourPet.html", newuser=newuser, day=current_day, year=current_year, data=data, month=current_month, time=current_time, hunger=hunger)

@app.route('/adminView')
def adminView():
    players = player_stats.query.all()
    return render_template('adminView.html', players=players, get_localzone=get_localzone)

@app.route('/adminView/delete_first')
def admin_Player_deleteFirst():
    try:
        all_players = player_stats.query.order_by(player_stats.id).all()
        first_entry = player_stats.query.first()
        
        if first_entry:
            db.session.delete(first_entry)
            db.session.commit()
            return redirect(url_for('adminView'))
        
        elif len(all_players) < 1:
            error = "You have no Players to delete."
            players = player_stats.query.all()
            return redirect(url_for('adminView'))
    
    except Exception as e:
        db.session.rollback()
        error = "An error occured whilst deleting. Try again."
        return redirect(url_for('adminView'))
    return render_template('adminView.html', players=players, error=error)

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