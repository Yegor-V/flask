var emps =document.getElementById('emps');
emps.onclick = function (event) {
    if(event.target.id == 'emp-edit-button'){
        var currentDepartment = document.getElementById('current-department-id').textContent;
        var currentPosition = document.getElementById('current-position-id').textContent;

        var currentName = document.getElementById('emp-name').textContent;
        var currentSurname = document.getElementById('emp-surname').textContent;
        var currentEmail = document.getElementById('emp-email').textContent;
        var currentPhone = document.getElementById('emp-phone').textContent;
        var currentBirthDate = document.getElementById('emp-birth-date').textContent;
        var currentStartWorkDate = document.getElementById('emp-start-work-date').textContent;
        var currentIsDepartmentLeader = document.getElementById('emp-is-department-leader').textContent;

        emps.innerHTML = document.getElementById('employeeForm').innerHTML;

        var deptsSelect = document.getElementById('emp-department-input');

        $.ajax('/api/department/', {
            success: function (data) {
                console.log(data);
                for(var l=0, len=data.length; l<len; l++){
                    var option = document.createElement('option');
                    option.value = data[l]['id'];
                    option.textContent = data[l]['name'];
                    deptsSelect.appendChild(option);
                }
            },
            error: function () {
                console.log('error loading departments')
            }
        });

        var posSelect = document.getElementById('emp-position-input');
        console.log(posSelect);

        $.ajax('/api/position/', {
            success: function (data) {
                console.log(data);
                for(var s=0, len=data.length; s<len; s++){
                    var option = document.createElement('option');
                    option.value = data[s]['id'];
                    option.textContent = data[s]['name'];
                    posSelect.appendChild(option);
                }
            },
            error: function () {
                console.log('error loading positions')
            }
        });

        document.getElementById('emp-name-input').value = currentName;
        document.getElementById('emp-surname-input').value = currentSurname;
        document.getElementById('emp-email-input').value = currentEmail;
        document.getElementById('emp-phone-input').value = currentPhone;
        document.getElementById('emp-birth-date-input').value = currentBirthDate;
        document.getElementById('emp-start-work-date-input').value = currentStartWorkDate;
        document.getElementById('emp-is-department-leader-input').value = currentIsDepartmentLeader;
    }
    if(event.target.id == 'sendEditEmployeeForm'){
        $.ajax('/api/employee/', {
            type: 'PATCH',
            data: {
                'employee_id': document.getElementById('emp-id').textContent,
                'position_id': document.getElementById('emp-position-input').value,
                'department_id': document.getElementById('emp-department-input').value,
                'name': document.getElementById('emp-name-input').value,
                'surname': document.getElementById('emp-surname-input').value,
                'email': document.getElementById('emp-email-input').value,
                'phone': document.getElementById('emp-phone-input').value,
                'birth_date': document.getElementById('emp-birth-date-input').value,
                'start_work_date': document.getElementById('emp-start-work-date-input').value,
                'is_department_leader': document.getElementById('emp-is-department-leader-input').value
            },
            success: function (data) {
                emps.innerHTML = document.getElementById('employeeNOForm').innerHTML;

                console.log(emps);

                document.getElementById('emp-name').textContent = data['employee']['name'];
                document.getElementById('emp-surname').textContent = data['employee']['surname'];
                document.getElementById('emp-position').textContent = data['employee']['position']['name'];
                document.getElementById('emp-department').textContent = data['employee']['department']['name'];
                document.getElementById('emp-email').textContent = data['employee']['email'];
                document.getElementById('emp-phone').textContent = data['employee']['phone'];
                document.getElementById('emp-birth-date').textContent = data['employee']['birth_date'];
                document.getElementById('emp-start-work-date').textContent = data['employee']['start_work_date'];
                document.getElementById('emp-is-department-leader').textContent =
                    data['employee']['is_department_leader'];
            },
            error: function () {
                document.getElementById('emp-errors').innerHTML = 'Failed to update info :('
            }

        })
    }
};