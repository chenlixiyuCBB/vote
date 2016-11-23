from flask import Flask, g
from werkzeug.contrib.cache import SimpleCache
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile("config.py", silent=True)
db = SQLAlchemy(app)

import view
import model

db.create_all()
db.session.commit()

cache = SimpleCache()


def get_com_count():
    com_count = cache.get("com_count")
    if com_count is None:
        com_count = db.session.query(model.competitor).count()
        cache.set("com_count", com_count)
    return com_count

def get_vote_count():
    vote_count = cache.get("vote_count")
    if vote_count is None:
        for com in db.session.query(model.competitor).all():
            vote_count = 0
            vote_count += com.count
        cache.set("vote_count",vote_count)
    return vote_count

def get_visit_count():
    visit_count = cache.get("visit_count")
    if visit_count is None:
        visit_count = db.session.query(model.visitor).count()
        cache.set("visit_count",visit_count)

def get_online_competitors():
    online_competitors = cache.get("online_competitors")
    if online_competitors is None:
        online_competitors = []
        for i in model.competitor.query().filter_by(method=1).order_by("count").limit(6).all():
            online_competitor = {}
            online_competitor['name'] = i.name
            online_competitor['company'] = i.company
            online_competitor['position'] = i.position
            online_competitor['photo'] = i.photo
            online_competitor['reason'] = i.reason
            online_competitor['method'] = i.method
            online_competitor['count']  = i.count
            online_competitors.append(online_competitor)

        cache.set("online_competitors",online_competitors)
    return online_competitors

def get_offline_competitors():
    offline_competitors = cache.get("offline_competitor")
    if offline_competitors is None:
        offline_competitors = []
        for i in  model.competitor.query().filter_by(method=1).order_by("count").limit(6).all():
            offline_competitor = {}
            offline_competitor['name'] = i.name
            offline_competitor['company'] = i.company
            offline_competitor['position'] = i.position
            offline_competitor['photo'] = i.photo
            offline_competitor['reason'] = i.reason
            offline_competitor['method'] = i.method
            offline_competitor['count']  = i.count
            offline_competitors.append(offline_competitor)
        cache.set("offline_competitors",offline_competitors)
    return offline_competitors


@app.before_first_request
def set_cache():
    get_com_count()
    get_vote_count()
    get_visit_count()
    get_online_competitors()
    get_offline_competitors()

@app.before_request
def get_cache():
    g.cache = cache