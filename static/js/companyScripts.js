function getCompanyData() {
    $.ajax('/api/company/', {
        success: function (data) {
            document.getElementById('companyName').innerHTML = data['company_name'];

            var depts_div = document.getElementById('departments');
            for (var i = 0; i < data['departments'].length; i++) {
                var dept_html = document.createElement('div');
                dept_html.id = 'department-' + data['departments'][i]['name'];
                dept_html.innerHTML = data['departments'][i]['id'] + ' ' + data['departments'][i]['name'] +
                    ' ' + data['departments'][i]['description'] + '<br>';
                depts_div.appendChild(dept_html);
            }

            var positions_div = document.getElementById('positions');
            for (var j = 0; j < data['positions'].length; j++) {
                var positions_html = document.createElement('div');
                positions_html.id = 'position-' + data['positions'][j]['name'];
                positions_html.innerHTML = data['positions'][j]['id'] + ' ' + data['positions'][j]['name'] +
                    ' ' + data['positions'][j]['description'] + '<br>';
                positions_div.appendChild(positions_html);
            }


        },
        error: function (data) {
            console.log('Failed to get data from /api/company/')
        }
    })

}

