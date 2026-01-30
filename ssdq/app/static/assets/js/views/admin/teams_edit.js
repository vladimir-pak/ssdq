const apiData = (endpoint, method="GET", body=undefined) => {
    let url = window.location.protocol + '//' + window.location.host + '/api/' + endpoint;
    var response;
    $.ajax({
        type: method,
        url: url,
        data: body,
        headers: {"X-CSRFToken": csrf_token},
        dataType: "json",
        encode: true,
        async: false
    }).done(function (data) {
        response = data;
        if (method == "PATCH") {
            Swal.fire({
                icon: 'success',
                title: 'Данные успешно обновлены',
                position: 'top-end',
                showConfirmButton: false,
                toast: true,
                timer: 5000
            });
        };
    }).fail(function (data) {
        Swal.fire({
            icon: 'error',
            title: data.responseText,
            position: 'top-end',
            showConfirmButton: false,
            toast: true,
            timer: 3000
        });
    });

    return response;
};

const cols = [
    {data: 'id'},
    {data: 'name'},
    {data: 'email'},
    {data: 'role_name'},
    {data: 'team_name'}
];

const setPageData = () => {
    let data = apiData("admin/teams/"+$("#id").val());
    data.sources.map(e => {
        $('#connId').append($('<option>', {
            value: e.name,
            text: e.description
        }));
    });
    $("#name").val(data.data.name);
    $("#display_name").val(data.data.display_name);
    $("#jira_project").val(data.data.jira_project);
    $("#description").val(data.data.description);
};

$("#update").on('click', function() {
    let formData = {
        name: $("#name").val(),
        description: $("#description").val(),
        display_name: $("#display_name").val(),
        jira_project: $("#jira_project").val()
    };
    let data = apiData("admin/teams/"+$("#id").val(), "PATCH", formData);
});


const modalToggle = () => {
    $('#modal-loading').modal('toggle');
};

const getSecrets = () => {
    var endpoint = 'db-conn';
    var team = $('#name').val();
    var connId = $('#connId').val();

    if (team && connId) {
        $.ajax({
            type: "GET",
            url: `/api/admin/${endpoint}?team=${team}&connId=${connId}`,
            dataType: "json",
            encode: true,
            async: true
        }).done(function (data) {
            // $('#host').val(data.response.host);
            // $('#port').val(data.response.port);
            // $('#dbName').val(data.response.db);
            $('#dbuser').val(data.response.username);
            // $('#password').val(data.response.password);
            $('#password').val("*********");
        }).fail(function (data) {
            Swal.fire({
                icon: 'error',
                title: 'Не удалось получить данные по подключениям',
                position: 'top-end',
                showConfirmButton: false,
                toast: true,
                timer: 5000
            });
        });
    };
};

$('#modalButton').on('click', function() {
    getSecrets()
});

$('#connId').on('change', function() {
    // $('#host').val('');
    // $('#port').val('');
    // $('#dbName').val('');
    $('#dbuser').val('');
    $('#password').val('');
    getSecrets();
});

$('#createDbConn').on('click', function() {
    modalToggle();
    var endpoint = 'db-conn';

    var formData = {
        team: $('#name').val(),
        conn_id: $('#connId').val(),
        // host: $('#host').val(),
        // port: $('#port').val(),
        // db_name: $('#dbName').val(),
        username: $('#dbuser').val(),
        password: $('#password').val()
    };
    // var successMessage = 'Источник успешно добавлен';

    // postAjax(endpoint, formData, successMessage);
    $.ajax({
        type: "POST",
        url: `/api/admin/${endpoint}`,
        data: formData,
        headers: {"X-CSRFToken": csrf_token},
        dataType: "json",
        encode: true,
        async: false
    }).done(function (data) {
        Swal.fire({
            icon: 'success',
            title: 'Источник успешно добавлен',
            position: 'top-end',
            showConfirmButton: false,
            toast: true,
            timer: 5000
        });
    }).fail(function (data) {
        Swal.fire({
            icon: 'error',
            title: 'Возникла непредвиденная ошибка',
            position: 'top-end',
            showConfirmButton: false,
            toast: true,
            timer: 5000
        });
    });
    
    setTimeout(modalToggle, 1000);
});

$(document).ready(
    function() {
        setPageData();
    }
);
