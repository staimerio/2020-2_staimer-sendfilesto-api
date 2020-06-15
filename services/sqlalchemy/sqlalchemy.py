"""Settings of SQLAlchemy"""

# Retic
from retic import App

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.query import Query

# Services
from services.sqlalchemy.base import Base

# Models
from models import *

"""Define all options"""

OPTIONS_URI = {
    u'drivername': App.config.get("MYSQL_DRIVERNAME"),
    u'host': App.config.get("MYSQL_HOST"),
    u'port': App.config.get("MYSQL_PORT", callback=int),
    u'username': App.config.get("MYSQL_USERNAME"),
    u'password': App.config.get("MYSQL_PASSWORD"),
    u'database': App.config.get("MYSQL_DATABASE"),
    u'query': App.config.get("MYSQL_QUERY"),
}
OPTIONS_ENGINE = {
    u"echo": App.config.get("MYSQL_ECHO", callback=bool)
}


def config_sqlalchemy():
    """Define the URI"""
    _database_uri = URL(**OPTIONS_URI)

    """Define the Engine"""
    _engine = create_engine(_database_uri, **OPTIONS_ENGINE)

    # create all models
    Base.metadata.drop_all(_engine)
    Base.metadata.create_all(_engine)

    """Define the session"""
    _sessionmaker = sessionmaker(_engine)
    return _sessionmaker
