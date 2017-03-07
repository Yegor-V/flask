
function getCompanyData() {
    $.ajax('/api/company/', {
        success: function (data) {
            document.getElementById('companyName').innerHTML = data['company_name'];
            document.getElementById('departments').innerHTML = data['departments'];
            document.getElementById('positions').innerHTML = data['positions'];
        },
        error: function (data) {
            console.log('Failed to get data from /api/company/')
        }
    })

}

