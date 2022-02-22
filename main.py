from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_ckeditor import CKEditorField

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm
from flask_gravatar import Gravatar
from wtforms import StringField,SubmitField,PasswordField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
login_manager=LoginManager()
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


login_manager.init_app(app)
##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
##CONFIGURE TABLES

class CommentForm(FlaskForm):
    body=CKEditorField("Comment",validators=[DataRequired()])
    submit=SubmitField("submit")




class Userss(db.Model,UserMixin):
    __tablename__ = "userss"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    posts = relationship("BlogPost",back_populates="author")
    name2 = relationship("Comment", back_populates="author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    author = relationship("Userss", back_populates="posts")
    author_id=db.Column(db.Integer,ForeignKey('userss.id'))
    children = relationship("Comment", back_populates="post")

db.create_all()
db.session.commit()


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    comment=db.Column(db.String(200),nullable=False)
    author_id=db.Column(db.Integer,ForeignKey("userss.id"))
    author = relationship("Userss", back_populates="name2")
    post_id = db.Column(db.Integer, ForeignKey('blog_posts.id'))
    post = relationship("BlogPost", back_populates="children")
db.create_all()
db.session.commit()
#
# author = db.Column(db.String(250), nullable=False)
# author_id = db.Column(db.Integer, ForeignKey('userss.id'))


class RegisterForm(FlaskForm):
    name=StringField("Name",validators=[DataRequired()])
    email=StringField("Email",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Submit")

class LoginForm(FlaskForm):
    email=StringField("Email",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Submit")



@login_manager.user_loader
def load_user(id):
    return Userss.query.get(int(id))

def admin_only(f):
    def decorated_function(*args, **kwargs):
        if current_user.id==3:
            return True
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    user = Userss.query.all()
    le=len(posts)
    au=[]
    for i in posts:
        auu=i.author_id
        u=Userss.query.filter_by(id=auu).first()
        au.append(u.name)
    if current_user.is_authenticated:
        ii=current_user.id
        print(ii)
        return render_template("index.html", post=posts,id=ii,a=au,l=le)
    else:
        return render_template("index.html", post=posts,id=0,l=le,a=au)

@app.route('/register',methods=["GET","POST"])
def register():
    form_r=RegisterForm()
    form_l=LoginForm()
    if form_r.validate_on_submit():
        n=form_r.name.data
        e=form_r.email.data
        p=form_r.password.data
        all_users=db.session.query(Userss).all()
        emails=[]
        for i in all_users:
            emails.append(i.email)
        if e in emails:
            flash("This emails is already registered.Log in instead !")
            return redirect(url_for("login"))
        else:
            i=len(all_users)+3
            new_user=Userss(id=i,email=e,name=n,password=p)
            db.session.add(new_user)
            db.session.commit()
            userr=Userss.query.filter_by(id=i).first()
            login_user(user=userr,remember=True)
            return redirect(url_for("get_all_posts"))
    else:
        return render_template("register.html",form=form_r)


@app.route('/login',methods=["GET","POST"])
def login():
    form_l=LoginForm()
    form_r=RegisterForm()
    if form_l.validate_on_submit():
        e=form_l.email.data
        p=form_l.password.data
        all_users = db.session.query(Userss).all()
        emails=[]
        ids=[]
        passwords=[]
        for i in all_users:
            emails.append(i.email)
            ids.append(i.id)
            passwords.append(i.password)
        if e in emails:
            ind=emails.index(e)
            pp=passwords[ind]
            ii=ids[ind]
            if p==pp:
                userr = Userss.query.filter_by(id=ii).first()
                login_user(user=userr, remember=True)
                print(current_user.is_authenticated)
                return redirect(url_for("get_all_posts"))
            else:
                flash("Wrong Password.Try again")
                return render_template("login.html",form=form_l)
        else:
            flash("This email is not registered with us.Register instead !")
            return redirect(url_for("register"))

    else:
        return render_template("login.html",form=form_l)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>",methods=["GET","POST"])
def show_post(post_id):
    form_c=CommentForm()
    requested_post = BlogPost.query.filter_by(id=post_id).first()
    iii=requested_post.author_id
    print(iii)
    au=Userss.query.filter_by(id=iii).first()
    if form_c.validate_on_submit():
        if current_user.is_authenticated:
            all_comments = db.session.query(Comment).all()
            l=len(all_comments)

            new_comment=Comment(id=l+1,comment=form_c.body.data,author_id=au.id,post_id=requested_post.id)

            db.session.add(new_comment)
            db.session.commit()
            ii = current_user.id
            all_comments = db.session.query(Comment).all()
            l=len(all_comments)

            all_users = db.session.query(Userss).all()
            return render_template("post.html",all_us=all_users,lc=l, post=requested_post, id=ii, a=au, form=form_c,c=all_comments,p_id=requested_post.id)
        else:
            print("YYYY")
            return redirect(url_for('login'))
    if current_user.is_authenticated:
        ii = current_user.id
        all_comments = db.session.query(Comment).all()
        l = len(all_comments)
        print("Yes", ii)
        all_users = db.session.query(Userss).all()
        return render_template("post.html",all_us=all_users,lc=l, post=requested_post, id=ii, a=au, form=form_c,c=all_comments,p_id=requested_post.id)

    all_comments = db.session.query(Comment).all()
    l = len(all_comments)
    ii=0
    all_users = db.session.query(Userss).all()
    return render_template("post.html", all_us=all_users, lc=l, post=requested_post, id=ii, a=au, form=form_c,
                           c=all_comments, p_id=requested_post.id)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post",methods=["GET","POST"])
def add_new_post():
    if current_user.id==3:

        form = CreatePostForm()
        if form.validate_on_submit():
            new_post = BlogPost(
                title=form.title.data,
                subtitle=form.subtitle.data,
                body=form.body.data,
                img_url=form.img_url.data,
                author=current_user,
                date=date.today().strftime("%B %d, %Y")
            )
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for("get_all_posts"))
        else:
            return render_template("make-post.html", form=form)
    else:
        return "Unauthorized Access"

@app.route("/edit-post/<int:post_id>")
def edit_post(post_id):
    if current_user.id==3:
        post = BlogPost.query.get(post_id)
        edit_form = CreatePostForm(
            title=post.title,
            subtitle=post.subtitle,
            img_url=post.img_url,
            author=post.author,
            body=post.body
        )
        if edit_form.validate_on_submit():
            post.title = edit_form.title.data
            post.subtitle = edit_form.subtitle.data
            post.img_url = edit_form.img_url.data
            post.author = edit_form.author.data
            post.body = edit_form.body.data
            db.session.commit()
            return redirect(url_for("show_post", post_id=post.id))
        else:
            return render_template("make-post.html", form=edit_form)
    else:
        return "Unauthorized Access"

@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    print(current_user.is_authenticated)
    if current_user.id==3:
        post_to_delete = BlogPost.query.get(post_id)
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    else:
        return "Unauthorized access",403

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000,debug=True)
