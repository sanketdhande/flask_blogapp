from flask import render_template, url_for, flash, redirect, request, Blueprint,abort
from flask_login import login_user, current_user, logout_user, login_required
from blogapp import db,app
from werkzeug.security import generate_password_hash,check_password_hash
from blogapp.models import User, BlogPost
from blogapp.users.forms import RegistrationForm, LoginForm, UpdateUserForm
from blogapp.users.picture_handler import add_profile_pic
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask_user import UserMixin
users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering! Now you can login!')
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        if user.check_password(form.password.data) and user is not None:
            #Log in the user

            login_user(user)
            flash('Logged in successfully.')


            # flask saves that URL as 'next'.
            next = request.args.get('next')
            if next == None or not next[0]=='/':
                next = url_for('core.index')

            return redirect(next)
    return render_template('login.html', form=form)




@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('core.index'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():

    form = UpdateUserForm()

    if form.validate_on_submit():
        print(form)
        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data,username)
            current_user.profile_image = pic

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('User Account Updated')
        return redirect(url_for('users.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    profile_image = url_for('static', filename='profile_pics/' + current_user.profile_image)
    return render_template('account.html', profile_image=profile_image, form=form)


@users.route("/<username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    blog_posts = BlogPost.query.filter_by(author=user).order_by(BlogPost.date.desc()).paginate(page=page, per_page=5)
    return render_template('user_blog_posts.html', blog_posts=blog_posts, user=user)

admin = Admin(app,name = 'control panel')

#@users.route("/create_admin", methods=['GET', 'POST'])
def create_admin():
    if request.method == 'POST':
        adminuser = User(email = request.form['email'],username=request.form['username'],password=request.form['password'],is_admin=True)
        db.session.add(adminuser)
        db.session.commit()
        return "create admin"
    return render_template('admin_signup.html')

class Controller(ModelView):
    def is_accessible(self):
        if current_user.is_admin == True:
            return current_user.is_authenticated
        else:
            return abort('not found')

    def not_auth(self):
        return 'not found'


admin.add_view(Controller(User,db.session))
admin.add_view(Controller(BlogPost,db.session))
