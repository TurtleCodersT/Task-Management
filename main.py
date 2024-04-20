import smtplib
from datetime import date
from typing import List
import sqlalchemy.exc
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
import forms
from flask_mail import Mail, Message
import requests
import html
import statistics
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
login_manager = LoginManager()
login_manager.init_app(app)
Bootstrap5(app)

@login_manager.user_loader
def load_user(user_id):
    #Use when database already has at least one user
    # return db.get_or_404(User, user_id)
    #If refactoring database (For example new feature) Use this line and comment out first line until one account is made
    return User.query.get(int(user_id))

class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", 'sqlite:///posts.db')
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    author = relationship('Task', back_populates='task_author')

class Task(db.Model):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    speed: Mapped[str] = mapped_column(String)
    deadline: Mapped[str] = mapped_column(String)
    task_author = relationship('User', back_populates='author')
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    is_overdue: Mapped[str] = mapped_column(String)
    time: Mapped[str] = mapped_column(String)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    all_tasks = db.session.execute(db.select(Task).order_by(Task.deadline)).scalars()
    all_tasks = list(all_tasks)
    current_date = datetime.datetime.today().date().strftime('%m/%d/%Y')
    unformatted_date = datetime.datetime.today().date()
    time = datetime.datetime.today().time().strftime('%H:%M:%S')
    time = datetime.datetime.strptime(time, "%H:%M:%S").strftime("%I:%M:%S %p")
    for task in all_tasks:
        date_to_complete = datetime.datetime.today().date().fromisoformat(task.deadline)
        if date_to_complete < unformatted_date:
            task_id = task.id
            result = db.session.execute(db.select(Task).where(Task.id == task_id)).scalar()
            result.is_overdue = True
            db.session.commit()
    return render_template('index.html', all_tasks=all_tasks, date=current_date, time=time, unformatted_date=unformatted_date)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)

        return redirect(url_for("home"))
    return render_template("register.html", form=form, current_user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', "POST"])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user == None:
            flash('Email Not Found')
        else:
            password = request.form.get('password')
            if check_password_hash(pwhash=user.password, password=password) == True:
                login_user(user)
            else:
                flash("Password Incorrect, please try again.")
                redirect(url_for('login'))
        return redirect(url_for('home'))
    return render_template("login.html", form=form)

@app.route('/add_task', methods=["GET", "POST"])
def add_task():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = forms.NewTask()
    if form.validate_on_submit():
        name = form.task_name.data
        description = form.description.data
        speed = form.speed.data
        deadline = form.deadline.data
        time = str(form.time.data)
        task = Task(task_name=name, description=description, speed=speed, deadline=deadline, user_id=current_user.id, is_overdue=False, time=time)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new_task.html', form=form)

@app.route("/delete/<input_id>", methods=['GET', "POST"])
def delete(input_id):
    row = db.session.execute(db.select(Task).order_by(Task.id)).scalars()
    for rows in row:
        if rows.id == int(input_id):
            task_name = rows.task_name
    task = db.session.execute(db.select(Task).where(Task.task_name == task_name)).scalar()
    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('home'))

@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    task_form = forms.ChangePriority()
    if task_form.validate_on_submit():
        task = db.get_or_404(Task, task_id)
        task.speed = task_form.new_priority.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("ChangePriority.html", form=task_form)



if __name__ == "__main__":
    app.run(debug=True, port=5002)