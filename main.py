from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lc101@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'dkEk13^%4@fR14^&1@@8kdFGa1'
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Blog ID:%d>'.format(self.id)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User ID:%d>.format(self.id)'


@app.route('/blog')
def display_blogs():

    if request.args:
        # request had query parameters, so display individual entry
        id = int(request.args.get('id'))
        blog = Blog.query.get(id)
        return render_template(
            'blog_entry.html',
            title="Blog Entry",
            blog=blog)
    else:
        # request had no query parameters, so display all the blog entries
        blogs = Blog.query.order_by("id desc").all()
        return render_template(
            'blog.html',
            title="Main Blog Page",
            blogs=blogs)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                session['username'] = username
                return redirect('/blog')
            else:
                return render_template('login.html',
                    title="Login Page with password error",
                    username = username,
                    password_error = "Password is incorrect")
        else:
                return render_template('login.html', title="Login Page with username error",
                username_error = "This username does not exist")


    return render_template('login.html', title="Login Page")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify_password']

        # TODO - Finish signup page processing
        username_error = ""
        password_error = ""
        verify_password_error = ""
        if len(username) < 3:
            username_error = "That's not a valid username"
        else:
            num_existing_users = User.query.filter_by(username=username).count()
            if num_existing_users > 0:
                username_error = "A user with that username already exists"
        if len(password) < 3:
            password_error = "That's not a valid password"
        if len(verify_password) == 0:
            verify_password_error = "Passwords don't match"
        elif password != verify_password:
            verify_password_error = "Passwords don't match"
        
        if username_error or password_error or verify_password_error:
            return render_template('signup.html',
                title = "Signup Page with errors",
                username_error = username_error,
                password_error = password_error,
                verify_password_error = verify_password_error)
        else:
            # No errors so save new user
            newuser = User(username, password)
            db.session.add(newuser)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html', title="Signup Page")


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        error_free = True
        blog_title = request.form['blog_title']
        if len(blog_title) == 0:
            flash('Please enter a title', 'title_error')
            error_free = False
        body = request.form['body']
        if len(body) == 0:
            flash('Please enter a body', 'body_error')
            error_free = False
        if error_free:
            # TODO - get the real owner for the blog entry
            owner = User.query.first()
            new_blog = Blog(blog_title, body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_blog.id))
        else:
            return render_template('newpost.html',
                title="Add a New Post",
                blog_title = blog_title,
                body = body)

    return render_template('newpost.html', title="Add a New Post")


if __name__ == '__main__':
    app.run()