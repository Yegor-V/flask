document.getElementById('vacancies').onclick = function (event) {

    var clickedElementClass = event['path'][0].className;
    var clickedElementId = event['path'][0].id;
    var vacanciesDiv = document.getElementById('vacancies');

    if (clickedElementClass === 'vacancy-delete-button') {
        var vacancyId = event['path'][0]['id'].split('-')[1];
        $.ajax('/api/vacancy/', {
            type: 'DELETE',
            data: {'id': vacancyId},
            success: function () {
                vacanciesDiv.removeChild(document.getElementById('vacancy-' + vacancyId));
            },
            error: function () {
                document.getElementById('vacancy-error').innerHTML = 'error deleting vacancy'
            }
        });


    }

    if (clickedElementId === 'open-vacancy') {

        vacanciesDiv.removeChild(document.getElementById('open-vacancy'));

        var newVacancyPositionLabel = document.createElement('label');
        newVacancyPositionLabel.for = 'new-vacancy-position';
        newVacancyPositionLabel.textContent = 'Position: ';
        newVacancyPositionLabel.id = 'new-vacancy-position-label';

        var newVacancyPosition = document.createElement('select');
        newVacancyPosition.id = 'new-vacancy-position';
        newVacancyPosition.name = 'position_id';

        $.ajax('/api/position/', {
            success: function (data) {
                for (var k = 0, len = data.length; k < len; k++) {
                    var option = document.createElement('option');
                    option.value = data[k]['id'];
                    option.textContent = data[k]['name'];
                    newVacancyPosition.appendChild(option);
                }
            },
            error: function () {
                console.log('failed to get positions')
            }
        });


        var newVacancyDateOpenedLabel = document.createElement('label');
        newVacancyDateOpenedLabel.for = 'new-vacancy-date-opened';
        newVacancyDateOpenedLabel.textContent = 'Date opened: ';
        newVacancyDateOpenedLabel.id = 'new-vacancy-date-opened-label';

        var newVacancyDateOpened = document.createElement('input');
        newVacancyDateOpened.type = 'text';
        newVacancyDateOpened.name = 'date_opened';
        newVacancyDateOpened.id = 'new-vacancy-date-opened';

        var sendNewVacancyButton = document.createElement('button');
        sendNewVacancyButton.id = 'send-new-vacancy-button';
        sendNewVacancyButton.textContent = 'Open Vacancy';

        vacanciesDiv.appendChild(newVacancyPositionLabel);
        vacanciesDiv.appendChild(newVacancyPosition);
        vacanciesDiv.appendChild(newVacancyDateOpenedLabel);
        vacanciesDiv.appendChild(newVacancyDateOpened);
        vacanciesDiv.appendChild(sendNewVacancyButton);

        $("#new-vacancy-date-opened").datepicker();

    }

    if (clickedElementId === 'send-new-vacancy-button') {
        $.ajax('/api/vacancy/', {
            type: 'POST',
            data: {
                'position_id': document.getElementById('new-vacancy-position').value,
                'department_id': document.getElementById('department-id').textContent.replace(/\s+/g, ''),
                'date_opened': document.getElementById('new-vacancy-date-opened').value
            },
            success: function (data) {
                var parentDiv = document.getElementById('vacancies');

                var vacancyId = data['vacancy']['id'];

                var createVacancyButton = document.createElement('button');
                createVacancyButton.id = 'open-vacancy';
                createVacancyButton.textContent = 'Open Vacancy';

                var newVacancyDiv = document.createElement('div');
                newVacancyDiv.className = 'vacancy';
                newVacancyDiv.id = 'vacancy-' + vacancyId;

                var newVacancyName = document.createElement('span');
                newVacancyName.id = 'vacancy-' + vacancyId + '-name';
                newVacancyName.textContent = data['vacancy']['position']['name'];

                var openedWord = document.createTextNode(' Opened: ');

                var newVacancyDateOpened = document.createElement('span');
                newVacancyDateOpened.id = 'vacancy-' + vacancyId + '-date-opened';
                newVacancyDateOpened.textContent = data['vacancy']['date_opened'];

                var newVacancyDeleteButton = document.createElement('button');
                newVacancyDeleteButton.textContent = 'Close Vacancy';
                newVacancyDeleteButton.id = 'vacancy-' + vacancyId + '-delete-button';
                newVacancyDeleteButton.className = 'vacancy-delete-button';

                newVacancyDiv.appendChild(newVacancyName);
                newVacancyDiv.appendChild(openedWord);
                newVacancyDiv.appendChild(newVacancyDateOpened);
                newVacancyDiv.appendChild(newVacancyDeleteButton);
                parentDiv.appendChild(newVacancyDiv);
                parentDiv.appendChild(createVacancyButton);

                parentDiv.removeChild(document.getElementById('new-vacancy-date-opened'));
                parentDiv.removeChild(document.getElementById('send-new-vacancy-button'));
                parentDiv.removeChild(document.getElementById('new-vacancy-position'));
                parentDiv.removeChild(document.getElementById('new-vacancy-position-label'));
                parentDiv.removeChild(document.getElementById('new-vacancy-date-opened-label'));

                document.getElementById('vacancy-error').innerHTML = ''
            },
            error: function () {
                document.getElementById('vacancy-error').innerHTML = 'error creating vacancy'
            }
        })
    }
};

document.getElementById('employees').onclick = function (event) {
    var employeeClickedElement = event.target;
    if (employeeClickedElement.id === 'hire-new-employee-button') {
        document.getElementById('hire-new-employee-div').innerHTML =
            document.getElementById('invisibleEmployeeForm').innerHTML;
        var vacancySelect = document.getElementById('new-employee-vacancy');
        var departmentVacancies = document.getElementsByClassName('vacancy');
        for (var m = 0, len = departmentVacancies.length; m < len; m++) {
            var option = document.createElement('option');
            option.value = departmentVacancies[m].id.split('-')[1];
            option.textContent = departmentVacancies[m].childNodes[1].textContent +
                ' ' + departmentVacancies[m].childNodes[3].textContent;
            vacancySelect.appendChild(option);
        }

        $("#new-employee-birth-date").datepicker();
        $("#new-employee-start-work-date").datepicker();

        $("#hire-new-employee-form").submit(function (event) {
            event.preventDefault();

            document.getElementById('name-error').innerHTML = '';
            document.getElementById('surname-error').innerHTML = '';
            document.getElementById('email-error').innerHTML = '';
            document.getElementById('phone-error').innerHTML = '';
            document.getElementById('birth-date-error').innerHTML = '';
            document.getElementById('start-work-date-error').innerHTML = '';

            var name = document.getElementById('new-employee-name').value;
            if(name === ''){
                document.getElementById('name-error').innerHTML = 'name is required';
                return
            }

            var surname = document.getElementById('new-employee-surname').value;
            if(surname === ''){
                document.getElementById('surname-error').innerHTML = 'surname is required';
                return
            }

            $.ajax('/api/employee/', {
                type: 'POST',
                data: {
                    'vacancy_id': document.getElementById('new-employee-vacancy').value,
                    'name': name,
                    'surname': document.getElementById('new-employee-surname').value,
                    'email': document.getElementById('new-employee-email').value,
                    'birth_date': document.getElementById('new-employee-birth-date').value,
                    'start_work_date': document.getElementById('new-employee-start-work-date').value,
                    'is_department_leader': document.getElementById('new-employee-is-department-leader').value
                },
                success: function (data) {
                    var buttonIsBack = document.createElement('button');
                    buttonIsBack.id = 'hire-new-employee-button';
                    buttonIsBack.textContent = 'Hire New Employee';

                    var hireDiv = document.getElementById('hire-new-employee-div');
                    hireDiv.innerHTML = '';
                    hireDiv.appendChild(buttonIsBack);

                    var employeeDiv = document.createElement('div');
                    employeeDiv.className = 'employee';
                    employeeDiv.id = 'employee-' + data['employee']['id'];

                    var employeeLink = document.createElement('a');
                    employeeLink.href = '/employee/' + data['employee']['id'] + '/';
                    employeeLink.textContent = data['employee']['name'] + ' ' + data['employee']['surname'] +
                        ' (' + data['employee']['position'] + ')';

                    employeeDiv.appendChild(employeeLink);
                    document.getElementById('employees').appendChild(employeeDiv);

                    hireDiv.parentNode.insertBefore(employeeDiv, hireDiv)

                },
                error: function () {
                    document.getElementById('employee-error').innerHTML = 'error hiring new employee'
                }
            })
        });

    }
};
