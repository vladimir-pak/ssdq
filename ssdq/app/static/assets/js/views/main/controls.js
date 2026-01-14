const apiData = (endpoint, method="GET", body=undefined) => {
    let url = window.location.protocol + '//' + window.location.host + '/api/' + endpoint;
    var response;
    $.ajax({
        type: method,
        url: url,
        data: body,
        dataType: "json",
        headers: {"X-CSRFToken": csrf_token},
        encode: true,
        async: false
    }).done(function (data) {
        response = data;
    }).fail(function (data) {
        Swal.fire({
            icon: 'error',
            title: data.responseJSON.message,
            position: 'top-end',
            showConfirmButton: false,
            toast: true,
            timer: 3000
        });
    });

    return response;
};

// templates

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

const htmlContent = (
    controlId,
    controlName,
    description,
    statusName,
    crossdb_flag,
    isFavorite,
    last_result,
    divName
) => {
    const lastResultHandle = (last_result) => {
        if (last_result) {
            let status = last_result.error_flag == 'Y' ? "danger" : last_result.mistake_count == 0 ? "success" : "warning";
            let tip = {
                danger: "Ошибка выполнения",
                success: "Нет ошибок",
                warning: "Ошибок: " + last_result.mistake_count.toString()
            };
            let className = {
                danger: "fas fa-circle danger",
                success: "fas fa-circle success",
                warning: "fas fa-circle warning"
            };
            return `<a data-title="${tip[status]}" class="nav-link tip-left p-1">
                        <i class="nav-icon ${className[status]}"></i>
                    </a>`;
        } else {
            return `<a data-title="Нет запусков" class="nav-link tip-left p-1">
                        <i class="nav-icon fas fa-circle info"></i>
                    </a>`;
        };
    };
    divName = divName.replace('-', '_');
    divName = divName.replace("#", "");
    let canvasId = `${divName}_${controlId}`;

    let getResultsFunc = last_result ? `getCanvas('${divName}', ${controlId}); toggleCanvas('${divName}', ${controlId});` : "";

    let isCrossDb = `<a data-title="Кросс-базовый" class="nav-link tip-left p-1" style="visibility: visible;">
                        <i class="nav-icon fas fa-link"></i>
                    </a>`;

    return `<div class="card" style="margin-bottom: 0.3em;">
                <div class="card-body control-card p-2" style="font-size: 0.8em;" id="control_${controlId}" onclick="toggleSelected(this);"
                    onmouseenter="${getResultsFunc}" 
                    onmouseleave="toggleCanvas('${divName}', ${controlId});">
                    <a href="/controls?id=${controlId}">
                        <h5 style="font-weight: normal; display: inline-block;
                            max-width: 75%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${controlId}. ${controlName}</h5>
                    </a>
                    <div class="row">
                        <div class="col-sm-5">
                            Статус: ${statusName}
                            <br><p style="max-width: 75%; overflow: hidden; margin-bottom: 0;
                                text-overflow: ellipsis; white-space: nowrap;">Описание: ${description}</p>
                        </div>
                        <div class="col-sm-5">
                            <canvas id="chart_${canvasId}" style="max-height: 3.8vh;"></canvas>
                        </div>
                    </div>
                </div>
                <div id="favorite_div_${controlId}" class="favorite-div p-2">
                    <a data-title="Редактировать" class="nav-link tip-left p-1" href="/controls/${controlId}">
                        <i class="nav-icon fas fa-pencil-alt"></i>
                    </a>
                    <a data-title="Клонировать" class="nav-link tip-left p-1" href="/controls/${controlId}/clone">
                        <i class="nav-icon fas fa-copy"></i>
                    </a>
                    <a data-title="${isFavorite == 'Y' ? 'Исключить из избранного' : 'Добавить в избранное'}" onclick="handleFavorites(this);"
                        class="nav-link tip-left p-1 ${isFavorite == 'Y' ? "favorite-selected-div" : ""}" control-id="${controlId}">
                        <i class="nav-icon ${isFavorite == 'Y' ? 'fas' : 'far'} fa-star"></i>
                    </a>
                    ${crossdb_flag == 'Y' ? isCrossDb : ""}
                    ${lastResultHandle(last_result)}
                </div>
            </div>`
};

const htmlContentControlInfo = (
    controlId,
    controlName,
    owners,
    objects,
    tags,
    lastResults
) => {
    return `<div class="card-body p-3" style="font-size: 1em;">
                <a href="/controls?id=${controlId}"><h5 style="font-weight: normal; display: inline-block;">${controlName}</h5></a>
                <br>
                <br><p style="color: #757575; margin-bottom: 0.5rem;">Ответственные</p>
                <div class="control-info-card">
                ${owners.map((e) => {return '<p style="margin-bottom: 0.1em;">' + e.name + ' (' + e.email + ')</p>'}).join('')}
                </div>
                <br><p style="color: #757575; margin-bottom: 0.5rem;">Объекты контроля</p>
                <div class="control-info-card">
                ${objects.map((e) => {return '<p style="margin-bottom: 0.1em;">' + e.name + '</p>'}).join('')}
                </div>
                <br><p style="color: #757575; margin-bottom: 0.5rem;">Теги</p>
                <div class="control-info-card">
                ${tags.map((e) => {return '<p style="margin-bottom: 0.1em;">' + e.name + '</p>'}).join('')}
                </div>
                <br><p style="color: #757575; margin-bottom: 0.5rem;">Результаты последнего запуска</p>
                <div class="control-info-card">
                <i>Отчетная дата:</i> ${lastResults.reportDate ? formatDate(lastResults.reportDate) : 'Нет данных'}
                <br><i>Количество ошибок:</i> ${lastResults.mistakeCount ? lastResults.mistakeCount : 'Нет данных'}
                ${lastResults.mistakeCount ? '<br><a href="/report/'+controlId+'">Отчет</a>' : ''}
                </div>
            </div>`
};

// Controls cards (grid)

var pagination = 0; // pages count
var page = 0; // current page

const toggleSelectedClass = (elem, parentDiv) => {
    $('.main-selected-card').toggleClass('main-selected-card');
    $(`#${parentDiv} >> #${elem}`).toggleClass('main-selected-card');
    return;
};

const divMaps = {
    "teams-controls": "teams-controls",
    "my-controls": "my-controls",
    "my-favorites": "my-favorites",
    "#teams-controls": "#teams-controls",
    "#my-controls": "#my-controls",
    "#my-favorites": "#my-favorites"
};

const toggleSelected = (elem) => {
    try {
        let parentDiv = $(elem).parent().parent().attr('id');
        parentDiv = divMaps[parentDiv];
        toggleSelectedClass(elem.id, parentDiv);
        let controlId = elem.id.split('_')[1];
        renderControlInfo(controlId);
        $('#controlInfo').prop('hidden', false);
    } catch (err) {
        console.log(err);
        $('#controlInfo').prop('hidden', true);
    };
};

const togglePagination = (page, pages) => {
    if (page >= pages) {
        $('#nextPage').addClass('no-hover');
    } else {
        $('#nextPage').removeClass('no-hover');
    };
    if (page == 0) {
        $('#prevPage').addClass('no-hover');
    } else {
        $('#prevPage').removeClass('no-hover');
    };
};

const setControlsList = (elementId="#teams-controls", page=0, search=undefined) => {
    const panelMapping = {
        '#teams-controls': 'TEAM',
        '#my-controls': 'USER',
        '#my-favorites': 'FAVORITES'
    };

    let data = apiData(`main/controls?page=${page}&owner=${panelMapping[elementId]}${search ? ("&search=" + search) : ""}`);

    pagination = data.pages;

    // render controls list
    $(elementId).html("");
    if (data) {
        data.data.map((e) => {
            $(elementId).append(htmlContent(
                e.id,
                e.name,
                e.description,
                e.status_name,
                e.crossdb_flag,
                e.is_favorite,
                e.last_result,
                elementId
            ));
        });
    };
    toggleSelected($(elementId).children().children()[0]);
    togglePagination(page, pagination);
};

const renderControlInfo = (
    controlId
) => {
    let data = apiData("main/card?controlId="+controlId);
    if (data) {
        $("#controlInfo").html("");
        $("#controlInfo").append(htmlContentControlInfo(
            controlId,
            data.controlName,
            data.owners,
            data.objects,
            data.tags,
            data.lastResults
        ));
    };
};

const handleFavorites = (elem) => {
    let controlId = $(elem).attr('control-id');
    let childElement = $(elem).children()[0];
    let isFavorite = $(childElement).hasClass('fas');
    let response;
    if (isFavorite) {
        response = apiData("main/controls", "DELETE", {controlId: Number(controlId)});
        $(childElement).removeClass('fas');
        $(childElement).addClass('far');
        $(elem).removeClass('favorite-selected-div');
        $(elem).attr('data-title', 'Добавить в избранное');
    } else {
        response = apiData("main/controls", "POST", {controlId: Number(controlId)});
        $(childElement).removeClass('far');
        $(childElement).addClass('fas');
        $(elem).addClass('favorite-selected-div');
        $(elem).attr('data-title', 'Исключить из избранного');
    };
    Swal.fire({
        icon: 'success',
        title: response.response,
        position: 'top-end',
        showConfirmButton: false,
        toast: true,
        timer: 3000
    });
};

const searchControls = (elementId) => {
    let searchString = $('#searchString').val();
    if (searchString) {
        setControlsList(elementId, 0, searchString);
        // toggleSelected($(elementId).children().children()[0]);
        // togglePagination(page, pagination);
    } else {
        setControlsList(elementId);
    };
};

$('#prevPage, #nextPage').on('click', function () {
    let div = $('#panels').children().find(".active");
    let divId = div.attr("href");
    divId = divMaps[divId];

    if (this.id == 'nextPage') {
        page += 1;
        setControlsList(divId, page);
    } else {
        if (page > 0) {
            page -= 1;
            setControlsList(divId, page);
        };
    };
    $('#controlInfo, #banners').css('top', 'initial');
});

$('#teamsButton, #userButton, #favoritesButton').on('click', function () {
    page = 0;
    let divId = $(this).attr('href');
    divId = divMaps[divId];

    setControlsList(divId, page);
    Object.values(Chart.instances).map((e) => {
        if (e.canvas.id != 'controlsError' && e.canvas.id != 'controls') {
            e.destroy();
        };
    });
});

// $('#searchButton').on('click', function () {
//     searchControls();
// });

var timer;
$("#searchString").bind("input", function() {
    window.clearTimeout(timer);
    timer = window.setTimeout(function() {
        searchControls();
    }, 1000);
});

const getChart = (element) => {
    var gradient = element.createLinearGradient(0, 40, 0, 0);
    gradient.addColorStop(1, 'rgba(68, 120, 255, 0.7)');
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
    var chart = new Chart(element, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Ошибок',
                    backgroundColor: gradient,
                    borderColor: 'rgba(68, 120, 255)',
                    borderWidth: 0.7,
                    data: [],
                    pointRadius: 0.1,
                    fill: true
                }
            ]
        },
        options: {
            layout: {
                padding: 1
            },
            maintainAspectRatio: false,
            tooltips: {
                enabled: false
            },
            hover: {
                mode: null
            },
            legend: {
                display: false
            },
            scales: {
                yAxes: [{
                    gridLines: {
                        display: false,
                        lineWidth: '1px',
                        color: 'rgba(0, 0, 0, .2)',
                        zeroLineColor: 'transparent',
                    },
                    ticks: {
                        display: false
                    }
                }],
                xAxes: [{
                    display: false,
                    gridLines: {
                        display: false
                    }
                }]
            }
        }
    });
    return chart;
};

const getCanvas = (divName, id) => {
    divName = divName.replace("#", "")
    let chartId = `chart_${divName}_${id}`;
    let isExist = Object.values(Chart.instances).filter((c) => c.canvas.id == chartId).pop();

    if (!isExist) {
        var canvas = $('#'+chartId).get(0);
        var context = canvas.getContext('2d');
        context.clearRect(0, 0, canvas.width, canvas.height);

        var chart = getChart(context);

        $(`#chart_${divName}_${id}`).toggle();

        let data = apiData("main/charts?type=results&controlId=" + id);
        if (data) {
            for (let i = data.length-1; i >= 0; i--) {
                chart.data.datasets[0].data.push(data[i].mistake_count);
                chart.data.labels.push(data[i].report_date);
            };
            chart.update();
        };
    };
};

const toggleCanvas = (divName, id) => {
    $(`#chart_${divName}_${id}`).slideToggle(200);
};

$(document).ready(
    function() {
        setControlsList();
    }
);
