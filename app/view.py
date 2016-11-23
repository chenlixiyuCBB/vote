# encoding = utf-8
from app import app,db,g
from app.model import competitor, reference, message, visitor



@app.route('/')
def index():
    com_count = g.cache.get("com_count")
    print com_count
    return ("<script>alert('fuck')</script>")
