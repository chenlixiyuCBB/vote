# encoding=utf-8
from app import app,db
from app.model import competitor, reference, message, visitor, vote,admin
from flask import request, render_template,redirect, url_for
from cache import get_com_count,get_all,get_visit_count,get_vote_count,\
    get_offline_competitors,get_online_competitors,get_range
from sqlalchemy.exc import SQLAlchemyError
import os,random,string
from json import dumps,loads
from unity import competitor2dict, allowed_file,message2dict,competitors2list


# 处理访问首页的请求
@app.route('/index/<name>/') #测试通过
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

    return render_template("index.html", com_count=com_count, vote_count=vote_count,
                           visit_count=visit_count,online_competitors=online_competitors,
                           offline_competitors=offline_competitors)
'''
    return (dumps(dict(com_count=com_count,vote_count=vote_count,visit_count=visit_count,
            online_competitors=online_competitors,offline_competitors=offline_competitors)))'''


# 处理全部页面初次请求,参赛者顺序排列随机，分页后返回第一页以及页数
@app.route('/all/')#测试通过
def all_first():
    return redirect(url_for('all',page=1))


# 处理全部页面后续请求，参赛者
@app.route('/all/<int:page>/')#测试通过
def all(page):
    all_competitor = get_all()
    len_all = len(all_competitor)
    if page % 8 == 0:
        page_count = len_all / 8
    else:
        page_count = len_all / 8 + 1

    if 8*page > len_all:
        competitors = all_competitor[8*(page-1):len_all]
    else:
        competitors = all_competitor[8*(page-1):8*page]
    #return (dumps(dict(page_count=page_count, competitors=competitors)))

    return  render_template("all.html",competitors=competitors,page_count=page_count,page=page)


# 处理排行榜页面请求，方法同上
@app.route('/range/')#测试通过
def range_first():
    return redirect(url_for('range',page=1))



# 处理排行榜页面后续请求
@app.route('/range/<int:page>/')#测试通过
def range(page):
    range = get_range()
    len_range = len(range)
    if page % 8 == 0:
        page_count = len_range / 8
    else:
        page_count = len_range / 8 + 1
    if 8*page > len_range:
        competitors = range[8*(page-1):len_range]
    else:
        competitors = range[8*(page-1):8*page]
    #return (dumps(dict(page_count=page_count, competitors=competitors)))

    return  render_template("range.html",competitors=competitors,page_count=page_count,page=page)


@app.route('/reference/',methods=['POST','GET'])#测试通过#TODO
def deal_reference():
    if request.method == 'GET':
        #return "12413423242"
        return render_template("reference.html")
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']
        if reference.query.filter_by(phone=phone).all()[0] is not None:
            return dumps(dict(statu=1,info='此手机号已经提名过'))
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

        cur_reference = reference.query.filter_by(phone=phone).all()[0]
        reference_id = cur_reference.id

        name = request.form['name']
        company = request.form['company']
        position = request.form['position']
        photo = request.form['photo']
        reason = request.form['reason']
        method = 1
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
        # return 'ok'
        return render_template('success.html',competitor=cur_competition,reference=cur_reference)


@app.route('/login/', methods=['POST','GET'])#测试通过
def login():
    if request.method == 'GET':
        return render_template('login.html')
    phone = request.form['phone']
    password = request.form['password']
    cur_reference = reference.query.filter_by(phone=phone, password=password).all()[0]
    if cur_reference is not None:
        competitor = competitor2dict(cur_reference.competitor[0])
        #return dumps(competitor)
        return render_template('edit.html', competitor=competitor,reference=cur_reference)
    return dumps({'statu': 1})


@app.route('/upload/', methods=['POST'])
def upload_file():
    file = request.form['image']
    filename = request.form['fileName']
    if file and allowed_file(filename):
        try:
         filename = (''.join(random.choice(string.ascii_uppercase + string.digits) for _ in [1,2,3,4,5,6,7,8,9,0])+'.'+filename.rsplit('.', 1)[1]).decode('ascii')
         with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'wb') as image:
           image.write(file)
           return dumps({'statu':0,'photo':filename})
        except:
            return dumps({'statu': 1})
    return dumps({'statu':1})

@app.route('/vote/',methods=['POST'])#测试通过（缺少投票限制）#TODO
def deal_vote():
    name = request.form['name'].encode('utf-8')
    position = request.form['position'].encode('utf-8')
    we_id = request.form['we_id'].encode('utf-8')

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

@app.route('/detail/<name>/<position>/',methods=['GET'])#测试通过
def get_detail(name,position):
    cur_competitor = competitor.query.filter_by(name=name,position=position).all()[0]
    cur_messages = cur_competitor.message
    messages = []
    for message in cur_messages:
        message = message2dict(message)
        messages.append(message)

    cur_competitor = competitor2dict(cur_competitor)
    #return dumps(dict(messages=messages,competitor=cur_competitor))
    return render_template('userInfo.html',competitor=cur_competitor,messages=messages)

@app.route('/detail/<phone>/',methods=['GET']) #测试通过
def get_detail_1(phone):
    cur_reference = reference.query.filter_by(phone=phone).all()[0]
    cur_competitor = cur_reference.competitor[0]
    cur_messages = cur_competitor.message
    messages = []
    for message in cur_messages:
        message = message2dict(message)
        messages.append(message)

    cur_competitor = competitor2dict(cur_competitor)
    #return dumps(dict(messages=messages, competitor=cur_competitor))
    return render_template('userInfo.html',competitor=cur_competitor,messages=messages)

@app.route('/message/',methods=['POST'])#测试通过
def deal_message():
    name = request.form['name'].encode('utf-8')
    positon = request.form['position'].encode('utf-8')
    content = request.form['content'].encode('utf-8')
    we_id = request.form['we_id'].encode('utf-8')

    cur_competitor = competitor.query.filter_by(name=name,position=positon).all()[0]
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
    return dumps({'statu':0,'message':message2dict(cur_message)})

@app.route('/follow/',methods=['GET'])
def follow():
    return render_template('follow.html')

@app.route('/edit/',methods=['POST'])
def edit():
    id = int(request.form['id'])
    reference_id = int(request.form['reference_id'])

    phone = request.form['phone']
    password = request.form['password']
    name = request.form['name']
    company = request.form['company']
    position = request.form['position']
    photo = request.form['photo']
    reason = request.form['reason']
    statu = int(request.form['statu'])
    try:
        cur_reference = reference(phone, password,reference_id)
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

    try:
        cur_competition = competitor(name, company, position, photo, reason, 1, reference_id,id,statu)
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
    return dumps(dict(statu=0))

@app.route('/admin/login/',methods=['POST','GET'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    name = request.form['name']
    password = request.form['password']

    cur_admin = admin.query.filter_by(name=name,password=password).all()[0]

    if cur_admin is not None:
        return render_template('admin_index.html')

@app.route('/admin/unreview/<int:page>/',methods=['GET'])
def get_unreview(page):
    competitors = competitor.query.filter_by(statu=0).all()
    len_all = len(competitors)
    if page % 8 == 0:
        page_count = len_all / 8
    else:
        page_count = len_all / 8 + 1

    if 8*page > len_all:
        competitors = competitors[8*(page-1):len_all]
    else:
        competitors = competitors[8*(page-1):8*page]
    competitors = competitors2list(competitors)
    return render_template('unreview.html',competitors=competitors,page=page,page_count=page_count)

@app.route('/admin/review/<int:page>/',methods=['GET'])
def get_review(page):
    competitors = competitor.query.filter_by(statu=1).all()
    len_all = len(competitors)
    if page % 8 == 0:
        page_count = len_all / 8
    else:
        page_count = len_all / 8 + 1

    if 8*page > len_all:
        competitors = competitors[8*(page-1):len_all]
    else:
        competitors = competitors[8*(page-1):8*page]
    competitors = competitors2list(competitors)
    return render_template('review.html',competitors=competitors,page=page,page_count=page_count)

@app.route('/admin/deleteCompetitors',methods=['POST'])
def rm_competitors():
    id_list = request.get_json(force=True)
    id_list = loads(id_list)
    try:
       db.session.query(competitor).filter(competitor.id.in_(id_list)).delete(synchronize_session=False)
       db.session.commit()
    except:
        return dumps(dict(statu=1))
    return dumps(dict(statu=0))

@app.route('/admin/editCompetitor/',methods=['POST'])
def edit_competitor():
    id = int(request.form['id'])
    reference_id = int(request.form['reference_id'])
    name = request.form['name']
    company = request.form['company']
    position = request.form['position']
    photo = request.form['photo']
    reason = request.form['reason']
    method = int(request.form['method'])
    status = int(request.form['status'])

    try:
        cur_competitor = competitor(name, company, position, photo, reason, method, reference_id,id,status)
    except ValueError,argument:
        app.logger.error(argument)
        return dumps(dict(statu=1,info=argument))

    try:
        cur_competitor.save()
    except SQLAlchemyError,argument:
        app.logger.error(argument)
        return dumps(dict(statu=1,info=argument))
    return dumps(dict(statu=0))

@app.route('/admin/deleteMessages/',methods=['POST'])
def delete_message():
    id_list = request.get_json(force=True)
    id_list = loads(id_list)
    try:
       db.session.query(delete_message).filter(delete_message.id.in_(id_list)).delete(synchronize_session=False)
       db.session.commit()
    except SQLAlchemyError,argument:
        return dumps(dict(statu=1,info=argument))
    return dumps(dict(statu=0))


@app.route('/admin/getMessage/<int:page>/',methods=['GET'])
def get_message(page):
    try:
        messages = message.query.all()
    except SQLAlchemyError,argument:
        app.logger.error(argument)
        return dumps(dict(statu=1, info=argument))
    len_all = len(messages)
    if page % 8 == 0:
        page_count = len_all / 8
    else:
        page_count = len_all / 8 + 1
    if 8*page > len_all:
        messages = messages[8*(page-1):len_all]
    else:
        messages = messages[8*(page-1):8*page]

    return render_template('messages.html',messages=messages,page=page,page_count=page_count)

@app.route('/admin/searchMessage/',methods=['POST'])
def search_message():
    name = request.form['name']
    competitors = competitor.query.filter_by(name=name).all()
    messages = []
    for cur_competitor in competitors:
        messages.extend(cur_competitor.message)
    return render_template('message,html',messages=messages)


