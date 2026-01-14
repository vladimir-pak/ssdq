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
            title: 'Отсутствует информация о результатах контроля',
            position: 'top-end',
            showConfirmButton: false,
            toast: true,
            timer: 3000
        });
    });

    return response;
};

const getAggData = () => {
    const params = new Proxy(new URLSearchParams(window.location.search), {
        get: (searchParams, prop) => searchParams.get(prop),
    });
    let curWfId = params.wfId;
    let data = apiData(`report/${controlId}`);

    let maxLen = data.report.report_date.length;

    data.report.report_date.map((e, index) => {
        if (index == maxLen-1) {
            $('#startdate').append($('<option>', {
                value: e,
                text: e,
                selected: true
            }));
        } else if (index ==0) {
            $('#enddate').append($('<option>', {
                value: e,
                text: e,
                selected: true
            }));
        } else {
            $('#startdate').append($('<option>', {
                value: e,
                text: e
            }));
            $('#enddate').append($('<option>', {
                value: e,
                text: e
            }));
        };

        $('#reportDate').append($('<option>', {
            value: data.report.wf_id[index],
            text: `${e} строк: ${data.report.mistake_count[index]}`,
            selected: data.report.wf_id[index] == curWfId
        }));
    });
    return data.report;
};

const getChart = () => {
    var $barChart = $('#barChart');
    
    barChart = new Chart($barChart, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [
                {
                    label               : 'Количество ошибок',
                    backgroundColor     : 'rgba(60,141,188,0.9)',
                    borderColor         : 'rgba(60,141,188,0.8)',
                    pointRadius         : false,
                    pointColor          : '#3b8bba',
                    pointStrokeColor    : 'rgba(60,141,188,1)',
                    pointHighlightFill  : '#fff',
                    pointHighlightStroke: 'rgba(60,141,188,1)',
                    data                : ''
                }
            ]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        min: 0
                    }
                }]
            },
            responsive              : true,
            maintainAspectRatio     : false,
            datasetFill             : false
        }
    });
    return barChart;
};

const updateChart = (barChart, report_time, mistake_cnt) => {
    let report_time_reversed = [...report_time];
    let mistake_cnt_reversed = [...mistake_cnt];
    var new_report_time = [...report_time_reversed.reverse()];
    var new_mistake_cnt = [...mistake_cnt_reversed.reverse()];
    var startdate = $('#startdate').val();
    var enddate = $('#enddate').val();
    var indexstartdate = new_report_time.indexOf(startdate);
    var indexenddate = new_report_time.indexOf(enddate);
    var filterDate = new_report_time.slice(indexstartdate, indexenddate+1);
    var filterCnt = new_mistake_cnt.slice(indexstartdate, indexenddate+1);
    barChart.data.labels = filterDate;
    barChart.data.datasets[0].data = filterCnt;
    barChart.update();
};

var chartData = getAggData();
var chart = getChart();

$("#updateChart").on("click", function() {
    updateChart(chart, chartData.report_date, chartData.mistake_count);
})

$(document).ready(
    function() {
        updateChart(chart, chartData.report_date, chartData.mistake_count);
    }
);
