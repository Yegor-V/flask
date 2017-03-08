function getCompanyData() {
    getAllDepartments();
    getAllPositions();
}


function showErrorMessage(message) {
    document.getElementById('errors').innerHTML = message
}


function getAllDepartments() {
    $.ajax('/api/department/', {
        success: function (data) {
            var deptsDiv = document.getElementById('departments');
            for (var i = 0, len = data.length; i < len; i++) {
                deptsDiv.appendChild(createSimpleHtmlDiv(data[i], 'department'));
            }
        },
        error: function () {
            showErrorMessage('error getting departments');
        }
    });
}


function getAllPositions() {
    $.ajax('/api/position/', {
        success: function (data) {
            var positionsDiv = document.getElementById('positions');
            for (var j = 0; j < data.length; j++) {
                positionsDiv.appendChild(createSimpleHtmlDiv(data[j], 'position'));
            }
        },
        error: function () {
            showErrorMessage('error getting positions');
        }
    });
}


function createSimpleHtmlDiv(dict, type) {
    var div = document.createElement('div');
    div.id = type + '-' + dict['id'];
    div.innerHTML = dict['name'] + ' ' + dict['description'];
    return div
}


function hideButtonShowForm() {
    document.getElementById('add-department').style.display = 'none';
    document.getElementById('add-department-form').style.display = 'block';
}


function hideFormShowButton() {
    document.getElementById('add-department').style.display = 'block';
    document.getElementById('department-name').value = '';
    document.getElementById('department-description').value = '';
    document.getElementById('add-department-form').style.display = 'none';
}


function sendCreateDepartmentForm() {

    var new_dept_name = document.getElementById('department-name').value;
    var new_dept_description = document.getElementById('department-description').value;

    $.ajax('/api/department/', {
        type: 'POST',
        data: {
            'name': new_dept_name,
            'description': new_dept_description
        },
        success: function (data) {
            hideFormShowButton();
            document.getElementById('departments').appendChild(createSimpleHtmlDiv(data['department'], 'department'));
            showErrorMessage('')
        },
        error: function (data) {
            hideFormShowButton();
            showErrorMessage('Failed to create department: ' + JSON.parse(data['responseText'])['error'])
        }
    })
}
