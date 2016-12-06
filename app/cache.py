# encoding=utf-8
from app import app,db
import model
import random
from flask_cache import Cache
from unity import competitor2dict
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
        count = 1
        for i in model.competitor.query.filter_by(method=1,status=1).order_by("count").limit(6).all():
            i = competitor2dict(i)
            i['id'] = count
            count += 1
            online_competitors.append(i)

        return online_competitors


@cache.cached(timeout=30, key_prefix='offline_competitors')
def get_offline_competitors():
        offline_competitors = []
        count = 1
        for i in  model.competitor.query.filter_by(method=2,status=1).order_by("count").limit(6).all():
            i = competitor2dict(i)
            i['id'] = count
            count += 1
            offline_competitors.append(i)
        return offline_competitors


@cache.cached(timeout=30, key_prefix='range')
def get_range():
        range = []
        count = 1
        for i in model.competitor.query.filter_by(status=1).order_by("count").all():
            i = competitor2dict(i)
            i['id'] = count
            count += 1
            range.append(i)
        return range

@cache.cached(timeout=30, key_prefix='all_competitor')
def get_all():
        all_competitor = []
        count = 1
        for i in model.competitor.query.filter_by(status=1).all():
            i = competitor2dict(i)
            i['id'] = count
            count += 1
            all_competitor.append(i)
        all_competitor = random.sample(all_competitor, len(all_competitor))
        return all_competitor



