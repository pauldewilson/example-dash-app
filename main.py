import os
from flask import Flask, render_template, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from forms.login_form import LoginForm
from datasource.datasource import DataController
from dashapp.dashapp import initiate_dash_app, protect_views

# instantiate application and dash app, sqlalchemy db, login manager, and config params
app = Flask(__name__, instance_relative_config=False)
dash = initiate_dash_app()
dash.init_app(app)
# protect views function ensures authentication from flask passes to dash
protect_views(dash, login_required)
# this secret key would never be publicly broadcast in a live environment
# better practice is to utilise environment variables
app.config['SECRET_KEY'] = 'j32hEQtYzYtHy5Egc^aTzrS6EvVipsJyggx5'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# basedir taken to place sqllite db within the project dir
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
login_manager = LoginManager()
login_manager.init_app(app)
# setting login view to index since /dashboard will be a protected route
login_manager.login_view = '/'
# normally a database uri is provided but for the purposes of demo the db will be held in memory
db = SQLAlchemy(app)


# User class as required by flask login
class User(UserMixin, db.Model):
    """
    User class required for flask login.
    Assuming email == username.
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the username address to satisfy Flask-Login's requirements."""
        return self.username

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


# test users - normally passwords would be hashed using werkzeug
testUserOne = User(username='bob@example.com', password='bobpass')
testUserTwo = User(username='sally@example.com', password='sallypass')
# drop all /create for the purposes of demo restart
db.drop_all()
db.create_all()
db.session.add(testUserOne)
db.session.add(testUserTwo)
db.session.commit()


@login_manager.user_loader
def load_user(username):
    """
    Flask login function that loads a user to the session
    """
    return User.query.filter_by(username=username).first()


@app.route('/log_out', methods=["GET", "POST"])
@login_required
def log_out():
    """
    Logout view that removes user from the session
    """
    logout_user()
    flash('successfully logged out')
    return redirect('/')


# home / login route
@app.route("/", methods=["GET", "POST"])
def home():
    """
    Home / index route for user to log in
    """
    # login form to be passed to html through render_template
    login_form = LoginForm()
    # if form posted and validate on submit then check credentials for successful login
    if login_form.validate_on_submit():
        # grab data from from
        username = login_form.username.data
        password = login_form.password.data
        # query User class to find if user exists
        user = User.query.filter_by(username=username).first()
        # if a user is found and the password matches that on db then authenticate and log in
        # normally the password would be hashed using werkzeug but omitted for purposes of demo
        if user and user.password == password:
            # if here then user provided valid email & password and will be logged in
            user.authenticated = True
            login_user(user, remember=True)
            return redirect('dashboard')
        else:
            # user failed validation
            # errors can be more specific but for security reasons it's not recommended
            # redirect back to homepage and flash error msg
            flash("Invalid user login")
            return redirect('/')
    # initial render template on load
    return render_template('index.html', form=login_form)


@app.route('/dashboard/', methods=["GET", "POST"])
@login_required
def dashboard():
    """
    TODO: build analytics dashboard
    """
    return redirect('/dashboard')


if __name__ == '__main__':
    # set download to false to turn off data download/aggregation
    DataController(download_and_aggr_data=False)
    # use_reloader set to False to stop double initialisation when in debug mode
    app.run(debug=True, use_reloader=False)