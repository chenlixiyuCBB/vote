# encoding=utf-8
from app import app, db
from app.model import competitor, reference, message, visitor
from flask import request, render_template,redirect, url_for
from cache import get_com_count,get_all,get_visit_count,get_vote_count,\
    get_offline_competitors,get_online_competitors,get_range
from sqlalchemy.exc import SQLAlchemyError
import os
from werkzeug import security
from json import dumps
from unity import competitor2dict, allowed_file, secure_filename,message2dict
import base64

# 处理访问首页的请求
@app.route('/index/<name>/')
def index(name):
    ip = request.remote_addr
    try:
        cur_visitor = visitor(name, ip)
    except ValueError, argument:
        app.logger.error(argument)
        return dumps({'statu':1,'info':str(argument)})

    try:
        visitor.save(cur_visitor)
    except SQLAlchemyError, argument:
        app.logger.error(argument)
        return dumps({'statu': 1, 'info': str(argument)})
    # 由缓存中取数据
    com_count = get_com_count()
    vote_count = get_vote_count()
    visit_count = get_visit_count()

    online_competitors = get_online_competitors()
    offline_competitors = get_offline_competitors()
    '''
    return render_template("index.html", com_count=com_count, vote_count=vote_count,
                           visit_count=visit_count,online_competitors=online_competitors,
                           offline_competitors=offline_competitors) '''

    return (dumps(dict(com_count=com_count,vote_count=vote_count,visit_count=visit_count,
            online_competitors=online_competitors,offline_competitors=offline_competitors)))


# 处理全部页面初次请求,参赛者顺序排列随机，分页后返回第一页以及页数
@app.route('/all/')
def all_first():
    return redirect(url_for('all',page=1))


# 处理全部页面后续请求，参赛者
@app.route('/all/<int:page>/')
def all(page):
    all_competitor = get_all()
    len_all = len(all_competitor)
    page_count = len_all / 8 + 1
    if 8*page > len_all:
        competitors = all_competitor[8*(page-1):len_all]
    else:
        competitors = all_competitor[8*(page-1):8*page]
    return (dumps(dict(page_count=page_count, competitors=competitors)))
    '''
    return  render_template("all.html",competitors=competitors,page_count=page_count,page=page)'''


# 处理排行榜页面请求，方法同上
@app.route('/range/')
def range_first():
    return redirect(url_for('range',page=1))

    '''
    return render_template("range.html",competitors=competitors,page_count=page_count,page=1)'''


# 处理排行榜页面后续请求
@app.route('/range/<int:page>/')
def range(page):
    range = get_range()
    len_range = len(range)
    page_count = len_range / 8 + 1
    if 8*page > len_range:
        competitors = range[8*(page-1):len_range]
    else:
        competitors = range[8*(page-1):8*page]
    return (dumps(dict(page_count=page_count, competitors=competitors)))
    '''
    return  render_template("range.html",competitors=competitors,page_count=page_count,page=page)'''


@app.route('/reference/', methods=['POST', 'GET'])
def refernce():
    if request.method == 'GET':
        return "12413423242"
        # return render_template("reference.html")
    else:
        phone = request.form['phone']
        password = request.form['password']
        try:
            cur_reference = reference(phone, password)
        except ValueError, argument:
            app.logger.error(argument)
            info = {'statu': 1, 'info': str(argument)}
            return dumps(info)
        try:
            cur_reference.save()
        except SQLAlchemyError, argument:
            app.logger.error(argument)
            info = {'statu': 1, 'info': str(argument)}
            return dumps(info)

        cur_reference = reference.query.filter_by(phone=phone).all()
        reference_id = cur_reference[0].id

        name = request.form['name']
        company = request.form['company']
        position = request.form['position']
        photo = request.form['photo']
        reason = request.form['reason']
        method = request.form['form']
        reference_id = reference_id

        try:
            cur_competition = competitor(name, company, position, photo, reason, method, reference_id)
        except ValueError, argument:
            app.logger.error(argument)
            info = {'statu': 1, 'info': str(argument)}
            return dumps(info)
        try:
            cur_competition.save()
        except SQLAlchemyError, argument:
            app.logger.error(argument)
            info = {'statu': 1, 'info': str(argument)}
            return dumps(info)

        return redirect(url_for("detail"))


@app.route('/login/', methods=['POST'])
def login():
    phone = request.form['phone']
    password = request.form['password']
    cur_reference = reference.query.filter_by(phone=phone, password=password).all()
    if len(cur_reference) > 0:
        competitor = competitor2dict(cur_reference[0].competitor[0])
        return dumps(competitor)
        #return render_template('manage.html', competitor=competitor)
    return dumps({'statu': 1})


@app.route('/upload/', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return dumps({'statu':0,'photo':app.config['UPLOAD_FOLDER']+filename})
    return dumps({'statu':1})

@app.route('/vote/',methods=['POST'])
def vote():
    name = request.form['name']
    position = request.form['position']
    we_id = request.form['we_id']

    cur_competitor = competitor.query.filter_by(name=name,position=position).all()[0]

    competitor_id = cur_competitor.id
    cur_competitor.count += 1

    try:
        cur_competitor.save()
    except SQLAlchemyError,argument:
        app.logger.error(argument)
        return dumps({'statu':1,'info':str(argument)})

    try:
        cur_vote = vote(we_id,competitor_id)
    except ValueError,argument:
        app.logger.error(argument)
        return dumps({'statu':1,'info':str(argument)})
    try:
        cur_vote.save()
    except SQLAlchemyError,argument:
        app.logger.error(argument)
        return dumps({'statu': 1, 'info': str(argument)})
    return dumps({'statu':0})

@app.route('/detail/<name>/<position>/',methods=['GET'])
def get_detail(name,position):
    cur_competitor = competitor.query.filter_by(name=name,position=position).all()[0]
    cur_messages = cur_competitor.message
    messages = []
    for message in cur_messages:
        message = message2dict(message)
        messages.append(message)

    cur_competitor = competitor2dict(cur_competitor)

    return render_template('detail.html',competitor=cur_competitor,messages=messages)

@app.route('/detail/<phone>/',methods=['GET'])
def get_detail_1(phone):
    cur_reference = reference.query.filter_by(phone=phone).all()[0]
    cur_competitor = cur_reference.competitor
    cur_messages = cur_competitor.message
    messages = []
    for message in cur_messages:
        message = message2dict(message)
        messages.append(message)

    cur_competitor = competitor2dict(cur_competitor)

    return render_template('detail.html', competitor=cur_competitor, messages=messages)

@app.route('/message/',methods=['POST'])
def message():
    name = request.form['name']
    positon = request.form['position']
    content = request.form['content']
    we_id = request.form['we_id']

    cur_competitor = competitor.query.filter_by(name=name,positon=positon).all()[0]
    competitor_id = cur_competitor.id

    try:
        cur_message = message(content,we_id,competitor_id)
    except ValueError,argument:
        app.logger.error(argument)
        return dumps({'statu':1,'info':str(argument)})
    try:
        cur_message.save()
    except SQLAlchemyError,argument:
        app.logger.error(argument)
        return dumps({'statu':1,'info':str(argument)})
    return dumps({'statu':0,'message':message2dict(message)})
