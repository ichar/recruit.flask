# -*- coding: utf-8 -*-

import uuid
import datetime
from operator import itemgetter

from app import db
from app import login_manager
from flask_login import UserMixin, AnonymousUserMixin
from flask_security import RoleMixin
from sqlalchemy.dialects.postgresql import CHAR, VARCHAR, UUID
from werkzeug.security import generate_password_hash, check_password_hash

from config import default_print_encoding


##  =============================
##  Строительство класса объектов
##  =============================


class ExtClassMethods(object):
    """
        Abstract class methods
    """
    @classmethod
    def all(cls):
        return cls.query.all()

    @classmethod
    def count(cls):
        return cls.query.count()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def print_all(cls):
        for x in cls.all():
            print(x)


'''
    Определение модели пользователей
'''
roles_users = db.Table('roles_users',
                       db.Column('user_id', UUID(as_uuid=True),
                                 db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), default=uuid.uuid4),
                       db.Column('role_id', UUID(as_uuid=True),
                                 db.ForeignKey('roles.id', onupdate='CASCADE', ondelete='CASCADE'), default=uuid.uuid4)
                       )


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    #######################################################
    us = db.relationship('User', secondary=roles_users)

    def __str__(self):
        return self.name


class User(db.Model, UserMixin, ExtClassMethods):
    __tablename__ = 'users'
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name = db.Column(VARCHAR(100), unique=True, nullable=False)
    user_name = db.Column(VARCHAR(100), nullable=False)
    user_surname = db.Column(VARCHAR(100), nullable=True)
    user_patronymic = db.Column(VARCHAR(100), nullable=True)
    password_hash = db.Column(VARCHAR(128), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                         backref=db.backref('users', lazy='dynamic'))
    theme = db.relationship('UserTheme')

    # mil_uid = db.Column(
    #    UUID(as_uuid=True),
    #    ForeignKey('milstrusture.uid'),
    #    default=uuid.uuid4
    # )

    def __init__(self, password, user_name, user_surname=None, user_patronymic=None, active=False,
                 confirmed_at=datetime.datetime.now(), name='admin'):
        self.name = name
        self.user_name = user_name
        self.user_surname = user_surname
        self.user_patronymic = user_patronymic
        self.active = active
        self.confirmed_at = confirmed_at
        self.password = self.set_password(password)

    def __repr__(self):
        return '<User %s:[%s] id=uid[%s] active=%s>' % (self.name, self.full_name, str(self.id), str(self.active and 1 or 0))

    #   -----------------------
    #   Permission settings XXX
    #   -----------------------

    @staticmethod
    def get_user_by_login(name):
        return User.query.filter_by(name=name).first()

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def can(self, role):
        return self.role is not None and roles[self.role] == role
    @property
    def is_authenticated(self):
        return True
    @property
    def is_active(self):
        return self.active and 1 or 0
    @property
    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return 1
        else:
            return 0
    @property
    def is_any(self):
        return self.is_active
    @property
    def is_anybody(self):
        return self.is_any
    @property
    def is_nobody(self):
        return 0
    @property
    def full_name(self):
        return ('%s %s %s' % (self.user_name, self.user_surname, self.user_patronymic)).strip()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def set_confirmed_at(self, confirmed_at):
        self.confirmed_at = confirmed_at

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id

    def get_fio(self):

        fio = self.full_name

        if fio:
            fio = ' %s' % fio 
        else: 
            fio = '-'

        return fio

    def short_name(self, is_back=None):
        if self.user_surname and self.user_name and self.user_patronymic:
            f = self.user_surname
            n = self.user_name and '%s.' % self.user_name[0] or ''
            o = self.user_patronymic and '%s.' % self.user_patronymic[0] or ''
            return (is_back and 
                '%s%s %s' % (n, o, f) or 
                '%s %s%s' % (f, n, o)
                ).strip()
        return self.full_name

    def has_role(self, *args):
        return set(args).issubset({role.name for role in self.roles})

    def get_roles(self):
        return (role.name for role in self.roles)

    #   -------------------------------
    #   Application roles & permissions
    #   -------------------------------

    def is_superuser(self, private=False):
        return 1

    def is_administrator(self, private=False):
        return 1

    def is_manager(self, private=False):
        return 1

    def is_operator(self, private=False):
        return 1


class UserTheme(db.Model):
    __tablename__ = 'user_theme'

    uid = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment='Уникальный идентификатор'
    )

    user_uid = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='CASCADE'),
        default=uuid.uuid4,
        comment='Уникальный идентификатор'
    )

    page_content_background = db.Column(
        db.String(255),
        nullable=True,
        comment='Цвет основного фона'
    )

    card_header_background = db.Column(
        db.String(255),
        nullable=True,
        comment='Цвет фона заголоков карточек'
    )

    card_header_border = db.Column(
        db.String(255),
        nullable=True,
        comment='Бордюр заголоков карточек'
    )

    card_header_color = db.Column(
        db.String(255),
        nullable=True,
        comment='Цвет шрифта заголовка карточек'
    )

    card_header_font_family = db.Column(
        db.String(255),
        nullable=True,
        comment='Класс шрифта заголоков карточек'
    )

    card_header_font_size = db.Column(
        db.String(255),
        nullable=True,
        comment='Размер шрифта заголоков карточек'
    )

    card_header_font_weigth = db.Column(
        db.String(255),
        nullable=True,
        comment='Насыщенность шрифта заголоков карточек'
    )

    card_body_background = db.Column(
        db.String(255),
        nullable=True,
        comment='Цвет фона тела карточек'
    )

    card_body_border = db.Column(
        db.String(255),
        nullable=True,
        comment='Бордюр тела карточек'
    )

    card_body_color = db.Column(
        db.String(255),
        nullable=True,
        comment='Цвет шрифта тела карточек'
    )

    card_body_font_family = db.Column(
        db.String(255),
        nullable=True,
        comment='Класс шрифта тела карточек'
    )

    card_body_font_size = db.Column(
        db.String(255),
        nullable=True,
        comment='Размер шрифта тела карточек'
    )

    card_body_font_weigth = db.Column(
        db.String(255),
        nullable=True,
        comment='Насыщенность шрифта тела карточек'
    )

    card_footer_background = db.Column(
        db.String(255),
        nullable=True,
        comment='Цвет фона подвала карточек'
    )

    card_footer_border = db.Column(
        db.String(255),
        nullable=True,
        comment='Бордюр подвала карточек'
    )

    card_footer_color = db.Column(
        db.String(255),
        nullable=True,
        comment='Цвет шрифта подвала карточек'
    )

    card_footer_font_family = db.Column(
        db.String(255),
        nullable=True,
        comment='Класс шрифта подвала карточек'
    )

    card_footer_font_size = db.Column(
        db.String(255),
        nullable=True,
        comment='Размер шрифта подвала карточек'
    )

    card_footer_font_weigth = db.Column(
        db.String(255),
        nullable=True,
        comment='Насыщенность шрифта подвала карточек'
    )


class DefaultTheme(db.Model):
    uid = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment='Уникальный идентификатор'
    )

    body_background = db.Column(
        db.String(255),
        nullable=True,
        comment='Цвет основного фона'
    )

    card_header_background = db.Column(
        db.String(255),
        nullable=True,
        comment='Цвет фона заголоков карточек'
    )

    card_header_color = db.Column(
        db.String(255),
        nullable=True,
        comment='Цвет шрифта заголоков карточек'
    )

    card_header_font_family = db.Column(
        db.String(255),
        nullable=True,
        comment='Класс шрифта заголоков карточек'
    )

    card_header_font_size = db.Column(
        db.String(255),
        nullable=True,
        comment='Размер шрифта заголоков карточек'
    )

    card_header_font_weigth = db.Column(
        db.String(255),
        nullable=True,
        comment='Насыщенность шрифта заголоков карточек'
    )

    card_body_background = db.Column(
        db.String(255),
        nullable=True,
        comment='Цвет фона тела карточек'
    )

    card_body_color = db.Column(
        db.String(255),
        nullable=True,
        comment='Цвет шрифта тела карточек'
    )

    card_body_font_family = db.Column(
        db.String(255),
        nullable=True,
        comment='Класс шрифта тела карточек'
    )

    card_body_font_size = db.Column(
        db.String(255),
        nullable=True,
        comment='Размер шрифта тела карточек'
    )

    card_body_font_weigth = db.Column(
        db.String(255),
        nullable=True,
        comment='Насыщенность шрифта тела карточек'
    )


##  ==========================


def get_users(key=None, is_ob=None):
    users = []
    for ob in User.all():
        if not ob.is_active:
            continue
        if is_ob:
            users.append(ob)
        else:
            users.append((
                ob.name,
                ob.full_name,
                ob.short_name(),
                ob.id,
                ob.active,
            ))
    if is_ob:
        return sorted(users, key=lambda x: x.full_name)
    return sorted(users, key=itemgetter(key is None and 1 or key or 0))

def get_users_dict(key=None, as_dict=None):
    if as_dict:
        return dict([(x[0], dict(zip(['name', 'full_name', 'short_name', 'id', 'active'], x[1:]))) for x in get_users(key)])
    return [dict(zip(['name', 'full_name', 'short_name', 'id', 'active'], x)) for x in get_users(key)]

def print_users(key=None):
    for x in get_users_dict(key):
        print(('%s: %s %s %s %s' % (
            x['name'], 
            x['full_name'], 
            x['short_name'], 
            x['id'], 
            x['active'], 
            )).encode(default_print_encoding, 'ignore').decode(default_print_encoding))


@login_manager.user_loader
def load_user(id):
    return User.query.get(str(id))
