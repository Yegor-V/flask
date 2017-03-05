from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
import time

from credentials import POSTGRES_CREDENTIALS

app = Flask(__name__)
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
    vacancies = db.relationship('Vacancy', backref='position', lazy='dynamic')
    employees = db.relationship('Employee', backref='position', lazy='dynamic')

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


@app.route('/department/<department_name>')
def department_details(department_name):
    positions = Department.query.filter_by(name=department_name).first().positions
    vacancies = []
    employees = []
    for position in positions:
        vacancies += position.vacancies
        employees += position.employees

    return render_template('department.html', department_name=department_name,
                           positions=positions, vacancies=vacancies, employees=employees)


# REST VIEWS
class DeleteDepartment(Resource):
    def post(self, department_name):
        department = Department.query.filter_by(name=department_name).first()
        if department:
            db.session.delete(department)
            db.session.commit()
            return {'success': 'department deleted'}
        else:
            return {'error': 'department NOT found'}, 404


class CreateDepartment(Resource):
    def post(self):
        department_name = request.form.get('name')
        department_description = request.form.get('description')

        if department_name is None:
            return {'error': 'department name is required'}, 400
        else:
            department = Department(name=department_name, description=department_description)
            db.session.add(department)
            db.session.commit()
            return {'success': 'department successfully created'}


class EditDepartment(Resource):
    def post(self):
        department_old_name = request.form.get('old_name')
        department_new_name = request.form.get('new_name')
        department_description = request.form.get('description')

        department = Department.query.filter_by(name=department_old_name).first()
        if department is None:
            return {'error': 'department not found'}, 404
        else:
            department.name = department_new_name
            department.description = department_description
            db.session.commit()
            return {'success': 'department data successfully updated'}


class CreatePosition(Resource):
    def post(self):
        position_name = request.form.get('position_name')
        position_description = request.form.get('position_description')
        department_name = request.form.get('department_name')

        department = Department.query.filter_by(name=department_name).first()
        if department is None:
            return {'error': 'department not found'}, 404
        else:
            position = Position(name=position_name, description=position_description, department_id=department.id)
            db.session.add(position)
            db.session.commit()
            return {'success': 'position created'}


class CreateVacancy(Resource):
    def post(self):
        position_id = request.form.get('position_id')
        print(position_id)
        print(type(position_id))
        position = Position.query.filter_by(id=position_id).first()
        if position is None:
            return {'error': 'position not found'}, 404
        else:
            vacancy = Vacancy(position_id=position_id)
            db.session.add(vacancy)
            db.session.commit()
            return {'success': 'vacancy created'}


class EmployeeView(Resource):
    def get(self):
        """
            Get info about employee
        """
        employee_id = request.args.get('employee_id')
        if not employee_id:
            return {'error': 'employee_id needed'}, 400
        else:
            employee = Employee.query.filter_by(id=employee_id).first()
            if employee is None:
                return {'error': 'employee not found'}, 404
            employee_department = employee.position.department.name
            print(employee_department)
            return render_template('employee.html', employee=employee, employee_department=employee_department)

    def post(self):
        """
            Hire new employee
        """
        name = request.form.get('name')
        surname = request.form.get('surname')
        vacancy_id = request.form.get('vacancy_id')

        vacancy = Vacancy.query.filter_by(id=vacancy_id).first()
        if vacancy is None:
            return {'error': 'vacancy not found or name or surname not specified'}, 400
        else:
            new_employee = Employee(name=name, surname=surname, position_id=vacancy.position.id)
            db.session.add(new_employee)
            db.session.delete(vacancy)
            db.session.commit()
            return {'success': 'hired!'}


api.add_resource(DeleteDepartment, '/delete_department/<department_name>')
api.add_resource(CreateDepartment, '/create_department')
api.add_resource(EditDepartment, '/edit_department')

api.add_resource(CreatePosition, '/create_position')
api.add_resource(CreateVacancy, '/create_vacancy')

api.add_resource(EmployeeView, '/employee/')

if __name__ == '__main__':
    app.run(debug=True)
