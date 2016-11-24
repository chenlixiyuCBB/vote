# encoding=utf-8
from app import app,db
import model
import random
from flask_cache import Cache
#初始化缓存
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


'''对多个数据设置缓存'''
@cache.cached(timeout=1, key_prefix='com_count')
def get_com_count():
        com_count = db.session.query(model.competitor).count()
        return com_count

@cache.cached(timeout=1, key_prefix='vote_count')
def get_vote_count():
    vote_count = db.session.query(model.vote).count()
    return vote_count

@cache.cached(timeout=1, key_prefix='visit_count')
def get_visit_count():
        visit_count = db.session.query(model.visitor).count()
        return visit_count

@cache.cached(timeout=30, key_prefix='online_competitors')
def get_online_competitors():
        online_competitors = []
        for i in model.competitor.query.filter_by(method=1).order_by("count").limit(6).all():
            online_competitor = {}
            online_competitor['name'] = i.name
            online_competitor['company'] = i.company
            online_competitor['position'] = i.position
            online_competitor['photo'] = i.photo
            online_competitor['reason'] = i.reason
            online_competitor['method'] = i.method
            online_competitor['count']  = i.count
            online_competitors.append(online_competitor)

        return online_competitors


@cache.cached(timeout=30, key_prefix='offline_competitors')
def get_offline_competitors():
        offline_competitors = []
        for i in  model.competitor.query.filter_by(method=1).order_by("count").limit(6).all():
            offline_competitor = {}
            offline_competitor['name'] = i.name
            offline_competitor['company'] = i.company
            offline_competitor['position'] = i.position
            offline_competitor['photo'] = i.photo
            offline_competitor['reason'] = i.reason
            offline_competitor['method'] = i.method
            offline_competitor['count']  = i.count
            offline_competitors.append(offline_competitor)
        return offline_competitors


@cache.cached(timeout=30, key_prefix='range')
def get_range():
        range = []
        for i in model.competitor.query.order_by("count").all():
             competitor = {}
             competitor['name'] = i.name
             competitor['company'] = i.company
             competitor['position'] = i.position
             competitor['photo'] = i.photo
             competitor['reason'] = i.reason
             competitor['method'] = i.method
             competitor['count']  = i.count
             range.append(competitor)
        return range

@cache.cached(timeout=30, key_prefix='all_competitor')
def get_all():
        all_competitor = get_range()
        all_competitor = random.shuffle(all_competitor)
        return all_competitor

@app.before_first_request
def set_cache():
    get_com_count()
    get_vote_count()
    get_visit_count()
    get_online_competitors()
    get_offline_competitors()
    get_range()
    get_all()

