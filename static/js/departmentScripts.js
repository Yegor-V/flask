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
                'department_id': document.getElementById('department-id').textContent,
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
                newVacancyDeleteButton.textContent = 'Delete';
                newVacancyDeleteButton.id = 'vacancy-' + vacancyId + '-delete-button';
                newVacancyDeleteButton.className = 'vacancy-delete-button';

                var newVacancyHireButton = document.createElement('button');
                newVacancyHireButton.textContent = 'Hire';
                newVacancyHireButton.id = 'vacancy-' + vacancyId + '-hire-button';
                newVacancyHireButton.className = 'vacancy-hire-button';

                newVacancyDiv.appendChild(newVacancyName);
                newVacancyDiv.appendChild(openedWord);
                newVacancyDiv.appendChild(newVacancyDateOpened);
                newVacancyDiv.appendChild(newVacancyDeleteButton);
                newVacancyDiv.appendChild(newVacancyHireButton);
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
    if (clickedElementClass === 'vacancy-hire-button') {
        console.log('hiring new person');
    }
};

