from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Goal, Buddy, Progress
from . import db
from sqlalchemy.sql import func

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if User.query.filter_by(current_buddy=None).first():
        return redirect(url_for('views.set_up'))
    else:
        if request.method == 'POST':
            role = request.form.get('roleSelect')
            score = request.form.get('scoreSelect')
            comment = request.form.get('comment')
            goal = Goal.query.filter_by(goal=current_user.current_goal).first()

            if role == "Choose...":
                flash('A role must be selected.', category='error')
            elif score == "Choose...":
                flash('A score must be selected.', category='error')
            else:
                new_progress = Progress(role=role, score=score, comment=comment,
                goal_count=goal.goal_count, user_id=current_user.id)
                db.session.add(new_progress)
                db.session.commit()
                flash('Progress added!', category='success')
                return redirect(url_for('views.home'))

        return render_template("home.html", user=current_user,
        roleOptions=["Prepared speech", "Tabletopic", "Other roles"],
        goal = Goal.query.filter_by(goal=current_user.current_goal).first())


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if User.query.filter_by(current_buddy=None).first():
        return redirect(url_for('views.set_up'))
    else:
        if request.method == 'POST':
            if request.form["btn"] == "Save Changes":
                name = request.form.get('buddyName')
                goal = request.form.get('goalSelect')
                reward = request.form.get('reward')
                other_goal = request.form.get('otherGoal')

                if goal == "Others (Please specify in the textbox below.)":
                    goal = other_goal
                    if len(goal) < 3:
                        flash('Your goal is too short.', category='error')

                if len(name) < 1:
                    flash('Buddy\'s name must be greater than 1 character.', category='error')
                elif goal == "Choose...":
                    flash('A goal must be selected.', category='error')
                elif len(reward) < 3:
                    flash('Reward is too short.', category='error')
                else:
                    user = current_user

                    former_buddies = Buddy.query.filter_by(user_id=user.id).all()
                    if name != user.current_buddy:
                        check_buddy = True
                        for former_buddy in former_buddies:
                            if name == former_buddy.name:
                                check_buddy = False
                                flash('You already had ' + name + ' as your buddy before.', category='error')
                        if check_buddy == False:
                            pass
                        else:
                            user.current_buddy = name

                            former_buddy_count = Buddy.query.filter_by(user_id=user.id).count()
                            buddy_count = former_buddy_count + 1
                            last_buddy = Buddy.query.filter_by(user_id=user.id, buddy_count=former_buddy_count).first()
                            last_buddy.end_date = func.now()

                            new_buddy = Buddy(name=name, buddy_count=buddy_count, user_id=current_user.id)
                            db.session.add(new_buddy)
                            db.session.commit()
                            flash('Buddy updated!', category='success')
                    else:
                        pass

                    former_goals = Goal.query.filter_by(user_id=user.id).all()
                    former_goal_count = Goal.query.filter_by(user_id=user.id).count()

                    if goal != user.current_goal:
                        check = True
                        for former_goal in former_goals:
                            if goal == former_goal.goal:
                                check = False
                                flash('You already had ' + goal + ' as your goal before.', category='error')
                        if check == False:
                            pass
                        else:
                            user.current_goal = goal
                            goal_count = former_goal_count + 1
                            user.current_reward = reward
                            new_goal = Goal(goal=goal, goal_count=goal_count, reward=reward, user_id=current_user.id)
                            db.session.add(new_goal)
                            db.session.commit()
                            flash('New goal and reward added!', category='success')

                    else:
                        last_goal = Goal.query.filter_by(user_id=user.id, goal_count=former_goal_count).first()
                        if reward != user.current_reward:
                            user.current_reward = reward
                            last_goal.reward = reward
                            db.session.commit()
                            flash('Reward updated!', category='success')
                        else:
                            pass

                    return redirect(url_for('views.profile'))
            else:
                return redirect(url_for('views.home'))

        return render_template("profile.html", user=current_user,
        goalOptions=["Filler words", "Gestures", "Eye contact", "Vocal Variety",
        "Clarity", "Audience Awareness", "Others (Please specify in the textbox below.)"])



@views.route('/set-up', methods=['GET', 'POST'])
@login_required
def set_up():
    if User.query.filter_by(current_buddy=None).first():
        if request.method == 'POST':
            name = request.form.get('buddyName')
            goal = request.form.get('goalSelect')
            reward = request.form.get('reward')
            other_goal = request.form.get('otherGoal')

            if goal == "Others (Please specify in the textbox below.)":
                goal = other_goal
                if len(goal) < 3:
                    flash('Your goal is too short.', category='error')

            user = current_user
            user.current_buddy = name
            user.current_goal = goal
            user.current_reward = reward

            if len(name) < 1:
                flash('Buddy\'s name must be greater than 1 character.', category='error')
            elif goal == "Choose...":
                flash('A goal must be selected.', category='error')
            elif len(reward) < 3:
                flash('Reward is too short.', category='error')
            else:
                new_buddy = Buddy(name=name, user_id=current_user.id)
                new_goal = Goal(goal=goal, reward=reward, user_id=current_user.id)
                db.session.add(new_buddy)
                db.session.add(new_goal)
                db.session.commit()
                flash('Things are all set!', category='success')
                return redirect(url_for('views.home'))

        return render_template("set_up.html", user=current_user,
        goalOptions=["Filler words", "Gestures", "Eye contact", "Vocal Variety",
        "Clarity", "Audience Awareness", "Others (Please specify in the textbox below.)"])
    else:
        return redirect(url_for('views.home'))
