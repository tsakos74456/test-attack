# -*- coding: utf-8 -*-
"""Application configuration."""
import os
import tempfile


_APP_DIR = os.path.abspath(os.path.dirname(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_APP_DIR, os.pardir))


def _load_secret(path):
    """Return a stable per-deployment SECRET_KEY.

    Gunicorn pre-forks workers; each worker imports `settings` in its own
    process. If each one rolls its own `os.urandom(...)`, sessions signed
    by worker A fail HMAC verification on worker B and a redirect chain
    of register -> follow / -> GET /users/mine/* trivially produces 401s.
    Atomically materialise a single value on disk so every worker
    converges on it. `os.link` is the atomicity primitive: it fails with
    FileExistsError if someone else won the race, leaving exactly one
    file content.
    """
    env = os.environ.get('BITCLICKER_SECRET')
    if env:
        return env.encode('utf-8') if isinstance(env, str) else env
    try:
        with open(path, 'rb') as f:
            data = f.read()
        if len(data) >= 16:
            return data
    except FileNotFoundError:
        pass
    new = os.urandom(32)
    try:
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix='.flask_secret.')
    except OSError:
        # Read-only deployment dir. Sessions won't survive across workers,
        # but the app still starts so the operator can spot the problem.
        return new
    try:
        os.write(fd, new)
        os.close(fd)
        try:
            os.link(tmp, path)
        except FileExistsError:
            pass
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    try:
        with open(path, 'rb') as f:
            return f.read()
    except OSError:
        return new


class Config(object):
    """Base configuration."""

    APP_DIR = _APP_DIR
    PROJECT_ROOT = _PROJECT_ROOT
    SECRET_KEY = _load_secret(os.path.join(_PROJECT_ROOT, '.flask_secret'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    DB_NAME = "bitclicker.db"
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
