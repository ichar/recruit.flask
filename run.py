import os
from app import db, create_app

from app.models.persons import Person

app = create_app(os.getenv('APP_CONFIG') or 'default')

#from app import cli
#cli.register(app)

'''
@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, Person=Person)
'''

if __name__ == "__main__":
    app.run()

