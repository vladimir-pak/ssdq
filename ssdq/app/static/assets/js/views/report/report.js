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
    config.exportOptions.columns = columnsExport;
    dt.one('preXhr', function (e, s, data) {
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

const hasResult = (has_result, errorMsg=undefined) => {
    if (!has_result) {
        $('#report').prop('hidden', true);
        if (errorMsg) {
            $('#message').html(`<h1 class="card-title" style="margin: 2% 2% 2% 2%;">Ошибка выполнения запроса:
               <p style="margin: 2% 2% 2% 2%;">${errorMsg}</p></h1>`);
        } else {
            $('#message').html(`<h1 class="card-title" style="margin: 2% 2% 2% 2%;">За выбранную дату ошибок не обнаружено</h1>`);
        };
    } else {
        $('#report').prop('hidden', false);
        $('#message').html('');
    };
};

const getColumns = () => {
    let cnt = 30; // max columns
    let dataset = [];
    for (let a = 0; a<cnt; a++) {
        dataset.push(
            {
                data: a,
                render: function (data) {
                    return `<plaintext style="margin: 0 0 0 0;">${data}`
                }
            }
        );
    };
    return dataset;
};

const colHeader = '<span class="dt-column-title"></span><span class="dt-column-order" role="button" aria-label=": Activate to invert sorting" tabindex="0"></span>';

var columnsExport = [];
var columnsTitle = [];

const grid = () => {
    let wfId = $('#reportDate').val();

    var dt = new DataTable("#report", {
        language: {
            url: '/static/assets/ru.json'
        },
        processing: true,
        serverSide: true,
        serverMethod: 'post',
        dom: 'B<"row"<"col-sm-6 p-1"l><"col-sm-6"f>>tip',
        buttons:
            [
                {
                    extend: 'excel',
                    text: 'Выгрузить в Excel',
                    className: 'btn btn-outline-primary btn-width p-1',
                    titleAttr: 'Excel',
                    title: controlId + '_report_'+formatDate(new Date()),
                    exportOptions: {
                        format: {
                            header: function(data, ind) {
                                return columnsTitle[ind]
                            },
                            body: function(inner, rowid, colid, node) {
                                return inner.replace('<plaintext style="margin: 0 0 0 0;">', '');
                            }
                        }
                    },
                    action: exportAction
                },
                {
                    extend: 'pdf',
                    orientation: 'landscape',
                    pageSize: 'LEGAL',
                    text: 'Выгрузить в pdf',
                    className: 'btn btn-outline-primary btn-width p-1',
                    titleAttr: 'pdf',
                    title: controlId + '_report_'+formatDate(new Date()),
                    exportOptions: {
                        format: {
                            header: function(data, ind) {
                                return columnsTitle[ind]
                            },
                            body: function(inner, rowid, colid, node) {
                                return inner.replace('<plaintext style="margin: 0 0 0 0;">', '');
                            }
                        }
                    },
                    action: exportAction
                }
            ],
        ajax: {
            url:`/api/report/${controlId}`,
            data: {wfId: wfId},
            headers: {"X-CSRFToken": csrf_token},
            dataSrc: function ( json ) {
                //Make your callback here.
                if (json.aaData.length) {
                    hasResult(true);
                    json.headers.map((e, index) => {
                        $($('#report>thead>tr>th')[index]).html(e + colHeader);
                    });
                    columnsTitle = json.headers;
                    columnsExport = dt.columns()[0].slice(0, json.headers.length);

                    dt.columns(dt.columns()[0].slice(json.headers.length)).visible(false);
                } else {
                    hasResult(false, json.error_message);
                };
                return json.aaData;
            }
        },
        lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
        searching: false,
        autoWidth: false,
        responsive: false,
        aaSorting: ['asc', 'desc'],
        columns: getColumns(),
        oLanguage: {sProcessing: `<div class="spinner-border text-success" style="width: 6rem; height: 6rem;"></div>`}
    });
    return dt;
};

var reportDatatable = grid();

$("#reportDate").on("change", function() {
    reportDatatable.destroy();
    reportDatatable = grid();
});

$('#reportEdit').on('click', function() {
    let wfId = $('#reportDate').val();
    window.location.href = `/report/${controlId}/edit/${wfId}`;
});
