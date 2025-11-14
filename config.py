import os
SECRET_KEY = os.urandom(24)

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://exam_user:exam_password@localhost/exam_db'