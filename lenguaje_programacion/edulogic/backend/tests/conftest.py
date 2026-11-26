import os, tempfile, pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    fd,path=tempfile.mkstemp(suffix='.db'); os.close(fd)
    application=create_app({'TESTING':True,'SQLALCHEMY_DATABASE_URI':f'sqlite:///{path}','SECRET_KEY':'test'})
    with application.app_context(): db.create_all()
    yield application
    with application.app_context(): db.session.remove(); db.drop_all()
    os.unlink(path)

@pytest.fixture
def client(app): return app.test_client()
