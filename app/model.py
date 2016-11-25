# encoding=utf-8
from app import db
import time

class competitor(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    company = db.Column(db.String(30))
    position = db.Column(db.String(15))
    photo = db.Column(db.String(50))
    reason = db.Column(db.String(400))
    method = db.Column(db.Integer) # 1为线上提名 2为线下提名
    count = db.Column(db.Integer)
    reference_id = db.Column(db.Integer, db.ForeignKey("reference.id"))

    reference = db.relationship('reference', backref=db.backref('competitor'))

    def __init__(self,name,company,position,photo,reason,method,reference_id):
        if name is None:
            raise ValueError("name is needed!")
        if company is None:
            raise  ValueError("company is needed!")
        if position is None:
            raise  ValueError("position is needed!")
        if photo is None:
            raise ValueError("photo is needed!")
        if reason is None:
            raise ValueError("reason is needed!")
        if method is None:
            raise ValueError("method is needed!")
        if method is None:
            raise ValueError("reference_id is needed!")

        self.name = name
        self.company = company
        self.position = position
        self.photo = photo
        self.reason = reason
        self.method = method
        self.count = 0
        self.reference=reference

    def __repr__(self):
        return "<competitor name %s company %s position %s photo %s reason %s method %s count %s reference%s>" %(self.name,self.company,self.position,
        self.photo,self.reason,self.method,self.count,self.reference)

    def save(self):
        db.session.add(self)
        db.session.commit()



class reference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(13))
    password = db.Column(db.String(20))

    def __init__(self,phone,password):
        if phone is None:
            raise ValueError("phone is needed!")
        if password is None:
            raise ValueError("password is needed!")

        self.phone = phone
        self.password = password

    def __repr__(self):
        return "reference: phone %s password %s" %(self.phone,self.password)

    def save(self):
        db.session.add(self)
        db.session.commit()

class visitor(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(10))
    ip = db.Column(db.String(15))
    time = db.Column(db.Date)

    def __init__(self,name,ip):
        if name is None:
            raise ValueError("name is needed!")
        if ip is None:
            raise ValueError("ip is needed!")
        self.ip = ip
        self.name = name
        self.time = time.strftime("%Y-%m-%d", time.localtime())

    def __repr__(self):
        return "visitor: name %s ip %s time %s" %(self.name,self.ip,self.time)

    def save(self):
        db.session.add(self)
        db.session.commit()

class message(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.String(200))
    we_id = db.Column(db.String(20),index=True)
    time = db.Column(db.Date)
    competitor_id = db.Column(db.Integer,db.ForeignKey("competitor.id"))

    competitor = db.relationship("competitor", backref=db.backref("message"))

    def __init__(self,content,we_id,competitor_id):
        if content is None:
            raise ValueError("content is needed!")
        if we_id is None:
            raise ValueError("we_id is needed!")
        if competitor_id is None:
            raise ValueError("competitor_id is needed!")

        self.content = content
        self.we_id = we_id
        self.time = time.strftime("%Y-%m-%d", time.localtime())
        self.competitor_id = competitor_id

    def __repr__(self):
        return "message: content %s we_id %s time %s competitor %s"%(self.content,self.visitor,self.competitor)

    def save(self):
        db.session.add(self)
        db.session.commit()



class vote(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    we_id = db.Column(db.String(15),index=True)
    time = db.Column(db.Date)
    competitor_id = db.Column(db.Integer,db.ForeignKey("competitor.id"))

    competitor = db.relationship(competitor,backref=db.backref("vote"))

    def __init__(self,we_id,competitor_id):
        if we_id is None:
            raise ValueError("content is needed!")
        if competitor_id is None:
            raise ValueError("time is needed!")

        self.we_id = we_id
        self.time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.competitor_id = competitor_id

    def __repr__(self):
        return "vote: we_id %s time %s competitor %s"%(self.we_id,self.time,self.competitor_id)

    def save(self):
        db.session.add(self)
        db.session.commit()
