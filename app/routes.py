from unicodedata import category
from app import app, db
from app.forms import AdminForm, LoginForm, RegistrationForm, EditProfileForm, EvaluationForm, ReportForm, SearchForm
from flask import render_template, flash, redirect, url_for, url_for, request, session
from werkzeug.urls import url_parse
from flask_login import current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc
from instascrape import *
 
from app.models import Business, Category, Evaluation, Influencer, Users, Admin

headers = {
  'cookie': 'sessionid=39947923929%3AEDhfuVy6QK1MrZ%3A17%3AAYdkgMtXQyf73KxlgcbPoSNvzuu8uyAOTHuRMud0Ww'
}

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

# Pass Stuff To Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    categories = Category.query
    acc = Users.query
    if form.validate_on_submit():
        post_searched = form.searched.data
        categories = categories.filter(Category.catg.like('%' + post_searched + '%'))
        categories = categories.order_by(Category.id).all()
        acc = Users.category
        return render_template('search.html', form=form, searched=post_searched, categories=categories, acc=acc)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    form = AdminForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'error')
            return redirect(url_for('admin'))
        return redirect(url_for('adminhome'))  
    return render_template('admin.html', form=form)

@app.route('/adminhome')
def adminhome():
    return render_template('adminhome.html', title='Admin')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():

        if request.form['account_type'] == 'Influencer':
            user = Influencer.query.filter_by(email=form.email.data).first()
        else:
            user = Business.query.filter_by(email=form.email.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    categories = Category.query.all()
    ctg_list = [(i.id, i.catg) for i in categories]
    form = RegistrationForm()
    form.category.choices = ctg_list
    if form.validate_on_submit():
        if request.form['account_type'] == 'Influencer':
            user = Influencer(name=form.name.data, username=form.username.data, 
            email=form.email.data, category=form.category.data)
        else:
            user = Business(name=form.name.data, username=form.username.data, 
            email=form.email.data, category=form.category.data)
            
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
  
    return render_template('register.html', title='Register', form=form, categories=categories)

@app.route('/home')
@login_required
def home():
    return render_template('home.html', title='My Home')

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = Users.query.filter_by(username=username).first_or_404()
    catid = user.category
    yes = Category.query.filter_by(id=catid).first_or_404()
    category = yes.catg
    evaluationlist  = Evaluation.query.filter_by(accEvaluated=user.id).all()
    ratings = None
    for eval in evaluationlist:
        ratings = eval.rating

    # igprof = Profile(username)
    # igprof.scrape()
    return render_template('user.html', user=user, category=category, evaluationlist=evaluationlist, ratings=ratings)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    categories = Category.query.all()
    ctg_list = [(i.id, i.catg) for i in categories]
    form = EditProfileForm()
    form.category.choices = ctg_list
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.username = form.username.data
        current_user.category = form.category.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.username.data = current_user.username
        form.category.data = current_user.category
        catid = current_user.category
        yes = Category.query.filter_by(id=catid).first_or_404()
        form.category.data = yes.catg
    return render_template('edit_profile.html', title='Edit Profile', form=form, catgs=categories)

@app.route('/Influencers')
def influencers():
    user = Influencer.query.all()
    for cat in user:
        category = cat.category
        catname = Category.query.filter_by(id=category).first()
        fcat = catname.catg
    # for un in user:
    #     username = un.username

    # igprof = Profile(username)
    # igprof.scrape()
    return render_template('viewInfluencers.html', all=user, fcat=fcat)
    
@app.route('/InfluencersAdmin')
def influencersadmin():
    user = Influencer.query.all()
    for cat in user:
        category = cat.category
        catname = Category.query.filter_by(id=category).first()
        fcat = catname.catg
    return render_template('influencerAdmin.html', all=user, fcat=fcat)

@app.route('/Brands')
def brands():
    user = Business.query.all()
    for cat in user:
        category = cat.category
        catname = Category.query.filter_by(id=category).first()
        fcat = catname.catg
    return render_template('viewBrands.html', all=user, fcat=fcat)

@app.route('/BrandsAdmin')
def brandsadmin():
    user = Business.query.all()
    for cat in user:
        category = cat.category
        catname = Category.query.filter_by(id=category).first()
        fcat = catname.catg
    return render_template('brandsAdmin.html', all=user, fcat=fcat)

@app.route('/viewUser/<userid>', methods=['GET', 'POST'])
@login_required
def viewUser(userid):
    user = Users.query.filter_by(id=userid).first_or_404()
    form = EvaluationForm()
    ratings = None
    link = None
    if form.validate_on_submit():
        ratings = request.form['rating']
        evaluations = Evaluation(comment=form.comment.data, rating=ratings, link=form.link.data, author=current_user, accEvaluated=userid, complaint=form.complaint.data)
        db.session.add(evaluations)
        db.session.commit()
        flash('Your evaluation is posted!')
        return redirect(url_for('viewUser', userid=user.id))

    catid = user.category
    yes = Category.query.filter_by(id=catid).first_or_404()
    category = yes.catg

    eval = Evaluation.query.filter_by(accEvaluated=userid).all()
    for content in eval:
        ratings = content.rating
        link = content.link
    
    return render_template('viewUser.html', user=user, form=form, eval=eval, ratings=ratings, link=link, category=category)

@app.route('/delete/<userid>')
def delete_profile(userid):
    user_to_delete = Users.query.get_or_404(userid)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")
        return render_template('adminhome.html')

    except:
        flash("Whoops! There was a problem deleting user, try again...")
        return render_template('adminhome.html')

@app.route('/reports')
def reports():
    evaluations = Evaluation.query
    return render_template('allreports.html', evaluations=evaluations)

@app.route('/delete_eval/<id>')
def delete_eval(id):
    eval_to_delete = Evaluation.query.get_or_404(id)
    try:
        db.session.delete(eval_to_delete)
        db.session.commit()
        flash("Evaluation Deleted Successfully!")
        return render_template('adminhome.html')

    except:
        flash("Whoops! There was a problem deleting user, try again...")
        return render_template('adminhome.html')

@app.route('/evaluation/<id>', methods=['GET', 'POST'])
def evaluation(id):
    eval = Evaluation.query.filter_by(id=id).first_or_404()
    form = ReportForm()
    if form.validate_on_submit():
        eval.complaint = form.complaint.data
        db.session.commit()
        flash('Your report have been posted!')
        return redirect(url_for('evaluation', id=id))
    elif request.method == 'GET':
        form.complaint.data = eval.complaint
    return render_template('evaluation.html', form=form, eval=eval)
