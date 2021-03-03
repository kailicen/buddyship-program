from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Goal, Buddy, Progress
from . import db
from sqlalchemy.sql import func
from datetime import date
from dateutil.relativedelta import relativedelta


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if User.query.filter_by(current_buddy=None).first():
        return redirect(url_for('views.set_up'))
    else:
        if request.method == 'POST':
            # Check if both buddyship participates have set their buddies and goals before they make a progress record
            buddy_account = User.query.filter_by(first_name=current_user.current_buddy).first()
            if buddy_account:
                if buddy_account.current_buddy == current_user.first_name:
                    buddy_role = request.form.get('roleSelect')
                    buddy_score = request.form.get('scoreSelect')
                    buddy_comment = request.form.get('comment')

                    buddy_goal = buddy_account.current_goal.split(" - ")[0]
                    user_buddy = Buddy.query.filter_by(buddy_name=current_user.current_buddy, user_id=current_user.id).first()

                    if buddy_role == None:
                        flash('A role must be selected.', category='error')
                    elif buddy_score == None:
                        flash('A score must be selected.', category='error')
                    else:
                        new_progress = Progress(buddy_role=buddy_role, buddy_score=buddy_score, buddy_comment=buddy_comment,
                        buddy_goal=buddy_goal, user_id=current_user.id, buddy_id=user_buddy.id)
                        db.session.add(new_progress)
                        db.session.commit()
                        flash('Progress added!', category='success')
                        return redirect(url_for('views.home'))
                else:
                    flash('Your buddy has changed his/her status. You can find another buddy to partner with.', category='error')
            else:
                flash('Your buddy hasn\'t set up his/her account yet. Please wait.', category='error' )

        return render_template("home.html", user=current_user, 
        roleOptions=["Prepared speech", "Tabletopic speech", "Toastmaster", "Word of the day/Grammarian", "Toast of the day", "Table topic master",
        "Table topic evaluator", "Prepared speech evaluator", "Hark and fine", "Ah counter", "General evaluator"], 
        buddy_account = User.query.filter_by(first_name=current_user.current_buddy).first())


@views.route('/me', methods=['GET'])
@login_required
def me():
    if User.query.filter_by(current_buddy=None).first():
        return redirect(url_for('views.set_up'))
    else:
        buddies = Buddy.query.filter_by(buddy_name=current_user.first_name).all()
        id_lst = []
        for buddy in buddies:
            id_lst.append(buddy.user_id)

        return render_template("me.html", user=current_user,
        buddy_accounts = User.query.filter(User.id.in_(id_lst)).all(), 
        current_time = date.today())


@views.route('/your-buddy', methods=['GET'])
@login_required
def your_buddy():
    if User.query.filter_by(current_buddy=None).first():
        return redirect(url_for('views.set_up'))
    else:
        return render_template("your_buddy.html", user=current_user)


@views.route('/tm-fam', methods=['GET'])
@login_required
def tm_fam():
    if User.query.filter_by(current_buddy=None).first():
        return redirect(url_for('views.set_up'))
    else:
        all_users = User.query.with_entities(User.first_name, User.current_goal, User.current_buddy).all()
        buddyships_double = []
        goals_double = []
        for user1 in all_users:
            for user2 in all_users:
                if user1.first_name == user2.current_buddy:
                    if user2.first_name == user1.current_buddy:
                        buddyships_double.append(user1.first_name + " & " + user2.first_name)
                        goals_double.append(user1.current_goal + " & " + user2.current_goal)
        buddy_check = []
        buddyships = []
        for buddyship in buddyships_double:
            buddy1 = buddyship.split(" & ")[0]
            buddy2 = buddyship.split(" & ")[1]
            if buddy1 not in buddy_check:
                buddy_check.append(buddy1)
                buddy_check.append(buddy2)
                buddyships.append(buddyship)
        goal_check = []
        goals = []
        for goal in goals_double:
            goal1 = goal.split(" & ")[0]
            goal2 = goal.split(" & ")[1]
            if goal1 not in goal_check:
                goal_check.append(goal1)
                goal_check.append(goal2)
                goals.append(goal)
        count = len(buddyships)
        return render_template("tm_fam.html", user=current_user, buddyships=buddyships, goals=goals, count=count)


@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if User.query.filter_by(current_buddy=None).first():
        return redirect(url_for('views.set_up'))
    else:
        if request.method == 'POST':
            if request.form["btn"] == "Buddy Updated":
                buddy_name = request.form.get('buddyName').lower().capitalize()

                if len(buddy_name) < 1:
                    flash('Buddy\'s name must be greater than 1 character.', category='error')
                else:
                    user = current_user

                    former_buddies = Buddy.query.filter_by(user_id=user.id).all()
                    former_buddy_count = Buddy.query.filter_by(user_id=user.id).count()

                    if buddy_name != user.current_buddy:
                        check_buddy = True
                        for former_buddy in former_buddies:
                            if buddy_name == former_buddy.buddy_name:
                                check_buddy = False
                                flash('You already had ' + name + ' as your buddy before.', category='error')
                        if check_buddy == False:
                            pass
                        else:
                            user.current_buddy = buddy_name
                            buddy_count = former_buddy_count + 1
                            last_buddy = Buddy.query.filter_by(user_id=user.id, buddy_count=former_buddy_count).first()
                            last_buddy.end_date = func.now()

                            new_buddy = Buddy(buddy_name=buddy_name, buddy_count=buddy_count, user_id=current_user.id)
                            db.session.add(new_buddy)
                            db.session.commit()
                            flash('Buddy updated!', category='success')
                    else:
                        pass
                    return redirect(url_for('views.profile'))

            elif request.form["btn"] == "Goal Updated":
                goal_direction = request.form.get('goalSelect')
                goal_reward = request.form.get('reward')
                user = current_user
                
                former_goal_count = Goal.query.filter_by(user_id=user.id).count()

                if goal_direction == None:
                    last_goal = Goal.query.filter_by(user_id=user.id, goal_count=former_goal_count).first()
                    if goal_reward != user.current_reward:
                        user.current_reward = goal_reward
                        last_goal.reward = goal_reward
                        db.session.commit()
                        flash('Reward updated!', category='success')
                    else:
                        pass
                else:
                    goal_elaborate = request.form.get('goalElaborate')
                    goal_statement = goal_direction + ' - ' + goal_elaborate
                    check_goal = True
                    if len(goal_elaborate) < 3:
                        flash('Please elaborate more about your goal.', category='error')
                    elif len(goal_reward) < 3:
                        flash('Your reward is too short.', category='error')
                    else:
                        former_goals = Goal.query.filter_by(user_id=user.id).all()

                        for former_goal in former_goals:
                            if goal_direction == former_goal.goal_direction:
                                check_goal = False
                                flash('You already had ' + goal + ' as your goal before.', category='error')
                        if check_goal == False:
                            pass
                        else:
                            user.current_goal = goal_statement
                            goal_count = former_goal_count + 1
                            last_goal = Goal.query.filter_by(user_id=user.id, goal_count=former_goal_count).first()
                            last_goal.end_date = func.now()
                            
                            end_date = date.today() + relativedelta(months=+6)
                            user.current_reward = goal_reward
                            new_goal = Goal(goal_direction=goal_direction, goal_statement=goal_statement, goal_count=goal_count, 
                            goal_reward=goal_reward, end_date=end_date, user_id=current_user.id)
                            db.session.add(new_goal)
                            db.session.commit()
                            flash('New goal and reward added!', category='success')

                    return redirect(url_for('views.profile'))
            else:
                return redirect(url_for('views.home'))

        return render_template("profile.html", user=current_user,
        goalOptions=["Filler words", "Gestures", "Eye contact", "Vocal Variety",
        "Clarity", "Audience Awareness", "Others"])



@views.route('/set-up', methods=['GET', 'POST'])
@login_required
def set_up():
    if User.query.filter_by(current_buddy=None).first():
        if request.method == 'POST':
            buddy_name = request.form.get('buddyName').lower().capitalize()
            goal_direction = request.form.get('goalSelect')
            goal_elaborate = request.form.get('goalElaborate')
            goal_reward = request.form.get('reward')



            if len(buddy_name) < 1:
                flash('Buddy\'s name must be greater than 1 character.', category='error')
            elif goal_direction == None:
                flash('A goal must be selected.', category='error')
            elif len(goal_elaborate) < 3:
                flash('Please elaborate more about your goal.', category='error')
            elif len(goal_reward) < 3:
                flash('Reward is too short.', category='error')
            else:
                goal_statement = goal_direction + ' - ' + goal_elaborate
                user = current_user
                user.current_buddy = buddy_name
                user.current_goal = goal_statement
                user.current_reward = goal_reward
                
                end_date = date.today() + relativedelta(months=+6)

                new_buddy = Buddy(buddy_name=buddy_name, user_id=current_user.id)
                new_goal = Goal(goal_direction=goal_direction, goal_statement=goal_statement, goal_reward=goal_reward, 
                end_date=end_date, user_id=current_user.id)
                db.session.add(new_buddy)
                db.session.add(new_goal)
                db.session.commit()
                flash('Things are all set!', category='success')
                return redirect(url_for('views.home'))

        return render_template("set_up.html", user=current_user,
        goalOptions=["Filler words", "Gestures", "Eye contact", "Vocal Variety",
        "Clarity", "Audience Awareness", "Others"])
    else:
        return redirect(url_for('views.home'))
