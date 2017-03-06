from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
import time
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from credentials import POSTGRES_CREDENTIALS, SECRET_KEY
from utils import to_timestamp

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_CREDENTIALS
db = SQLAlchemy(app)
api = Api(app)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    vacancies = db.relationship('Vacancy', backref='department', lazy='dynamic', cascade='delete')
    employees = db.relationship('Employee', backref='department', lazy='dynamic', cascade='delete')

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return 'Department {}'.format(self.name)


class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    vacancies = db.relationship('Vacancy', backref='position', lazy='dynamic', cascade='delete')

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return 'Position {}'.format(self.name)


class Vacancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_opened = db.Column(db.BigInteger, nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))

    def __init__(self, position_id, department_id, date_opened=None):
        self.position_id = position_id
        self.department_id = department_id
        if date_opened is None:
            date_opened = int(time.time())
        self.date_opened = date_opened

    def __repr__(self):
        return 'Vacancy for {}'.format(self.position.name)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    birth_date = db.Column(db.String(50))
    start_work_date = db.Column(db.BigInteger)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    is_department_leader = db.Column(db.Boolean, default=False)

    def __init__(self, name, surname, position_id, department_id):
        self.name = name
        self.surname = surname
        self.position_id = position_id
        self.department_id = department_id
        self.start_work_date = int(time.time())

    def __repr__(self):
        return 'Employee {} {}'.format(self.name, self.surname)


@app.route('/')
def index():
    all_departments = Department.query.all()
    all_positions = Position.query.all()
    return render_template('index.html', depts=all_departments, positions=all_positions)


@app.route('/department/<department_name>/')
def department_details(department_name):
    dept = Department.query.filter_by(name=department_name).first()
    vacancies = list(dept.vacancies)
    employees = list(dept.employees)
    positions = list(Position.query.all())
    return render_template('department.html', department_name=department_name,
                           vacancies=vacancies, employees=employees, positions=positions)


@app.route('/create_department/', methods=['POST'])
def create_department():
    try:
        department = Department(name=request.form.get('name'), description=request.form.get('description'))
        db.session.add(department)
        db.session.commit()
    except IntegrityError:
        flash('Department already exists')

    return redirect(url_for('index'))


@app.route('/delete_department/<department_name>/', methods=['POST'])
def delete_department(department_name):
    department = Department.query.filter_by(name=department_name).first()
    db.session.delete(department)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/create_position/', methods=['POST'])
def create_position():
    try:
        position = Position(name=request.form.get('name'), description=request.form.get('description'))
        db.session.add(position)
        db.session.commit()
    except IntegrityError:
        flash('Position already exists')

    return redirect(url_for('index'))


@app.route('/delete_position/<position_name>/', methods=['POST'])
def delete_position(position_name):
    try:
        position = Position.query.filter_by(name=position_name).first()
        db.session.delete(position)
        db.session.commit()
    except UnmappedInstanceError:
        flash('Object not found')
    return redirect(url_for('index'))


@app.route('/create_vacancy/', methods=['POST'])
def create_vacancy():
    position = Position.query.filter_by(name=request.form.get('vacancy_position_name')).first()
    department = Department.query.filter_by(name=request.form.get('department_name')).first()

    vacancy = Vacancy(position_id=position.id, department_id=department.id,
                      date_opened=to_timestamp(request.form.get('vacancy_date')))
    db.session.add(vacancy)
    db.session.commit()

    return redirect('/department/{}/'.format(department.name))


@app.route('/delete_vacancy/', methods=['POST'])
def delete_vacancy():
    vacancy = Vacancy.query.filter_by(id=request.form.get('vacancy_id')).first()
    db.session.delete(vacancy)
    db.session.commit()
    return redirect('/department/{}/'.format(request.form.get('department_name')))


if __name__ == '__main__':
    app.run(debug=True)
