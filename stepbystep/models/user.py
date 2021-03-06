from stepbystep import db, login_manager
from datetime import datetime
from flask.ext.login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from .role import RoleModel
from mongoengine import DENY, NULLIFY  # noqa


@login_manager.user_loader
def load_user(id):
    return UserModel.objects(id=id).first()


class AccountItem(db.Document):
    origin_oj = db.StringField()
    username = db.StringField(max_length=255)
    nickname = db.StringField(max_length=255)
    accept = db.StringField()
    submit = db.StringField()
    rank = db.StringField()
    solved = db.DictField()
    rating = db.StringField()

    meta = {
        'collection': 'AccountItem'
    }

    def __unicode__(self):
        return '%s: %s' % (self.origin_oj, self.username)


class Account(db.EmbeddedDocument):
    user_id = db.StringField(max_length=255)
    account = db.ReferenceField(AccountItem)


class UserModel(db.Document, UserMixin):
    username = db.StringField(max_length=255)
    name = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    created_at = db.DateTimeField(default=datetime.now, required=True)
    roles = db.ListField(
        db.ReferenceField(
            'RoleModel',
            reverse_delete_rule=DENY
        ),
        default=[]
    )
    grade = db.StringField(max_length=255)

    poj = db.EmbeddedDocumentField(Account)
    sdut = db.EmbeddedDocumentField(Account)
    hduoj = db.EmbeddedDocumentField(Account)
    bestcoder = db.EmbeddedDocumentField(Account)
    topcoder = db.EmbeddedDocumentField(Account)
    codeforces = db.EmbeddedDocumentField(Account)

    last_login_at = db.DateTimeField()
    current_login_at = db.DateTimeField()
    last_login_ip = db.StringField(max_length=255)
    current_login_ip = db.StringField(max_length=255)

    @staticmethod
    def generate_password(password):
        return generate_password_hash(
            current_app.config['SECRET_KEY'] + password
        )

    def set_password(self, password):
        self.password = self.generate_password(password)

    def verify_password(self, password):
        return check_password_hash(
            self.password,
            current_app.config['SECRET_KEY'] + password
        )

    @classmethod
    def create_user(cls, username, password, **kwargs):
        password = cls.generate_password(password)
        return cls.objects.create(
            username=username,
            password=password,
            **kwargs
        )

    def is_administrator(self):
        admin = RoleModel.objects(name='admin').first()
        return admin in self.roles

    def __unicode__(self):
        return self.username

    meta = {
        'collection': 'User'
    }


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
