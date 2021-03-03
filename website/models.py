from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buddy_role = db.Column(db.String(150))
    buddy_score = db.Column(db.String(150))
    buddy_comment = db.Column(db.String(1500))
    date = db.Column(db.DateTime, default=func.now())
    buddy_goal = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    buddy_id = db.Column(db.Integer, db.ForeignKey('buddy.id'))

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal_direction = db.Column(db.String(150))
    goal_statement = db.Column(db.String(150))
    goal_count = db.Column(db.Integer, default=1)
    goal_reward = db.Column(db.String(150))
    start_date = db.Column(db.DateTime, default=func.now())
    end_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Buddy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buddy_name = db.Column(db.String(150))
    buddy_count = db.Column(db.Integer, default=1)
    start_date = db.Column(db.DateTime, default=func.now())
    end_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    buddy_progresses = db.relationship('Progress')

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
    record_progresses = db.relationship('Progress')
