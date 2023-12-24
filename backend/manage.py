from flask_script import Manager
from flask_migrate import MigrateCommand

from your_application import app_admin, db

manager = Manager(app_admin)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
