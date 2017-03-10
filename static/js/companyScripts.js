/**Gets all info needed for company (index) page: all departments and all positions*/
function getCompanyData() {
    getAllDepartments();
    getAllPositions();
}

/**Show error message on company page*/
function showErrorMessage(message) {
    document.getElementById('errors').innerHTML = message
}

/**Get all departments and put them in divs inside 'departments' parent div*/
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

/**Get all positions and put them in divs inside 'positions' parent div*/
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

/**Create div with department/position*/
function createSimpleHtmlDiv(dict, type) {
    var div = document.createElement('div');
    div.id = type + '-' + dict['id'];
    div.innerHTML = dict['name'] + ' ' + dict['description'];
    var button = createDeleteButton(dict, type);
    div.appendChild(button);
    return div
}

/**Creates 'Delete' button (used by createSimpleHtmlDiv*/
function createDeleteButton(dict, type) {
    var button = document.createElement('button');
    button.id = type + '-' + dict['id'] + '-delete-button';
    button.className = 'delete-' + type + '-button';
    button.innerHTML = 'Delete';
    return button
}

/**Catch click event on departments div and if delete button is hit - delete corresponding item*/
var departmentsDiv = document.getElementById('departments');
departmentsDiv.onclick = function (event) {
    var clickedOnId = event['path'][0].id;
    var clickedOnClass = event['path'][0].className;

    if (clickedOnClass === 'delete-department-button'){
        var department_id = clickedOnId.split('-')[1];
        deleteItem(department_id, 'department')
    }
    if (clickedOnClass === 'delete-position-button'){
        var position_id = clickedOnId.split('-')[1];
        deleteItem(position_id, 'position')
    }

};


/**Send ajax delete-item request*/
function deleteItem(id, type) {
    console.log('Deleting ' + type + ' '+ id);
    $.ajax('/api/' + type + '/', {
        type: 'DELETE',
        data: {'id': id},
        success: function (data) {
            console.log(data);
            var parent_div = document.getElementById(type + 's');
            parent_div.removeChild(document.getElementById(type + '-' + id))
        },
        error: function (data) {
            console.log(data);
            showErrorMessage(data)
        }
    })
}


/**Hides add-department button and shows add-department form*/
function hideButtonShowForm() {
    document.getElementById('add-department').style.display = 'none';
    document.getElementById('add-department-form').style.display = 'block';
}


/**Hides add-department form and replaces with add-department button*/
function hideFormShowButton() {
    document.getElementById('add-department').style.display = 'block';
    document.getElementById('department-name').value = '';
    document.getElementById('department-description').value = '';
    document.getElementById('add-department-form').style.display = 'none';
}


/**Sends ajax create-department event*/
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
