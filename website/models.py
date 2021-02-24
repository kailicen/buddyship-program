from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(150))
    score = db.Column(db.String(1))
    comment = db.Column(db.String(1500))
    date = db.Column(db.DateTime, default=func.now())
    goal_count = db.Column(db.Integer, db.ForeignKey('goal.goal_count'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String(150))
    goal_count = db.Column(db.Integer, default=1)
    reward = db.Column(db.String(150))
    start_date = db.Column(db.DateTime, default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    progresses = db.relationship('Progress')

class Buddy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    buddy_count = db.Column(db.Integer, default=1, unique=True)
    start_date = db.Column(db.DateTime, default=func.now())
    end_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    current_buddy = db.Column(db.String(150))
    current_goal = db.Column(db.String(150))
    current_reward = db.Column(db.String(150))
    buddies = db.relationship('Buddy')
    goals = db.relationship('Goal')
    progresses = db.relationship('Progress')
