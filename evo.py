from flask import Flask, redirect, render_template, request, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
import time
from sqlalchemy.exc import IntegrityError

from credentials import POSTGRES_CREDENTIALS, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_CREDENTIALS
db = SQLAlchemy(app)
api = Api(app)


# MODELS
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    positions = db.relationship('Position', backref='department', lazy='dynamic', cascade='delete')

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return 'Department {}'.format(self.name)


class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    vacancies = db.relationship('Vacancy', backref='position', lazy='dynamic', cascade='delete')
    employees = db.relationship('Employee', backref='position', lazy='dynamic', cascade='delete')

    def __init__(self, name, description, department_id):
        self.name = name
        self.description = description
        self.department_id = department_id

    def __repr__(self):
        return 'Position {}'.format(self.name)


class Vacancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))
    date_opened = db.Column(db.BigInteger, nullable=False)

    def __init__(self, position_id, date_opened=None):
        self.position_id = position_id
        if date_opened is None:
            date_opened = int(time.time())
        self.date_opened = date_opened

    def __repr__(self):
        return 'Vacancy for {}'.format(self.position.name)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))
    email = db.Column(db.String(80))
    phone = db.Column(db.String(80))
    birth_date = db.Column(db.String(80))
    start_work_date = db.Column(db.BigInteger)
    is_department_leader = db.Column(db.Boolean, default=False)

    def __init__(self, name, surname, position_id, start_work_date=None):
        self.name = name
        self.surname = surname
        self.position_id = position_id
        if start_work_date is None:
            start_work_date = int(time.time())
        self.start_work_date = start_work_date

    def __repr__(self):
        return 'Employee {} {}'.format(self.name, self.surname)


# REGULAR VIEWS
@app.route('/')
def index():
    all_departments = Department.query.all()
    return render_template('index.html', depts=all_departments)


@app.route('/department/<department_name>/')
def department_details(department_name):
    positions = Department.query.filter_by(name=department_name).first().positions
    vacancies = []
    employees = []
    for position in positions:
        vacancies += position.vacancies
        employees += position.employees

    return render_template('department.html', department_name=department_name,
                           positions=positions, vacancies=vacancies, employees=employees)


@app.route('/delete_department/<department_name>/', methods=['POST'])
def delete_department(department_name):
    department = Department.query.filter_by(name=department_name).first()
    db.session.delete(department)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/create_department/', methods=['POST'])
def create_department():
    name = request.form.get('name')
    description = request.form.get('description')

    if not name or not description:
        return redirect('index')

    try:
        department = Department(name=request.form.get('name'), description=request.form.get('description'))
        db.session.add(department)
        db.session.commit()
    except IntegrityError:
        flash('Name already exists')
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route('/create_position/', methods=['POST'])
def create_position():
    name = request.form.get('name')
    description = request.form.get('description')
    department_name = request.form.get('department_name')

    if not name or not description or not department_name:
        flash('Error creating position')
        return redirect('index')
    else:
        dept = Department.query.filter_by(name=department_name).first()
        position = Position(name=name, description=description, department_id=dept.id)
        db.session.add(position)
        db.session.commit()
        return redirect('/department/{}/'.format(department_name))


@app.route('/delete_position/', methods=['POST'])
def delete_position():
    position_id = request.form.get('position_id')
    department_name = request.form.get('department_name')
    position = Position.query.filter_by(id=position_id).first()
    if not position_id or not department_name or not position:
        flash('Error deleting position')
        return redirect('index')
    else:
        db.session.delete(position)
        db.session.commit()
        return redirect('/department/{}/'.format(department_name))





if __name__ == '__main__':
    app.run(debug=True)
