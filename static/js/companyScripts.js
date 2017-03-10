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
    var nameDiv = document.createElement('span');
    var descriptionDiv = document.createElement('span');
    div.id = type + '-' + dict['id'];
    nameDiv.innerHTML = dict['name'] + ' ';
    nameDiv.id = type + '-' + dict['id'] + '-name';
    descriptionDiv.innerHTML = dict['description'];
    descriptionDiv.id = type + '-' + dict['id'] + '-description';
    div.appendChild(nameDiv);
    div.appendChild(descriptionDiv);
    var deleteButton = createDeleteButton(dict, type);
    div.appendChild(deleteButton);
    div.appendChild(createEditButton(dict, type));
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

/**Creates 'Delete' button (used by createSimpleHtmlDiv*/
function createEditButton(dict, type) {
    var button = document.createElement('button');
    button.id = type + '-' + dict['id'] + '-edit-button';
    button.className = 'edit-' + type + '-button';
    button.innerHTML = 'Edit';
    return button
}

/**Catch click event on departments div and if delete button is hit - delete corresponding item*/
var departmentsDiv = document.getElementById('departments');
departmentsDiv.onclick = function (event) {
    var clickedOnId = event['path'][0].id;
    var clickedOnClass = event['path'][0].className;
    var department_id = clickedOnId.split('-')[1];

    if (clickedOnClass === 'delete-department-button'){
        deleteItem(department_id, 'department')
    }
    if (clickedOnClass === 'edit-department-button'){
        editDepartment(department_id, event)
    }
    if (clickedOnClass === 'send-edit-department'){
        sendEditDepartment(event)
    }
};


function editDepartment(department_id, event) {
    var old_name = document.getElementById('department-' + department_id + '-name').textContent;
    var old_description = document.getElementById('department-' + department_id + '-description').textContent;
    var divToEdit = document.getElementById('department-' + department_id);

    divToEdit.innerHTML = '';

    var new_name_input_label = document.createElement('label');
    new_name_input_label.for = 'department-new-name';
    new_name_input_label.textContent = 'New name: ';
    var new_name_input = document.createElement('input');
    new_name_input.id = 'department-' + department_id + '-new-name';
    new_name_input.name= 'new_name';
    new_name_input.type = 'text';
    new_name_input.value = old_name;
    var new_description_input_label = document.createElement('label');
    new_description_input_label.for = 'department-new-description';
    new_description_input_label.textContent = 'New description:';
    var new_description_input = document.createElement('input');
    new_description_input.id = 'department-' + department_id + '-new-description';
    new_description_input.name= 'new_description';
    new_description_input.type = 'text';
    new_description_input.value = old_description;

    var sendFormButton= document.createElement('button');
    sendFormButton.textContent = 'Edit';
    sendFormButton.className = 'send-edit-department';
    sendFormButton.id = 'send-department-' + department_id + '-edit-form';

    divToEdit.appendChild(new_name_input_label);
    divToEdit.appendChild(new_name_input);
    divToEdit.appendChild(new_description_input_label);
    divToEdit.appendChild(new_description_input);
    divToEdit.appendChild(sendFormButton);


}

function sendEditDepartment(event){
    var department_id = event['path'][1].id.split('-')[1];
    var new_name = document.getElementById('department-' + department_id + '-new-name').value;
    var new_description = document.getElementById('department-' + department_id + '-new-description').value;

    $.ajax('/api/department/',{
        type: 'PATCH',
        data: {
            'department_id': department_id,
            'new_name': new_name,
            'new_description': new_description
        },
        success: function () {
            var parentDiv = document.getElementById('department-' + department_id);
            parentDiv.innerHTML = '';
            var nameDiv = document.createElement('span');
            var descriptionDiv = document.createElement('span');
            nameDiv.innerHTML = new_name;
            nameDiv.id = 'department-' + department_id + '-name';
            descriptionDiv.innerHTML = new_description;
            descriptionDiv.id = 'department-' + department_id + '-description';
            parentDiv.appendChild(nameDiv);
            parentDiv.appendChild(descriptionDiv);
            var dict = {'id': department_id, 'name': new_name, 'description': new_description};
            var deleteButton = createDeleteButton(dict, 'department');
            parentDiv.appendChild(deleteButton);
            parentDiv.appendChild(createEditButton(dict, 'department'));
        },
        error: function (data) {
            console.log(data)
        }
    })
}

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
