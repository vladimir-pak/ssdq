const formatDate = (date) => {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();
    if (month.length < 2)
         month = '0' + month;
    if (day.length < 2)
         day = '0' + day;
    return [day, month, year].join('.');
};

function exportAction (e, dt, button, config, n) {
    var self = this;
    var oldStart = dt.settings()[0]._iDisplayStart;
    dt.one('preXhr', function (e, s, data) {
        // Just this once, load all data from the server...
        data.start = 0;
        data.length = 2147483647;
        dt.one('preDraw', function (e, settings) {
        // Call the original action function
        if (button[0].className.indexOf('buttons-excel') >= 0) {
            $.fn.dataTable.ext.buttons.excelHtml5.available(dt, config) ?
                 $.fn.dataTable.ext.buttons.excelHtml5.action.call(self, e, dt, button, config, n) :
                 $.fn.dataTable.ext.buttons.excelFlash.action.call(self, e, dt, button, config, n);
        } else if (button[0].className.indexOf('buttons-pdf') >= 0) {
            $.fn.dataTable.ext.buttons.pdfHtml5.available(dt, config) ?
                $.fn.dataTable.ext.buttons.pdfHtml5.action.call(self, e, dt, button, config, n) :
                $.fn.dataTable.ext.buttons.pdfFlash.action.call(self, e, dt, button, config, n);
        };
        dt.one('preXhr', function (e, s, data) {
             // DataTables thinks the first item displayed is index 0, but we're not drawing that.
             // Set the property to what it was before exporting.
             settings._iDisplayStart = oldStart;
             data.start = oldStart;
        });
        // Reload the grid with the original page. Otherwise, API functions like table.cell(this) don't work properly.
        setTimeout(dt.ajax.reload, 0);
        // Prevent rendering of the full data to the DOM
        return false;
        });
    });
    // Requery the server with the new one-time export settings
    dt.ajax.reload();
};

new DataTable('#monitoringTable', {
    language: {
        url: '/static/assets/ru.json'
    },
    processing: true,
    serverSide: true,
    serverMethod: 'post',
    dom: "B<'row'<'col-sm-3 p-2'l><'col-sm-6'><'col-sm-3 p-2'f>>tip",
    buttons:
        [
            {
                extend: 'excel',
                text: 'Выгрузить в Excel',
                className: 'btn btn-block btn-outline-primary btn-width',
                titleAttr: 'Excel',
                title: 'SSDQ_'+formatDate(new Date()),
                action: exportAction
            }
        ],
    ajax: {
        url: window.location.protocol + '//' + window.location.host + `/api/monitoring?filter=${filter}`,
        headers: {"X-CSRFToken": csrf_token},
    },
    lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    searching: true,
    order: [0,'desc'],
    aaSorting: ['asc', 'desc'],
    autoWidth: false,
    responsive: false,
    columns: [
        { data: 'id' },
        { data: 'name',
            render: function (data, type, row) {
                return `<a href="/controls?id=${row.id}">${data}</a>`;
            }
        },
        { data: 'description' },
        { data: 'object_name' },
        { data: 'owner' },
        { data: 'report_date',
            render: function (data, type, row) {
                let dd = '';
                if (formatDate(data) == '01.01.1970') {
                    dd = '-';
                }
                else {
                    dd = formatDate(data);
                }
                return dd;
            }
        },
        { data: 'mistake_count',
            render: function (data, type, row) {
                if (data != null) {
                    return '<a href="/report/'+ row.id +'">'+data+'</a>';
                }
                else {
                    return '-';
                };
            }
        },
        { data: 'team_name' },
        { data: 'status_name' }
    ],
    oLanguage: {
        sProcessing: `<div class="spinner-border text-success" style="width: 6rem; height: 6rem;"></div>`,
        sEmptyTable: "Нет данных"
    }
});

const filterNameMap = {
    ALL: "Все контроли",
    EXPLOITATION: "контроли в эксплуатации",
    ACTUALIZATION: "контроли на актуализации",
    DISABLED: "отключенные контроли",
    DEVELOPMENT: "контроли в работе",
    USER: "Мои контроли",
    TEAM: "Контроли команды",
    EXPIRING: "Подходит срок актуализации"
};

$('#cardHeader').html(filterNameMap[filter]);

