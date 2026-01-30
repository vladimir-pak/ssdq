const gridDiv = document.querySelector("#teamAttributesGrid");

const toggleActiveList = ['update', 'hardRemove'];

const columnDefs = [
    { headerName: "ID", field: "id", colId: "id", filter: "agTextColumnFilter" },
    { headerName: "Наименование", field: "name", colId: "name", filter: "agTextColumnFilter" },
    { headerName: "Описание", field: "description", colId: "description", filter: "agTextColumnFilter" },
    { 
        headerName: "Обязательность заполнения",
        field: "is_required",
        colId: "is_required",
        filter: "agTextColumnFilter",
        valueFormatter: p => p.value ? "Да" : "Нет",
        filterParams: {
            filterOptions: ["equals", "notEqual", "blank", "notBlank"]
        }
    }
];

const rowHandler = (data, event) => {
    if (data) {
        $('#id').val(data.id);
        $('#name').val(data.name);
        $('#description').val(data.description);
        $('#is_required').prop('checked', data.is_required);
    } else {
        $('#id').val('');
        $('#name').val('');
        $('#description').val('');
        $('#is_required').prop('checked', false);
    }

    if (event) {
        window.AGGridUtils.setHidden('add');
        deleted = data.deleted_flag == 'Y' ? true : false;

        toggleActiveList.forEach((element) => {
            deleted ? window.AGGridUtils.setHidden(element) : window.AGGridUtils.removeHidden(element);
        });
    } else {
        toggleActiveList.forEach((element) => {
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
                    teamId: $("#team_id").val(),
                    startRow: params.startRow,
                    endRow: params.endRow,
                    sortModel: params.sortModel,
                    filterModel: params.filterModel,
                };

                const resp = await fetch("/api/admin/team-attributes", {
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
            url: "/api/admin/team-attributes/csv",
            filename: "team_attributes.csv",
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
const inputAttributes = ['id', 'team_id', 'name', 'description', 'is_required'];
const requiredAttributes = ['name', 'description'];

var postRequests = new postRequests(
    'TeamAttributes',
    'Атрибуты карточки контроля',
    inputAttributes
);

$('#add, #update, #hardRemove').on('click', function() {
    if (!postRequests.verifyFileds(requiredAttributes)) {
        return;
    };

    postRequests.postRequest(
        `api/admin/team-attributes` + (this.id != "add" ? `/${$("#id").val()}` : ""), 
        this.id,
        this.id == 'hardRemove' ? 'hardDelete=True' : undefined,
        this.id == "add" ? "PUT" : undefined
    );
    inputAttributes.filter(item => item !== 'team_id').forEach(e => {
        $(`#${e}`).val('');
    });
    rowHandler(null);
    gridApi.setGridOption("datasource", makeDatasource());
    gridApi.paginationGoToFirstPage();
});
