const modalToggle = () => {
    $('#modal-loading').modal('toggle');
};

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

const setHidden = (element) => {
    $(`#${element}`).prop('hidden', true);
    $(`#${element}`).css('display', 'none');
    return;
};

const removeHidden = (element) => {
    $(`#${element}`).prop('hidden', false);
    $(`#${element}`).css('display', 'inline-block');
    return;
};

var data = apiData(`report/${controlId}/edit/${wfId}`);
var columnList = data.columns;
$("#generalJiraIssue").html(data.jira_issue);
$("#generalJiraIssue").attr("href", jiraUrl + data.jira_issue);
data.error_reason.map(e => {
    $('#error_reason').append($('<option>', {
        value: e.id,
        text: e.name
    }));
});
columnList.map((e) => {
    $('#report>thead>tr').append(`<th class="sorting">${e}</th>`);
});

/* DataTable start */
const columns = [
    {
        data: 'rowId'
    },
    {
        data: 'jira_issue',
        render: function (data) {
            return data ? `<a href="${jiraUrl + data}">${data}</a>` : null;
        }
    },
    {
        data: 'error_reason'
    },
    {
        data: 'json',
        render: function (data) {
            return data ? data['error_origin'] : null;
        }
    },
    {data: 'xk'}
];

columnList.map((e) => {columns.push(
    {
        data: e,
        render: function (data) {
            return `<plaintext style="margin: 0 0 0 0;">${data}`
        }
    }
)});

const attr = ['xk', 'jira_issue', 'error_origin', 'error_reason', 'xk'];
const toggleActiveList = ['add', 'hardRemove', 'createTask'];

var myTable = $("#report").DataTable({
    language: {
        url: '/static/assets/ru.json'
    },
    processing: true,
    serverSide: true,
    serverMethod: 'post',
    ajax: {
        url: `${window.location.protocol + '//' + window.location.host}/api/report/${controlId}/edit/${wfId}`,
        headers: {"X-CSRFToken": csrf_token},
        dataSrc: function ( json ) {
            $('#report tbody input[type="checkbox"]:checked').each(function() {
                $(this).prop("checked", false);
            });
            buttonsToggle();
            return json.aaData;
        }
    },
    lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    searching: false,
    sort: true,
    order: [4,'asc'],
    aaSorting: ['asc', 'desc'],
    autoWidth: false,
    responsive: false,
    columns: columns,
    oLanguage: {
        sProcessing: `<div class="spinner-border text-success" style="width: 6rem; height: 6rem;"></div>`,
        sEmptyTable: "Нет данных"
    },
    columnDefs: [{
        'targets': 0,
        'searchable': false,
        'orderable': false,
        'className': 'dt-body-center',
        'render': function (data, type, full, meta){
            return '<input type="checkbox" name="rowId[]" value="' + $('<div/>').text(data).html() + '">';
        }
    }],
});

const setTableDelay = (table) => {
    const delay = (callback, ms) => {
        var timer = 0;
        return function () {
            var context = this, args = arguments;
            clearTimeout(timer);
            timer = setTimeout(function () {
                callback.apply(context, args);
            }, ms || 0);
        };
    };

    $('.dataTables_filter input')
    .unbind() // Unbind previous default bindings
    .bind('input', (delay(function (e) { // Bind our desired behavior
        table.search($(this).val()).draw();
        return;
    }, 400))); // Set delay in milliseconds
};

// Mapping DataTable's attributes
const attributesMap = {
    0: "xk",
    1: "jira_issue",
    // 2: "error_origin",
    // 3: "error_reason",
    4: "xk"
};

const toggleButtons = ["add"];

const validateJiraTask = (task) => {
    const pattern = /^\w*-\d*$/g;
    return task.match(pattern);
};

const buttonsToggle = () => {
    if ($('#report tbody input[type="checkbox"]:checked').length) {
        toggleButtons.forEach(el => removeHidden(el));
        setHidden("addAll");
        let jiraTask;
        myTable.$('input[type="checkbox"]:checked').each(function() {
            jiraTask = $(this).parent().parent().find('td').eq(1).html();
            if (jiraTask) {
                return false;
            };
        });
        if (jiraTask) {
            setHidden("createTask");
        } else {
            removeHidden("createTask");
        };
    } else {
        toggleButtons.forEach(el => setHidden(el));
        removeHidden("addAll");
        setHidden("createTask");
    };
};

// Handle click on checkbox to set state of "Select all" control
$('#report tbody').on('change', 'input[type="checkbox"]', function(){
    $(this).parent().parent().children().each(function(ind) {
        let val = $(this).text();
        if (ind == 1 && val && !validateJiraTask(val)) {
            return;
        };
        let attr = attributesMap[Number(ind)];
        $("#" + attr).val(val);
        // Handling error reason select
        // if (ind == 3) {
        //     $("#error_reason > option").each(function() {
        //         if (val == $(this).html()) {
        //             $(this).prop("selected", true);
        //         };
        //     });
        // } else if (ind == 1) {
        if (ind == 1) {
            $("#jira_issue").html(`<a href="${jiraUrl + val}">${val}</a>`);
        };
    });
    buttonsToggle();
});

const multipleSelect = () => {
    let response = [];
    myTable.$('input[type="checkbox"]:checked').each(function(){
        response.push(this.value);
    });

    return response;
};

/* DataTable end */

var postRequests = new postRequests(
    'DqReportEdit', // entity name
    undefined, // russian entity name
    ['jira_issue', 'error_origin', 'error_reason'] // list of inputs (create form to http request)
);

$('#getStatus').on('click', function() {
    $('#jira_status').val("");
    let jiraIssue = $('#jira_issue').val();
    var json = `[{"jiraIssue": "${jiraIssue}"}]`;
    var obj = eval(json);
    $('#jira_issue').html(`<a href="${jiraUrl + obj[0]["jiraIssue"]}">${obj[0]["jiraIssue"]}</a>`);
    
    if (jiraIssue) {
        let xk = $("#xk").val();
        $.ajax({
            type: "GET",
            url: window.location.protocol + '//' + window.location.host + `/api/jira/task?wfId=${wfId}&xk=${xk}`,
            dataType: "json",
            encode: true,
            async: true
        }).done(function (data) {
            $('#jira_status').val(data.fields.status.name);
        }).fail(function () {
            $('#jira_status').val("Нет информации");
        });
    } else {
        Swal.fire({
            icon: 'error',
            title: 'По выбранной строке отсутствует трек Jira',
            position: 'top-end',
            showConfirmButton: false,
            toast: true,
            timer: 5000
        });
    };
});

$('#add, #hardRemove, #addAll').on('click', function() {
    let form = {
        add: {rowsId: multipleSelect()},
        hardRemove: undefined,
        addAll: []
    };
    postRequests.postRequest(
        `api/report/${controlId}/edit/${wfId}`, // endpoint
        this.id == "addAll" ? "add" : this.id, // button ID
        undefined, // http request param
        (this.id == "add" || this.id == "addAll") ? "PUT" : "DELETE", // method
        form[this.id]
    );
    myTable.draw();
});

$('#createTask').on('click', function() {
    modalToggle();
    selectedRows = multipleSelect();
    if (!selectedRows) {
        Swal.fire({
            icon: 'error',
            title: "Не выбрана строка",
            position: 'top-end',
            showConfirmButton: false,
            toast: true,
            timer: 3000
        });
        return;
    };

    // postRequests.postRequest(
    //     `api/report/${controlId}/edit/${wfId}`, // endpoint
    //     "add", // button ID
    //     undefined, // http request param
    //     "PUT", // method
    //     (selectedRows ? {rowsId: selectedRows} : undefined)
    // );

    let formData = {
        controlId: controlId,
        wfId: wfId,
        rowsId: selectedRows ? selectedRows : []
    };

    $.ajax({
        type: "POST",
        url: window.location.protocol + '//' + window.location.host + '/api/jira/task',
        dataType: "json",
        data: formData,
        headers: {"X-CSRFToken": csrf_token},
        encode: true,
        async: true
    }).done(function (data) {
        myTable.draw();
        setTimeout(modalToggle, 1000);
        Swal.fire({
            icon: 'success',
            title: 'Трек Jira успешно создан',
            position: 'top-end',
            showConfirmButton: false,
            toast: true,
            timer: 3000
        });
    }).fail(function (data) {
        myTable.draw();
        setTimeout(modalToggle, 1000);
        Swal.fire({
            icon: 'error',
            title: "Возникла ошибка при создании задачи",
            position: 'top-end',
            showConfirmButton: false,
            toast: true,
            timer: 3000
        });
    });
});

$(document).ready(
    function() {
        setTableDelay(myTable);
    }
);
