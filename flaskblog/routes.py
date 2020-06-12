import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, QuestionpaperForm, WritingpaperFrom
from flaskblog.models import User, Post, Questionpaper, Writingpaper
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(firstname=form.firstname.data, lastname=form.lastname.data, username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your Account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Pleasse check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)
    output_size = (75, 75)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your Account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been Created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been Updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!!', 'success')
    return redirect(url_for('home'))


@app.route("/writing")
def writing():
    writingpapers = Writingpaper.query.all()
    return render_template('writing.html', writingpapers=writingpapers)


@app.route("/writing/new", methods=['GET', 'POST'])
@login_required
def new_writingpaper():
    form = WritingpaperFrom()
    if form.validate_on_submit():
        writingpaper = Writingpaper(title=form.title.data, task01=form.task01.data, task01_img=form.task01_img.data,
                                    task02=form.task02.data, task02_img=form.task02_img.data, wcreator=current_user)
        db.session.add(writingpaper)
        db.session.commit()
        flash('Your Writing Paper has been Created!', 'success')
        return redirect(url_for('writing'))
    return render_template('create_writing.html', title='Writing Paper', form=form, legend='Writing Paper')


@app.route("/writing/<int:writing_id>")
def show_writing(writing_id):
    writingpaper = Writingpaper.query.get_or_404(writing_id)
    return render_template('writing_paper.html', title=writingpaper.title, writingpaper=writingpaper)


@app.route("/speaking")
def speaking():
    return render_template('speaking.html')


@app.route("/listening")
def listening():
    questions = Questionpaper.query.filter(
        Questionpaper.questiontype.endswith('listening')).all()
    return render_template('listening.html', questions=questions)


@app.route("/reading")
def reading():
    questions = Questionpaper.query.filter(
        Questionpaper.questiontype.endswith('reading')).all()
    return render_template('reading.html', questions=questions)


@app.route("/questionpaper/new", methods=['GET', 'POST'])
@login_required
def new_question():
    form = QuestionpaperForm()
    if form.validate_on_submit():
        questionpaper = Questionpaper(title=form.title.data, questions=form.question.data, duration=form.duration.data,
                                      questiontype=form.questionpapertype.data, creator=current_user)
        db.session.add(questionpaper)
        db.session.commit()
        flash('Your Question Paper has been Created!', 'success')
        return redirect(url_for('writing'))
    return render_template('create_questionpaper.html', form=form, legend='Question New Paper')