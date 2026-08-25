from os import getenv
from mssql_python import connect
import click

from flask import g, current_app, Flask
from dotenv import load_dotenv

load_dotenv()

connection_string = getenv("AZURE_SQL_CONNECTIONSTRING")

def get_db():
    if "db" not in g:
        try:
            g.db = connect(connection_string)
            g.db.setautocommit(True)
            
            return g.db

        except Exception as e:
            print(e)


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.execute(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """DROPS ALL TABLES AND CREATES NEW ONES"""
    init_db()
    click.echo('===DB Initialized===')

def init_app(app:Flask):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)