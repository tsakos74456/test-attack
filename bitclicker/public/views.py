# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from bitclicker.extensions import login_manager
from bitclicker.public.forms import LoginForm
from bitclicker.user.forms import RegisterForm
from bitclicker.user.models import User
from bitclicker.utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder='../static')


def get_flag():
    return open("./key").read().strip()


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    """Home page."""
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash('You are logged in.', 'success')
            redirect_url = request.args.get('next') or url_for('public.mine')
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template('public/home.html', form=form)


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form, meta={'csrf': False})
    if form.validate_on_submit():
        u = User.create(
            username=form.username.data, password=form.password.data, active=True,
            btc=0.0, usd=0.0)

        if not current_user.is_authenticated:
            login_user(u)

        if form.password.data == get_flag():
            current_user.update(usd=400.0)
        else:
            current_user.update(usd=100.0)

        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)


@blueprint.route('/mine/')
@login_required
def mine():
    return render_template('mine.html')
