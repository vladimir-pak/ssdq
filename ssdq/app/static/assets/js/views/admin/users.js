const apiData = (endpoint) => {
    let url = window.location.protocol + '//' + window.location.host + '/api/' + endpoint;
    var response;
    $.ajax({
        type: "GET",
        url: url,
        //data: body,
        dataType: "json",
        encode: true,
        async: false
    }).done(function (data) {
        response = data;
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

const setPageData = () => {
    let data = apiData("admin/users");
    data.teams.map(e => {
        $('#team_id').append($('<option>', {
            value: e.id,
            text: e.name,
            selected: e.id == userTeamId ? true : false
        }));
    });
    data.roles.map(e => {
        $('#role').append($('<option>', {
            value: e.id,
            text: e.name
        }));
    });
};

/* DataTable start */
const columns = [
    {data: 'id'},
    {data: 'name'},
    {data: 'email'},
    {data: 'role_name'},
    {data: 'team_name'}
];

const attr = ['id', 'name', 'email'];
const toggleActiveList = ['update', 'hardRemove'];

var dataTab = new dataTableHandler(
    'users',
    columns,
    `api/admin/users?teamId=${userTeamId}`,
    'update',
    toggleActiveList
);
dataTab.setTableDelay();

const customFunc = () => {
    let id = $("#id").val();
    let data = apiData("admin/users/"+id);

    $("#role > option").each(function() {
        $(this).prop("selected", false);
        if (this.value == data.role_id) {
            $(this).prop("selected", true);
        };
    });

    $("#team_id > option").each(function() {
        $(this).prop("selected", false);
        if (this.value == data.team_id) {
            $(this).prop("selected", true);
        };
    });
};

dataTab.setRowHandler(attr, customFunc);

var myTable = dataTab.getTable();

/* DataTable end */

/* Ajax to back for CRUD (start) */
const requiredAttributes = ['name', 'email', 'role', 'team_id'];

var postRequests = new postRequests(
    'Users', // entity name
    'Пользователь', // russian entity name
    ['id', 'name', 'email', 'role', 'team_id'] // list of inputs (create form to http request)
);

$('#update, #hardRemove').on('click', function() {
    if (!postRequests.verifyFileds(requiredAttributes)) {
        return;
    };

    postRequests.postRequest(
        `api/admin/users/${$("#id").val()}`, 
        this.id
    );
    dataTab.resetButtons(attr);
    myTable.draw();
});

// $('#team_id').on('change', function() {
//     team_id = $(this).val();
//     myTable.ajax.url(`/api/admin/users?teamId=${team_id}`);
//     toggleActiveList.forEach((e) => {dataTab.setHidden(e)});
//     myTable.ajax.reload();
//     //myTable.draw();
// });

$(document).ready(
    function() {
        setPageData();
    }
);
