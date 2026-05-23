# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from json import dumps

import random

blueprint = Blueprint('user', __name__, url_prefix='/users', static_folder='../static')

BTC_GAIN = 0.02

def get_flag():
    return open("./key").read()

def get_energy_cost():
    old_state = random.getstate()

    random.seed(get_flag())
    cost = round(random.uniform(6.50, 6.75), 2)

    random.setstate(old_state)
    return cost

def get_stats():
    return {
        "btc": round(current_user.btc, 2),
        "usd": round(current_user.usd, 2),
        "energyCost": get_energy_cost()
    }

@blueprint.route('/currency')
@login_required
def user_stats():
    return dumps(get_stats())

@blueprint.route('/mine/<string:times>')
@login_required
def user_mine(times):
    try:
        times = int(times)
        if times <= 0:
            return dumps(get_stats())

        ENERGY_COST = get_energy_cost()

        if current_user.usd >= ENERGY_COST * times:

            new_btc = current_user.btc + BTC_GAIN * times
            new_usd = current_user.usd - ENERGY_COST * times

            current_user.update(btc=new_btc, usd=new_usd)
            current_user.save()
    finally:

        return dumps(get_stats())

@blueprint.route('/buy/<string:item>')
@login_required
def user_buy(item):

    result = "That item doesn't exist."

    if item == "Flag":
        if current_user.usd >= 300:
            result = "The flag is: %s. Sadly your purchase has attracted the wrong kind of attention. Your account has been robbed and reset by hackers!" % get_flag()
            current_user.update(btc=0.0, usd=0.0)
            current_user.save()
        else:
            result = "You can't afford it a flag right now. It's not that easy!"
    elif item == "Money ($100)":
        if current_user.btc >= 0.5:
            current_user.update(btc=current_user.btc-0.5, usd=current_user.usd+100)
            current_user.save()
            result = "You have received $100."
        else:
            result = "You can't afford the transaction for $100."
    elif item == "Random DDoS":
        if current_user.btc >= 0.05:
            current_user.update(btc=current_user.btc-0.05)
            current_user.save()
            result = "You have sacked a random internet user. I hope you feel better."
        else:
            result = "You can't afford a DDoS attack right now."

    stats = get_stats()
    stats["result"] = result

    return dumps(stats)
