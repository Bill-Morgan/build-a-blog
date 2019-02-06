from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blogpassword@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    post_txt = db.Column(db.String(1000))
    post_datetime = db.Column(db.TIMESTAMP,default=datetime.utcnow)
    def __init__(self, title, post_txt):
        self.title = title
        self.post_txt = post_txt
        

def isvalidpost(title,newpost):
    title_error = ''
    blog_error = ''
    if not title:
        title_error = 'Please fill in the title'
    if not newpost:
        blog_error = 'Please fill in the body'
    return (title_error, blog_error)

@app.route('/edit', methods=['POST', 'GET'])        
def editpost():
    if request.method == 'POST':
        id = int(request.form['id'])
        title = request.form['title']
        post_txt = request.form['newpost']
        post_datetime = request.form['datetime']
        title_error, blog_error = isvalidpost(title,post_txt)
        if (title_error or blog_error):
            return render_template('editpost.html', page_title='Edit a Blog Entry', title_error=title_error, blog_error=blog_error, title=title, newpost=post_txt, id=id)
        new_blog_post = BlogPost(title, post_txt)
        new_blog_post.post_datetime = post_datetime
        db.session.add(new_blog_post)
        db.session.commit()
        del_old_post = BlogPost.query.filter_by(id=id).first()
        db.session.delete(del_old_post)
        db.session.commit()
        return redirect('/blog?id={}'.format(new_blog_post.id))
    id = request.args.get('id')
    try:
        id = int(id)
    except:
        return redirect('/')
    blog_post = BlogPost.query.filter_by(id=id).first()
    if blog_post:
        title = blog_post.title
        post_txt = blog_post.post_txt
        id = blog_post.id
        datetime = blog_post.post_datetime
        return render_template('editpost.html', page_title='Edit a Blog Entry', title=title, newpost=post_txt, id=id, datetime=datetime)
    return redirect('/')

@app.route('/deletepost', methods=['POST', 'GET'])
def delpost():
    if request.method == 'POST':
        if request.form['submit'] != 'Delete':
            return redirect('/')
        id = int(request.form['id'])
        del_post = BlogPost.query.filter_by(id=id).first()
        db.session.delete(del_post)
        db.session.commit()
        return redirect('/')
    id = int(request.args.get('id'))
    del_post = BlogPost.query.filter_by(id=id).first()
    return render_template('deletepost.html', page_title=del_post.title, post=del_post)

@app.route('/newpost', methods=['POST', 'GET'])        
def newpost():
    error = request.args.get("error")
    if request.method == 'POST':
        title = request.form['title']
        newpost = request.form['newpost']
        title_error, blog_error = isvalidpost(title,newpost)
        if (title_error or blog_error):
            return render_template('newpost.html', page_title='Add a Blog Entry', title_error=title_error, blog_error=blog_error, title=title, newpost=newpost)
        new_blog_post = BlogPost(title, newpost)
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect('/blog?id={}'.format(new_blog_post.id))
    return render_template('newpost.html', page_title='Add a Blog Entry', error=error)

@app.route("/blog")
def blog():
    id = request.args.get("id")
    if id:
        the_blogs = BlogPost.query.filter_by(id=id).first()
        if the_blogs:
            title=the_blogs.title
            return render_template('1blog.html', page_title=title, post=the_blogs)
        return redirect('/') # there was no db return with the requested id.
    the_blogs = BlogPost.query.order_by('post_datetime DESC').all()
    return render_template('blog.html', page_title='Build a Blog', posts=the_blogs)

@app.route("/")
def index():
    return redirect('/blog')

if __name__ == "__main__":
    app.run()
