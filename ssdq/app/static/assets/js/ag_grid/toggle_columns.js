class HideableHeader {
    init(params) {
        this.params = params;

        const eGui = document.createElement("div");
        eGui.className = "ag-custom-header";

        const title = document.createElement("span");
        title.className = "ag-custom-header-title";
        title.textContent = params.displayName ?? "";

        // ✅ Клик по заголовку => сортировка
        title.addEventListener("click", (e) => {
            params.progressSort(e.shiftKey); // shift = multi-sort
        });

        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "ag-custom-header-hidebtn btn btn-link";
        btn.title = "Скрыть колонку";
        btn.innerHTML = `<i class="fas fa-minus"></i>`;

        // Спрятать колонки
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            params.api.setColumnsVisible([params.column.getColId()], false);
        });

        eGui.appendChild(title);
        eGui.appendChild(btn);

        this.eGui = eGui;
    }

    getGui() {
        return this.eGui;
    }

    refresh() {
        return false;
    }
}
