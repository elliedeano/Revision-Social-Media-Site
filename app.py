
import sqlalchemy as db
from flask import url_for 
from flask import Flask, redirect,  request, flash
from sqlalchemy.sql import func
from sqlalchemy import desc
from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin, LoginManager,login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired
from wtforms import StringField, PasswordField, SubmitField
from flask_bcrypt import Bcrypt
from wtforms.widgets import TextArea
from flask import Flask, request, render_template, url_for 

app = Flask(__name__, template_folder='template')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/elliedeaner/RevisionSocialMediaSite/revision.db'
app.config['SECRET_KEY'] = 'key'

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'
@login_manager.user_loader
def load_the_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def main():
    posts = Post.query.all()

    return render_template('main.html', user = current_user, posts = posts)

@app.route('/entry', methods=['GET', 'POST'])
#loginrequired
def entry():
    posts = Post.query.order_by(desc(Post.date))
    return render_template('entry.html', posts=posts)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('logging_in'))


@app.route('/profile', methods=['GET', 'POST'])
def profile(): 
    return render_template("profile.html")



@app.route('/file', methods=['GET', 'POST'])
def file(): 
    file = request.files
    return render_template("file.html")


@app.route('/logging_in', methods=['GET', 'POST'])
def logging_in():
    Login_form = Logging_in()
    if Login_form.validate():
        current_user = User.query.filter_by(username=Login_form.username.data, email=Login_form.email.data, password = Login_form.password.data).first()
        if current_user:
            login_user(current_user)
            return redirect(url_for('entry'))
    return render_template('logging_in.html', form=Login_form)
    
@app.route('/registering', methods=['GET', 'POST'])
def registering():
    Register_form = Registering()

    if Register_form.validate():
        create_user = User(username=Register_form.username.data, password=Register_form.password.data, email=Register_form.email.data)
        db.session.add(create_user)
        db.session.commit()
        db.session.close()
        return redirect(url_for('logging_in'))

    return render_template('registering.html', form=Register_form)


@app.route('/posts')
def posts():
	# Grab all the posts from the database
	posts = Post.query.order_by(Post.date)
	return render_template("posts.html", posts=posts)


@app.route('/posts/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template("post.html", post=post)



@app.route('/create-post', methods=['GET', 'POST'])
def create_post():
    
    form = PostForm()
    if form.validate_on_submit():
        post = Post(text=form.text.data, author=form.author.data, title=form.title.data, tag=form.tag.data)
        db.session.add(post)
        db.session.commit()
        flash("Blog post submitted successfully ")
    return render_template('create_post.html', form=form)

class TagForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    search = SubmitField("Search")


@app.route('/search', methods=['POST', 'GET'])
def tagged_posts(): 
    form = TagForm()
    posts = Post.query
    if form.validate_on_submit():
        post = Tag(searched = form.search.data, search = form.search.data)
        post.searched = form.searched.data
		# Query the Database
        posts = posts.filter(Post.tag.like('%' + post.searched + '%'))
        posts = posts.order_by(Post.date).all()
        return render_template("tags.html", form=form, searched = post.searched, posts = posts)
        
@app.context_processor
def base():
    form = TagForm()
    return dict(form=form)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    searched = db.Column(db.Text,nullable=False)
    search = db.Column(db.Text,nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True )
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    posts = db.relationship('Post', backref='poster')
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    date = db.Column(db.DateTime(timezone=True), default = func.now())
    text=db.Column(db.Text,nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    tag = db.Column(db.Text,nullable=False)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text, unique=True, nullable=False)
    
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    text = StringField("Text", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    tag = StringField("Tags", validators=[DataRequired()])
    submit = SubmitField("Post")
      
class Registering(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[ InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    email =  StringField(validators=[ InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "email"})
    submit = SubmitField("Register")
    def check_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username already exists ")
   
class Logging_in(FlaskForm):
    
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20,)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length( 
        min=4, max=20,)], render_kw={"placeholder": "Password"})
    email =  StringField(validators=[ InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "email"})
    submit = SubmitField("Login")


if __name__ == '__main__':
    app.run(debug=True)


