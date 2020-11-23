import flask
from application import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class User(db.Document):
    user_id     =   db.IntField( unique=True)
    first_name  =   db.StringField( max_length=50 )
    last_name   =   db.StringField( max_length=50 )
    email       =   db.StringField( max_length=30, unique=True )
    password    =   db.StringField()
    role        =   db.StringField( max_length=50 )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'email': self.email}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            email = s.loads(token)['email']
        except:
            return None
        return User.objects.get(email=email)   

class Universitymail(db.Document):
    user_id     =   db.IntField( unique=True)
    email       =   db.StringField( max_length=30, unique=True )
    role        =   db.StringField( max_length=50 )

class Professor(db.Document):
    prof_id     =   db.IntField( unique=True)
    Name        =   db.StringField( max_length=50 )
    Designation =   db.StringField( max_length=50 )
    Dept        =   db.StringField( max_length=30 )
    MailID      =   db.StringField( max_length=30 )

class Appointment(db.Document):
    myid        =   db.IntField( db_field='id', unique=True)
    prof_id     =   db.IntField( max_length=50 )    
    user_id     =   db.IntField( max_length=50 )
    prof_name   =   db.StringField( max_length=50 )  
    status      =   db.StringField( max_length=20 )  
    slot        =   db.StringField( max_length=30 )   
    date        =   db.DateField()

class Holiday(db.Document):
    holiday_id  =   db.IntField( unique=True)
    date        =   db.DateField(unique=True)

class Professorslot(db.Document):
    block_id    =   db.IntField( unique=True)
    prof_id     =   db.IntField( max_length=50 )    
    date        =   db.DateField(unique=True)
    slots       =   db.ListField()