from app import app
from flask_script import Manager

manager = Manager(app)
manager.add_command("runserver",app.run())


