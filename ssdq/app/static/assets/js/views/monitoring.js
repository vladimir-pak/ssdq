const gridDiv = document.querySelector("#monitoringGrid");

const columnDefs = [
    { headerName: "ID", field: "id", colId: "id", filter: "agTextColumnFilter" },
    { headerName: "Наименование", field: "name", colId: "name", filter: "agTextColumnFilter", minWidth: 155 },
    { headerName: "Описание", field: "description", colId: "description", filter: "agTextColumnFilter" },
    { headerName: "Условие отбора", field: "conditions", colId: "conditions", filter: "agTextColumnFilter", minWidth: 160 },
    { headerName: "Сегмент", field: "segment", colId: "segment", filter: "agTextColumnFilter" },
    { headerName: "Источник", field: "source", colId: "source", filter: "agTextColumnFilter" },
    { headerName: "Статус", field: "status_name", colId: "status_name", filter: "agTextColumnFilter" },
    { headerName: "wiki", field: "wiki", colId: "wiki", filter: "agTextColumnFilter" },
    { headerName: "Команда", field: "team_name", colId: "team_name", filter: "agTextColumnFilter" },
    { headerName: "Тип контроля", field: "control_type", colId: "control_type", filter: "agTextColumnFilter", minWidth: 155 },
    { headerName: "Предметная область", field: "subject_area", colId: "subject_area", filter: "agTextColumnFilter", minWidth: 195 },
    { headerName: "Уровень критичности", field: "critical_level", colId: "critical_level", filter: "agTextColumnFilter" , minWidth: 200 },
    { headerName: "Нижняя граница", field: "threshold_min", colId: "threshold_min", filter: "agTextColumnFilter", minWidth: 165 },
    { headerName: "Верхняя граница", field: "threshold_max", colId: "threshold_max", filter: "agTextColumnFilter", minWidth: 165 },
    { headerName: "Вид почтовой рассылки", field: "alerting_type", colId: "alerting_type", filter: "agTextColumnFilter", minWidth: 215 },
    { headerName: "Вид создаваемого инцидента", field: "jira_mode", colId: "jira_mode", filter: "agTextColumnFilter", minWidth: 255 },
    { headerName: "Объект", field: "object_name", colId: "object_name", filter: "agTextColumnFilter" },
    { headerName: "Ответственный", field: "owner", colId: "owner", filter: "agTextColumnFilter", minWidth: 155 },
    { headerName: "Теги", field: "tags", colId: "tags", filter: "agTextColumnFilter" },
    { headerName: "Последний запуск", field: "report_date", colId: "report_date", filter: "agDateColumnFilter", minWidth: 180 },
    { headerName: "Результат", field: "mistake_count", colId: "mistake_count", filter: "agTextColumnFilter" }
];

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

const path = window.location.pathname;
const pathParts = path.split('/').filter(part => part.length > 0);
const endpoint = pathParts[pathParts.length - 1];

const getEndpoint = () => {
    const path = window.location.pathname;
    const pathParts = path.split('/').filter(part => part.length > 0);
    return pathParts[pathParts.length - 1].toUpperCase();
}

function makeDatasource() {
    return {
        getRows: async (params) => {
            try {
                const body = {
                    flt: endpoint.toUpperCase(),
                    startRow: params.startRow,
                    endRow: params.endRow,
                    sortModel: params.sortModel,
                    filterModel: params.filterModel,
                };

                const resp = await fetch("/api/monitoring", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": window.csrf_token,
                    },
                    body: JSON.stringify(body),
                });

                if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
                const data = await resp.json();

                params.successCallback(data.rows, data.lastRow);
                params.api.setGridOption("loading", false);
            } catch (e) {
                console.error(e);
                params.failCallback();
                params.api.setGridOption("loading", false);
            }
        },
    };
}

// кнопки — на странице, чтобы URL/filename были конкретными
function wireButtons(params) {
    document.querySelector("#btnResetFilters").addEventListener("click", () => {
        params.api.setFilterModel(null);
        params.api.onFilterChanged();
        params.api.paginationGoToFirstPage();
    });

    document.querySelector("#btnResetColumns").addEventListener("click", () => {
        params.api.resetColumnState();
    });

    document.querySelector("#btnExportCsv").addEventListener("click", async () => {
        await window.AGGridUtils.exportCsvAll(params, {
            url: "/api/monitoring/csv",
            filename: "monitoring.csv",
            extraBody: {flt: getEndpoint()},
            csrfToken: window.csrf_token,
        });
    });
}

const baseOptions = window.AGGridUtils.createBaseGridOptions({
    headerComponent: HideableHeader,   // ваш компонент на этой странице
    paginationPageSize: 20,
    cacheBlockSize: 20,
    maxBlocksInCache: 5,
    onGridReady: (params) => {
        params.api.setGridOption("loading", true);
        params.api.setGridOption("datasource", makeDatasource());
        wireButtons(params);
    },
});

const gridOptions = {
    ...baseOptions,
    columnDefs
};

const gridApi = agGrid.createGrid(gridDiv, gridOptions);

const modalToggle = () => {
    $('#modal-loading').modal('toggle');
};


$('#allDagToggle').on('click', function () {
    const $el = $(this);
    const active = $el.toggleClass('active').hasClass('active');

    $el
        .toggleClass('fa-toggle-on', active)
        .toggleClass('fa-toggle-off', !active);

    // Включить
    if (active) {
        toggleSelectedDags('unpauseDag');
    } else {
        // Выключить
        toggleSelectedDags('pauseDag');
    }
});

async function toggleSelectedDags(action) {
    modalToggle();
    const filterModel = gridApi.getFilterModel();
    const sortModel = AGGridUtils.getSortModelFromColumnState(gridApi);

    const resp = await fetch("/api/monitoring/get-ids", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": window.csrf_token
        },
        body: JSON.stringify({
            field: "id",
            filterModel,
            sortModel
        }),
    });

    if (!resp.ok) {
        let msg = `HTTP ${resp.status}`;
        try {
            const err = await resp.json();
            msg += err?.error ? `: ${err.error}` : "";
        } catch {
            const text = await resp.text().catch(() => "");
            if (text) msg += `: ${text}`;
        }
        throw new Error(msg);
    }

    const data = await resp.json();
    const ids = data.values || [];

    for (const id of ids) {
        let response = apiCall(action, id); // from .api/apiAirflow.js
        if (!response) {
            Swal.fire({
                icon: 'error',
                title: `По контролю ${id} запрос не выполнен`,
                position: 'top-end',
                showConfirmButton: false,
                toast: true,
                timer: 5000
            });
            const $toggle = $('#allDagToggle');
            const enabled = false;

            $toggle
                .toggleClass('fa-toggle-on', enabled)
                .toggleClass('fa-toggle-off', !enabled);
                
            setTimeout(modalToggle, 1000);
            break
        }
    };

    setTimeout(modalToggle, 1000);
};
