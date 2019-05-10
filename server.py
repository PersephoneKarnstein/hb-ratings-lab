"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import * #User, Rating, Movie, connect_to_db, db

from sqlalchemy.orm.exc import NoResultFound

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/', methods=["GET", "POST"])
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """show a list of users"""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/receive-email")
def receive_email():

    return render_template("receive-email.html")



@app.route("/check-email", methods=['POST'])
def check_email():
    email = request.form.get("email", "Error") #it will return an error if it can't find them
    session["email"] = email
    print(email)
    try:
        user_with_email = db.session.query(User).filter_by(email = email).one() 
        #at most we shoule find one person with this email
        print(user_with_email)
        testEmail = {'exists':True,
        'alert':"Welcome back!\nRedirecting to login"
        }
        return jsonify(testEmail)
    except NoResultFound:
        #this just means that we don't have that user registered yet
        testEmail = {'exists':True,
        'alert':"""It doesn't look like you've signed up yet!\n
        Click 'OK' to be redirected..."""
        }
        return jsonify(testEmail)
    except Exception:
        raise "There is more than one user registered with that email!!"



@app.route("/login")
def login():
    return render_template("login.html", )

@app.route("/sign-up")
def sign_up():
    return render_template("sign-up.html")



@app.route("/process-login", methods=["POST"])
def check_success():
    attempt_type = request.form.get("attempt-type")
    user_email = request.form.get("email")

    print(attempt_type, user_email)

    # user_email = db.session.query(User).filter_by(email = email).one() #at most we shoule find one person with this email
    

    if attempt_type == "login": #so nominally, if they get to 
        #this page, check_email() has already determined that there
        #is a person with this email in the database
        user = db.session.query(User).filter_by(email = user_email).first()
        
        #the case where there is more than one person with that email (or
        # 0 people with that email) has already been caught by check_email()
        if user.password == request.form.get("password"):
            flash('You were successfully logged in')
            return redirect("/")
        else: 
            flash("That password is incorrect.")
            return redirect("/login")


    elif attempt_type == "signup": #there is *not* a person with this
        #name already in the database
    
        #add to database
        user = User(email=user_email,
                    password=request.form.get("password"),
                    age=int(request.form.get("age")),
                    zipcode=request.form.get("zipcode"))

        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you've been signed up. I'm so excited.")
        return redirect("/")

    else:
        raise "Invalid attempt type."

    


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
