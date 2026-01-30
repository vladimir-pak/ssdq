const gridDiv = document.querySelector("#usersGrid");

const columnDefs = [
    { headerName: "ID", field: "id", colId: "id", filter: "agTextColumnFilter" },
    { headerName: "ФИО", field: "name", colId: "name", filter: "agTextColumnFilter" },
    { headerName: "email", field: "email", colId: "email", filter: "agTextColumnFilter" },
    { headerName: "role_id", field: "role_id", colId: "role_id", filter: "agTextColumnFilter", hide: true },
    { headerName: "Роль", field: "role_name", colId: "role_name", filter: "agTextColumnFilter" },
    { headerName: "team_id", field: "team_id", colId: "team_id", filter: "agTextColumnFilter", hide: true },
    { headerName: "Команда", field: "team_name", colId: "team_name", filter: "agTextColumnFilter" }
];

const rowHandler = (data, event) => {
    if (data) {
        $('#id').val(data.id);
        $('#name').val(data.name);
        $('#email').val(data.email);
        $('#role').val(data.role_id);
        $('#team_id').val(data.team_id);
    } else {
        $('#id').val('');
        $('#name').val('');
        $('#email').val('');
        $('#team_id').val('');
    }
}

function makeDatasource() {
    return {
        getRows: async (params) => {
            try {
                const body = {
                    teamId: $("#team_id").val(),
                    startRow: params.startRow,
                    endRow: params.endRow,
                    sortModel: params.sortModel,
                    filterModel: params.filterModel,
                };

                const resp = await fetch("/api/admin/users", {
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
            url: "/api/admin/users/csv",
            filename: "users.csv",
            teamId: $("#team_id").val(),
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

$("#team_id").on("change", () => {
    gridApi.setGridOption("datasource", makeDatasource());
    gridApi.paginationGoToFirstPage();
});

/* Ajax to back for CRUD */
const inputAttributes = ['id', 'name', 'email', 'role', 'team_id'];
const requiredAttributes = ['name', 'email', 'role', 'team_id'];

var postRequests = new postRequests(
    'Users',
    'Пользователь',
    inputAttributes
);

$('#update, #hardRemove').on('click', function() {
    if (!postRequests.verifyFileds(requiredAttributes)) {
        return;
    };

    postRequests.postRequest(
        `api/admin/users/${$("#id").val()}`, 
        this.id
    );
    inputAttributes.filter(item => item !== 'team_id').forEach(e => {
        $(`#${e}`).val('');
    });
    rowHandler(null);
    gridApi.setGridOption("datasource", makeDatasource());
    gridApi.paginationGoToFirstPage();
});
