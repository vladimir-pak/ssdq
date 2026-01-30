const gridDiv = document.querySelector("#sourcesGrid");

const toggleActiveList = ['update', 'remove', 'hardRemove'];
const toggleDeletedList = ['restore'];

const columnDefs = [
    { headerName: "ID", field: "id", colId: "id", filter: "agTextColumnFilter" },
    { headerName: "Наименование", field: "name", colId: "name", filter: "agTextColumnFilter" },
    { headerName: "Описание", field: "description", colId: "description", filter: "agTextColumnFilter" },
    { headerName: "Хост", field: "host", colId: "host", filter: "agTextColumnFilter" },
    { headerName: "Порт", field: "port", colId: "port", filter: "agTextColumnFilter" },
    { headerName: "БД", field: "db_name", colId: "db_name", filter: "agTextColumnFilter" },
    { headerName: "Тип СУБД", field: "dbtype", colId: "dbtype", filter: "agTextColumnFilter" },
    { headerName: "SSL mode", field: "sslmode", colId: "sslmode", filter: "agTextColumnFilter" },
    {
        headerName: "Удален",
        field: "deleted_flag",
        colId: "deleted_flag",
        filter: "agTextColumnFilter",
        width: 120,
    }
];

const rowHandler = (data, event) => {
    if (data) {
        $('#id').val(data.id);
        $('#name').val(data.name);
        $('#description').val(data.description);
        $('#host').val(data.host);
        $('#port').val(data.port);
        $('#db_name').val(data.db_name);
        $('#dbtype').val(data.dbtype);
        $('#sslmode').val(data.sslmode);
    } else {
        $('#id').val('');
        $('#name').val('');
        $('#description').val('');
        $('#host').val('');
        $('#port').val('');
        $('#db_name').val('');
        $('#sslmode').val('');
    }

    if (event) {
        window.AGGridUtils.setHidden('add');
        deleted = data.deleted_flag == 'Y' ? true : false;

        toggleActiveList.forEach((element) => {
            deleted ? window.AGGridUtils.setHidden(element) : window.AGGridUtils.removeHidden(element);
        });
        toggleDeletedList.forEach((element) => {
            deleted ? window.AGGridUtils.removeHidden(element) : window.AGGridUtils.setHidden(element);
        });
    } else {
        toggleActiveList.forEach((element) => {
            window.AGGridUtils.setHidden(element);
        });
        toggleDeletedList.forEach((element) => {
            window.AGGridUtils.setHidden(element);
        });
        window.AGGridUtils.removeHidden('add');
    }
}

function makeDatasource() {
    return {
        getRows: async (params) => {
            try {
                const body = {
                    startRow: params.startRow,
                    endRow: params.endRow,
                    sortModel: params.sortModel,
                    filterModel: params.filterModel,
                };

                const resp = await fetch("/api/admin/sources", {
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
            url: "/api/admin/sources/csv",
            filename: "dq_source_sdim.csv",
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
    columnDefs,
    onRowClicked: (event) => {
        const node = event.node;
        if (node.isSelected()) {
            node.setSelected(false);
            rowHandler(null);
        } else {
            event.api.deselectAll();
            node.setSelected(true);
            rowHandler(event.data, event);
        }
    },
};

const gridApi = agGrid.createGrid(gridDiv, gridOptions);

/* Ajax to back for CRUD */
const inputAttributes = ['id', 'name', 'description', 'host', 'port', 'db_name', 'dbtype', 'sslmode'];
const requiredAttributes = ['name', 'description', 'host', 'port', 'dbtype'];

var postRequests = new postRequests(
    'Sources',
    'Источник',
    inputAttributes
);

$('#add, #update, #remove, #hardRemove, #restore').on('click', function() {
    if (!postRequests.verifyFileds(requiredAttributes)) {
        return;
    };

    postRequests.postRequest(
        `api/admin/sources` + (this.id != "add" ? `/${$("#id").val()}` : ""), 
        this.id,
        this.id == 'hardRemove' ? 'hardDelete=True' : undefined,
        this.id == "add" ? "PUT" : undefined
    );
    inputAttributes.filter(item => item !== 'dbtype').forEach(e => {
        $(`#${e}`).val('');
    });
    rowHandler(null);
    gridApi.setGridOption("datasource", makeDatasource());
    gridApi.paginationGoToFirstPage();
});
