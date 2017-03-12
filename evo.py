import sys
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
import time

from sqlalchemy.exc import DataError, IntegrityError

from credentials import POSTGRES_CREDENTIALS, SECRET_KEY
from utils import to_timestamp, from_timestamp

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_CREDENTIALS
db = SQLAlchemy(app)
api = Api(app)

MODELS_LIST = ['Department', 'Position', 'Vacancy', 'Employee']
COMPANY_NAME = 'RANDOM'
DATABASE_STRING_LENGTH = 50


def get_object_dict(table_row_object):
    table_row_dict = table_row_object.__dict__
    del table_row_dict['_sa_instance_state']
    return table_row_dict


def get_all_positions():
    return [get_object_dict(p) for p in Position.query.all()]


def get_all_departments():
    return [get_object_dict(d) for d in Department.query.all()]


def get_department_vacancies(department_id):
    return [get_object_dict(v) for v in Vacancy.query.filter_by(department_id=department_id)]


def get_department_employees(department_id):
    return [get_object_dict(e) for e in Employee.query.filter_by(department_id=department_id)]


def make_new_department_leader(department_id, employee_id):
    employees = Employee.query.filter_by(department_id=department_id)
    for employee in employees:
        if employee.id != employee_id:
            employee.is_department_leader = False
        else:
            employee.is_department_leader = True
        db.session.add(employee)
    db.session.commit()  # TODO: Make in 1 query



class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(DATABASE_STRING_LENGTH), unique=True, nullable=False)
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
    name = db.Column(db.String(DATABASE_STRING_LENGTH), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    vacancies = db.relationship('Vacancy', backref='position', lazy='dynamic', cascade='delete')
    employees = db.relationship('Employee', backref='position', lazy='dynamic', cascade='delete')

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

    @property
    def str_date_opened(self):
        return from_timestamp(self.date_opened)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(DATABASE_STRING_LENGTH), nullable=False)
    surname = db.Column(db.String(DATABASE_STRING_LENGTH), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    email = db.Column(db.String(DATABASE_STRING_LENGTH))
    phone = db.Column(db.String(DATABASE_STRING_LENGTH))
    birth_date = db.Column(db.String(DATABASE_STRING_LENGTH))
    start_work_date = db.Column(db.BigInteger)
    is_department_leader = db.Column(db.Boolean, default=False)

    def __init__(self, name, surname, position_id, department_id,
                 email=None, phone=None, birth_date=None,
                 start_work_date=int(time.time()), is_department_leader=False):
        self.name = name
        self.surname = surname
        self.position_id = position_id
        self.department_id = department_id
        self.email = email
        self.phone = phone
        self.birth_date = birth_date
        self.start_work_date = start_work_date
        self.is_department_leader = is_department_leader

    def __repr__(self):
        return 'Employee {} {}'.format(self.name, self.surname)


@app.route('/')
def company_view():
    return render_template('company.html', company_name=COMPANY_NAME)


@app.route('/department/<department_name>/')
def department_view(department_name):
    department = Department.query.filter_by(name=department_name).first()
    return render_template('department.html', department=department)


@app.route('/employee/<employee_id>/')
def employee_view(employee_id):
    employee = Employee.query.filter_by(id=employee_id).first()
    return render_template('employee.html', employee=employee, employee_birth_date=from_timestamp(employee.birth_date),
                           employee_start_work_date=from_timestamp(employee.start_work_date))


class ResourceCRUD(Resource):
    model_name = None

    @classmethod
    def delete(cls):
        """
        Deletes item (department, position, vacancy or employee) by id.
        :return: success/error json
        """
        if cls.model_name is None:
            raise NotImplementedError
        item_id = request.form.get('id')
        if not item_id:
            return {'error': 'id required'}, 400
        else:
            class_ = getattr(sys.modules[__name__], cls.model_name)
            try:
                item = class_.query.filter_by(id=item_id).first()
                if not item:
                    return {'error': '{} with specified id not found'.format(cls.model_name)}, 404
                else:
                    db.session.delete(item)
                    db.session.commit()
                    return {'success': '{} {} deleted'.format(cls.model_name, item.id)}
            except DataError:
                return {'error': 'id must be int'}, 400


class DepartmentApi(ResourceCRUD):
    model_name = 'Department'

    @staticmethod
    def get():
        """
        :return: All departments json or particular department details if id is specified
        """
        department_id = request.args.get('department_id')
        if not department_id:
            return get_all_departments()
        else:
            try:
                department = Department.query.filter_by(id=department_id).first()
                if department:
                    return get_object_dict(department)
                else:
                    return {'error': 'department not found'}, 404
            except DataError:
                return {'error': 'department_id must be a number'}, 400

    @staticmethod
    def post():
        """
        Saves new department to db. name and description are needed. Name is unique.
        :return: success/error json
        """
        name = request.form.get('name')
        description = request.form.get('description')

        if not name or not description:
            return {'error': 'name and description required'}, 400
        elif len(name) > DATABASE_STRING_LENGTH:
            return {'error': 'name and description must not be longer then {} symbols'.format(
                DATABASE_STRING_LENGTH)}, 400
        else:
            try:
                department = Department(name=name, description=description)
                db.session.add(department)
                db.session.commit()
                return {'success': 'department created', 'department': {
                    'name': department.name, 'id': department.id, 'description': department.description}}, 201
            except IntegrityError:
                return {'error': 'department with this name already exists'}, 400

    @staticmethod
    def patch():
        """
        Updates department name/description. department_id is needed.
        :return: success/error json
        """
        department_id = request.form.get('department_id')
        new_name = request.form.get('new_name')
        new_description = request.form.get('new_description')
        if not department_id:
            return {'error': 'department_id is required'}, 400
        elif not new_name and not new_description:
            return {'error': 'at least one of new_name and new_description needed'}, 400
        elif len(new_name) > DATABASE_STRING_LENGTH:
            return {'error': 'new_name too long'}, 400
        else:
            try:
                department = Department.query.filter_by(id=department_id).first()
                if not department:
                    return {'error': 'department with specified id not found'}, 404
                if new_name:
                    department.name = new_name
                if new_description:
                    department.description = new_description
                db.session.commit()
                return {'success': 'department updated successfully'}

            except DataError:
                return {'error': 'department_id must be string'}, 400


class PositionApi(ResourceCRUD):
    model_name = 'Position'

    @staticmethod
    def get():
        """
        :return: All positions json
        """
        return get_all_positions()

    @staticmethod
    def post():
        """
        Saves new position to db. name and description are needed. Name is unique.
        :return: success/error json
        """
        name = request.form.get('name')
        description = request.form.get('description')

        if not name or not description:
            return {'error': 'name and description required'}, 400
        elif len(name) > DATABASE_STRING_LENGTH:
            return {'error': 'name must not be longer then {} symbols'.format(DATABASE_STRING_LENGTH)}, 400
        else:
            try:
                position = Position(name=name, description=description)
                db.session.add(position)
                db.session.commit()
                return {'success': 'position created', 'position': {
                    'id': position.id,
                    'name': position.name,
                    'description': position.description
                }}, 201
            except IntegrityError:
                return {'error': 'position with this name already exists'}, 400

    @staticmethod
    def patch():
        """
        Updates position name/description.
        :return: success/error json
        """
        position_id = request.form.get('position_id')
        new_name = request.form.get('new_name')
        new_description = request.form.get('new_description')
        if not position_id:
            return {'error': 'position_id is required'}, 400
        elif not new_name and not new_description:
            return {'error': 'at least one of new_name and new_description needed'}, 400
        else:
            try:
                position = Position.query.filter_by(id=position_id).first()
                if not position:
                    return {'error': 'position with specified id not found'}, 404
                if new_name:
                    position.name = new_name
                if new_description:
                    position.description = new_description
                db.session.commit()
                return {'success': 'position updated'}

            except DataError:
                return {'error': 'position_id must be string'}, 400


class VacancyApi(ResourceCRUD):
    model_name = 'Vacancy'

    @staticmethod
    def get():
        """
        :return: All vacancies json of current department. department id is needed in request.
        """
        department_id = request.args.get('department_id')
        if not department_id:
            return {'error': 'department_id id required'}, 400
        else:
            try:
                return get_department_vacancies(department_id)
            except DataError:
                return {'error': 'department_id must be int'}, 400

    @staticmethod
    def post():
        """
        Opens vacancy in current department. department_id and position_id are needed.
        date_opened is optional (defaults to now)
        :return: success/error json
        """
        department_id = request.form.get('department_id')
        position_id = request.form.get('position_id')
        date_opened = request.form.get('date_opened')

        if not position_id or not department_id:
            return {'error': 'position_id and department_id required'}, 400
        else:
            try:
                department = Department.query.filter_by(id=department_id).first()
                position = Position.query.filter_by(id=position_id).first()
            except DataError:
                return {'error': 'department_id and position_id must be ints'}, 400

            if not department or not position:
                return {'error': 'department or position not found'}, 404

            else:
                if date_opened:
                    try:
                        date_opened = to_timestamp(date_opened)
                        vacancy = Vacancy(department_id=department_id, position_id=position_id, date_opened=date_opened)
                    except ValueError:
                        return {'error': 'date_opened must be in format mm/dd/yyyy'}, 400
                else:
                    vacancy = Vacancy(department_id=department_id, position_id=position_id)
                db.session.add(vacancy)
                db.session.commit()
                return {
                    'success': 'vacancy created',
                    'vacancy': {
                        'id': vacancy.id, 'department_id': vacancy.department_id,
                        'date_opened': vacancy.str_date_opened,
                        'position': {'id': vacancy.position.id, 'name': vacancy.position.name}
                    }
                }

    @staticmethod
    def patch():
        """
        Updates vacancy data.
        :return: success/error json
        """
        vacancy_id = request.form.get('vacancy_id')
        new_department_id = request.form.get('new_department_id')
        new_position_id = request.form.get('new_position_id')
        new_date_opened = request.form.get('new_date_opened')

        if not vacancy_id or not all((new_department_id, new_position_id, new_date_opened)):
            return {
                'error': 'vacancy_id and at least one of new_department_id, new_position_id, new_date_opened needed'
            }, 400
        else:
            try:
                vacancy = Vacancy.query.filter_by(id=vacancy_id).first()
                if not vacancy:
                    return {'error': 'vacancy not found'}, 404
                if new_department_id:
                    vacancy.department_id = new_department_id
                if new_position_id:
                    vacancy.position_id = new_position_id
                if new_date_opened:
                    try:
                        vacancy.date_opened = to_timestamp(new_date_opened)
                    except ValueError:
                        return {'error': 'date_opened must be in format mm/dd/yyyy'}, 400
                db.session.add(vacancy)
                db.session.commit()
                return {
                    'success': 'vacancy updated',
                    'vacancy': {
                        'id': vacancy.id,
                        'date_opened': vacancy.date_opened,
                        'department': {'id': vacancy.department_id, 'name': vacancy.department.name},
                        'position': {'id': vacancy.position_id, 'name': vacancy.position.name}
                    }
                }
            except (DataError, IntegrityError):
                return {'error': 'bad department_id, position_id, vacancy_id'}


class EmployeeApi(ResourceCRUD):
    model_name = 'Employee'

    @staticmethod
    def get():
        """
        :return: All employees of current department json. Needs department_id parameter.
        """
        department_id = request.args.get('department_id')
        employee_id = request.args.get('employee_id')

        if not department_id and not employee_id:
            return {'error': 'department_id or/and employee_id is required'}, 400

        if employee_id:
            try:
                employee = Employee.query.filter_by(id=employee_id).first()
                if not employee:
                    return {'error': 'employee with specified employee_id not found'}, 404
                else:
                    return get_object_dict(employee)
            except DataError:
                return {'error': 'employee_id must be a string'}, 400

        elif department_id:
            try:
                department = Department.query.filter_by(id=department_id).first()
                if not department:
                    return {'error': 'department with specified id not found'}, 404
                else:
                    return get_department_employees(department_id)
            except DataError:
                return {'error': 'department_id must be a string'}, 400

    @staticmethod
    def post():
        """
        Creates new db instance of Employee. position_id, department_id, name and surname args are needed.
        Other info (email, phone, birth_date, start_work_date and is_department_leader) is optional.
        If start_work_date is not set -> will be set to now.
        If is_department_leader is not set -> will be set to False.
        :return: success/error json
        """
        vacancy_id = request.form.get('vacancy_id')
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        birth_date = to_timestamp(request.form.get('birth_date'))
        start_work_date = to_timestamp(request.form.get('start_work_date'))
        is_department_leader = request.form.get('is_department_leader')

        if not all((vacancy_id, name, surname)):
            return {'error': 'vacancy_id, name, surname required'}, 400
        else:
            try:
                vacancy = Vacancy.query.filter_by(id=vacancy_id).first()
                employee = Employee(position_id=vacancy.position.id, department_id=vacancy.department.id,
                                    name=name, surname=surname, email=email, phone=phone, birth_date=birth_date,
                                    start_work_date=start_work_date, is_department_leader=is_department_leader)
                db.session.add(employee)
                db.session.commit()
                return {'success': 'employee created',
                        'employee': {'id': employee.id, 'name': employee.name,
                                     'surname': employee.surname, 'position': employee.position.name}}
            except Exception as e:
                return {'error': 'failed to create employee: {}'.format(e)}, 400

    @staticmethod
    def patch():
        """
        Updates employee's personal info.
        Just gets all updated info from request data and updates table row.
        :return: success/error json
        """
        employee_id = request.form.get('employee_id')

        new_name = request.form.get('name')
        new_surname = request.form.get('surname')
        new_department_id = request.form.get('department_id')
        new_position_id = request.form.get('position_id')
        new_phone = request.form.get('phone')
        new_email = request.form.get('email')
        new_birth_date = to_timestamp(request.form.get('birth_date'))
        new_start_work_date = to_timestamp(request.form.get('start_work_date'))
        new_is_department_leader = request.form.get('is_department_leader')

        if not employee_id:
            return {'error': 'employee_id is required'}, 400

        try:
            employee = Employee.query.filter_by(id=employee_id).first()
            if not employee:
                return {'error': 'employee {} not found'.format(employee_id)}, 400
            else:
                try:
                    employee.name = new_name
                    employee.surname = new_surname
                    employee.department_id = new_department_id
                    employee.position_id = new_position_id
                    employee.phone = new_phone if new_phone else ''
                    employee.email = new_email if new_email else ''
                    employee.birth_date = new_birth_date if new_birth_date else 0
                    employee.start_work_date = new_start_work_date if new_start_work_date else 0
                    if new_is_department_leader and new_is_department_leader in (True, 'true', 'True', 'yes'):
                        make_new_department_leader(new_department_id, employee_id)
                    db.session.add(employee)
                    db.session.commit()
                    return {'success': 'employee info updated',
                            'employee': {
                                'id': employee.id,
                                'department': {'id': employee.department.id, 'name': employee.department.name},
                                'position': {'id': employee.position.id, 'name': employee.position.name},
                                'name': employee.name,
                                'surname': employee.surname,
                                'email': employee.email,
                                'phone': employee.phone,
                                'birth_date': from_timestamp(employee.birth_date),
                                'start_work_date': from_timestamp(employee.start_work_date),
                                'is_department_leader': employee.is_department_leader
                            }}
                except Exception as e:
                    return {'error': e}
        except DataError:
            return {'error': 'employee_id must be int'}, 400

api.add_resource(DepartmentApi, '/api/department/')
api.add_resource(PositionApi, '/api/position/')
api.add_resource(VacancyApi, '/api/vacancy/')
api.add_resource(EmployeeApi, '/api/employee/')


if __name__ == '__main__':
    app.run(debug=True)
