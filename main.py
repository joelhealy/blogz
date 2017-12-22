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