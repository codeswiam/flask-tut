import sqlite3
from datetime import datetime

import click
from flask import current_app, g

# g is immediately available in templates

# you will need to run "flask --app flaskr init-db" to work with this

# connect to the database if not already connected
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row # allows accessing columns by name

    return g.db

# close a connection if it exists
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# execute the schema.sql script
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# define a cli cmd init-db that calls the init_db function
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# how to interpret timestamp values in the database
sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

# register the functions above with the app instance
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


