// utils.js (глобальный)

(function (w) {
    function getSortModelFromColumnState(api) {
        const state = api.getColumnState() || [];
        return state
            .filter(c => c.sort)
            .sort((a, b) => (a.sortIndex ?? 0) - (b.sortIndex ?? 0))
            .map(c => ({ colId: c.colId, sort: c.sort }));
    }

    async function exportCsvAll(params, options) {
        const {
            url,
            filename,
            teamId,
            csrfToken,
            extraBody = {},
        } = options;

        const api = params.api;
        const filterModel = api.getFilterModel();
        const sortModel = getSortModelFromColumnState(api);
        const visibleCols = (api.getAllDisplayedColumns() || []).map(c => c.getColId());

        const resp = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({
                teamId,
                filterModel,
                sortModel,
                visibleCols,
                ...extraBody,
            }),
        });

        if (!resp.ok) {
            console.error("Export failed", resp.status);
            return;
        }

        const blob = await resp.blob();
        const downloadUrl = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = filename || "export.csv";
        a.click();

        URL.revokeObjectURL(downloadUrl);
    }

    // фабрика базовых опций: зависимости передаются снаружи
    function createBaseGridOptions(opts) {
        const {
            headerComponent,       // например HideableHeader
            paginationPageSize = 20,
            cacheBlockSize = 20,
            maxBlocksInCache = 5,
            overlayLoadingTemplate,
            overlayNoRowsTemplate,
            onGridReady,           // ваша функция (на странице)
        } = opts || {};

        return {
            defaultColDef: {
                resizable: true,
                sortable: true,
                filter: true,
                floatingFilter: true,
                flex: 1,
                minWidth: 120,
                ...(headerComponent ? { headerComponent } : {}),
            },

            rowModelType: "infinite",

            pagination: true,
            paginationPageSize,

            cacheBlockSize,
            maxBlocksInCache,

            suppressAutoSize: true,

            overlayLoadingTemplate: overlayLoadingTemplate
                || '<div class="spinner-border text-success" style="width: 4rem; height: 4rem;"></div>',
            overlayNoRowsTemplate: overlayNoRowsTemplate || "Нет данных",

            rowSelection: {
                mode: "singleRow",
                enableClickSelection: false,
                checkboxes: false, 
            },

            // onGridReady пусть задаётся страницей, потому что datasource разный
            ...(onGridReady ? { onGridReady } : {}),
        };
    }

    function setHidden(element) {
        $(`#${element}`).prop('hidden', true);
        $(`#${element}`).css('display', 'none');
        return;
    };

    function removeHidden(element) {
        $(`#${element}`).prop('hidden', false);
        $(`#${element}`).css('display', 'inline-block');
        return;
    };

    // делаем доступным глобально
    w.AGGridUtils = {
        getSortModelFromColumnState,
        exportCsvAll,
        createBaseGridOptions,
        setHidden,
        removeHidden
    };
})(window);
