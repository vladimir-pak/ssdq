const formatMonth = (date) => {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1)
    const months = ['янв.', 'февр.', 'март', 'апр.', 'май', 'июнь', 'июль', 'авг.', 'сент.', 'окт.', 'нояб.', 'дек.'];
    return months[month - 1];
};

const setBanners = () => {
    const bannersId = ["usr_cnt", "dev_cnt", "exp_cnt", "expiring_cnt", "act_cnt", "cncl_cnt"];
    let data = apiData("main");
    
    bannersId.map(e => {
        $('#'+e).html(data[e]);
    });
};

const setCharts = () => {
    var controlsCanvas = $('#controls').get(0).getContext('2d');
    var controlsErrorCanvas = $('#controlsError').get(0).getContext('2d');

    // gradients for charts
    var gradientExp = controlsCanvas.createLinearGradient(0, 250, 0, 0);
    gradientExp.addColorStop(1, '#44bf78');
    gradientExp.addColorStop(0, 'rgba(255, 255, 255, 1)');

    var gradientAct = controlsCanvas.createLinearGradient(0, 250, 0, 0);
    gradientAct.addColorStop(1, '#ff7900');
    gradientAct.addColorStop(0, 'rgba(255, 255, 255, 1)');

    var gradientCncl = controlsCanvas.createLinearGradient(0, 250, 0, 0);
    gradientCncl.addColorStop(1, '#798bac');
    gradientCncl.addColorStop(0, 'rgba(255, 255, 255, 1)');

    var gradient = controlsErrorCanvas.createLinearGradient(0, 250, 0, 0);
    gradient.addColorStop(1, '#f6514c');
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');

    var controlsData = {
        labels: [],
        datasets: [
            {
                label: 'Эксплуатация',
                backgroundColor: gradientExp, //'#1b438b',
                borderColor: '#44bf78',
                data: [],
                pointRadius: 1.5,
                borderWidth: 1.5,
                fill: true
            },
            {
                label: 'На актуализации',
                backgroundColor: gradientAct, //'#ff7900',
                borderColor: '#ff7900',
                data: [],
                pointRadius: 1.5,
                borderWidth: 1.5,
                fill: true
            },
            {
                label: 'Отключен',
                backgroundColor: gradientCncl, // '#798bac',
                borderColor: '#798bac',
                data: [],
                pointRadius: 1.5,
                borderWidth: 1.5,
                fill: true
            }
        ]
    };

    var controlsOptions = {
        layout: {
            padding: {
                top: 3
            }
        },
        maintainAspectRatio: false,
        tooltips: {
            mode: 'point',
            intersect: true
        },
        hover: {
            mode: 'point',
            intersect: true
        },
        legend: {
            display: false
        },
        scales: {
            yAxes: [{
                gridLines: {
                    display: true,
                    lineWidth: '1px',
                    color: 'rgba(0, 0, 0, .2)',
                    zeroLineColor: 'transparent'
                },
                ticks: $.extend({
                    beginAtZero: true,
                    callback: function (value) {
                        return Number.isInteger(value) ? value : '';
                    }
                }, {
                    display: false,
                    fontColor: '#495057',
                    fontStyle: 'bold'
                })
            }],
            xAxes: [{
                display: true,
                gridLines: {
                    display: false
                },
                ticks: {
                    fontColor: '#495057',
                    fontStyle: 'bold'
                }
            }]
        }
    };

    var controls = new Chart(controlsCanvas, {
        type: 'line',
        data: controlsData,
        options: controlsOptions
    });

    var controlsErrorData = {
        labels: [],
        datasets: [
            {
                label: 'Контролей с ошибками',
                type: 'line',
                data: [],
                backgroundColor: gradient,
                borderColor: '#f6514c',
                pointRadius: 1.5,
                borderWidth: 1.5,
                fill: true
            }
        ]
    };

    var controlsErrorOptions = {
        layout: {
            padding: {
                top: 3
            }
        },
        maintainAspectRatio: false,
        tooltips: {
            mode: 'point',
            intersect: true
        },
        hover: {
            mode: 'point',
            intersect: true
        },
        legend: {
            display: false
        },
        scales: {
            yAxes: [{
                // display: false,
                gridLines: {
                    display: true,
                    lineWidth: '1px',
                    color: 'rgba(0, 0, 0, .2)',
                    zeroLineColor: 'transparent'
                },
                ticks: $.extend({
                    beginAtZero: true,
                    callback: function(value) {
                        return Number.isInteger(value) ? value : '';
                    }
                }, {
                    display: false,
                    fontColor: '#495057',
                    fontStyle: 'bold'
                }),
            }],
            xAxes: [{
                display: true,
                gridLines: {
                    display: false
                },
                ticks: {
                    fontColor: '#495057',
                    fontStyle: 'bold'
                }
            }]
        }
    };

    var controlsError = new Chart(controlsErrorCanvas, {
        type: 'line',
        data: controlsErrorData,
        options: controlsErrorOptions
    });

    const controlStatus = {
        DEVELOPMENT: 1,
        EXPLOITATION: 2,
        ACTUALIZATION: 3,
        DISABLED: 4
    }

    let data = apiData("main/charts?type=main")

    // Upload data from database to chart
    // controls by status
    var mapped = data.controls.reduce((acc, cur, index) => {
        acc[cur.thedate] = acc[cur.thedate] || {
            thedate: cur.thedate,
            expl_cnt: 0,
            canceled_cnt: 0,
            actual_cnt: 0
        },
        acc[cur.thedate].expl_cnt += 1 ? cur.status_id == controlStatus.EXPLOITATION : 0;
        acc[cur.thedate].canceled_cnt += 1 ? cur.status_id == controlStatus.DISABLED : 0;
        acc[cur.thedate].actual_cnt += 1 ? cur.status_id == controlStatus.ACTUALIZATION : 0;
        acc[index] = acc[cur.thedate];
        
        return acc;
    }, []);

    var controlsDataDetail = [...new Set(mapped)];
    if (!controlsDataDetail.length) {
        $('#controls').html('<p style="text-align: center;">Отсутствуют данные для формирования графика</p>');
        return false;
    };

    for (cur in controlsDataDetail) {
        controlsData.datasets[0].data.push(controlsDataDetail[cur].expl_cnt);
        controlsData.datasets[2].data.push(controlsDataDetail[cur].canceled_cnt);
        controlsData.datasets[1].data.push(controlsDataDetail[cur].actual_cnt);
        controlsData.labels.push(formatMonth(controlsDataDetail[cur].thedate))
    };

    controls.update();

    // controls with errors
    var mapped = data.controls_error.reduce((acc, cur, index) => {
        acc[cur.report_date] = acc[cur.report_date] || {
            report_date: cur.report_date,
            all_cnt: 0
        };
        acc[cur.report_date].all_cnt += 1 ? cur.id > 0 : 0;
        acc[index] = acc[cur.report_date];

        return acc;
    }, []);

    var controlsErrorDataDetail = [...new Set(mapped)];

    if (!controlsErrorDataDetail.length) {
        $('#controlsError').html('<p style="text-align: center;">Отсутствуют контроли КД с выявленными ошибками</p>');
        return;
    };

    for (cur in controlsErrorDataDetail) {
        controlsErrorData.datasets[0].data.push(controlsErrorDataDetail[cur].all_cnt);
        controlsErrorData.labels.push(formatMonth(controlsErrorDataDetail[cur].report_date));
        controlsError.update();
    };

    return;
};

$(document).ready(
    function() {
        setBanners();
        setCharts();
    }
);
