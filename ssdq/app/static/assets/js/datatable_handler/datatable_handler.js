/**
 * Class for handling DataTable
 * @param {string} tabElementId [table's element ID]
 * @param {Map} cols [Map of DataTable's columns]
 * @param {string} endpoint [endpoint for GET request to fill DataTable via AJAX]
 * @param {boolean} deletable [True if dictionary is deletable]
 * @param {number} deletedColIndex [Index of deleted_flag column]
 */
window.dataTableHandler = class DataTableHandler {
    /**
     * 
     * @param {string} tabElementId [table's element ID]
     * @param {Set} cols [Map of DataTable's columns]
     * @param {string} endpoint [endpoint for GET request to fill DataTable via AJAX]
     * @param {string} addElement [element ID with add entity button]
     * @param {Array<string>} toggleList [list of elements ID to display when a row of DataTable is selected]
     * @param {boolean} deletable [True if dictionary is deletable]
     * @param {number} deletedColIndex [Index of deleted_flag column]
     * @param {Array<string>} toggleDeletedList [list of elements ID to display when a row of DataTable is selected with deleted flag]
     */
    constructor(
        tabElementId, 
        cols, 
        endpoint,
        addElement,
        toggleList,
        deletable=false,
        deletedColIndex=undefined,
        toggleDeletedList=undefined
    ) {
        this.endpoint = endpoint;
        this.addElement = addElement;
        this.toggleList = toggleList;
        this.deletable = deletable;
        this.deletedColIndex = deletedColIndex;
        this.toggleDeletedList = toggleDeletedList;
        this.url = window.location.protocol + '//' + window.location.host;

        this.table = new DataTable("#"+tabElementId, {
            language: {
                url: '/static/assets/ru.json'
            },
            processing: true,
            serverSide: true,
            serverMethod: 'post',
            ajax: {
                url: `${this.url}/${this.endpoint}`,
                headers: {"X-CSRFToken": csrf_token},
            },
            lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
            searching: true,
            sort: true,
            order: [0,'asc'],
            autoWidth: false,
            responsive: false,
            columns: cols,
            aaSorting: ['asc', 'desc'],
            oLanguage: {
                sProcessing: `<div class="spinner-border text-success" style="width: 6rem; height: 6rem;"></div>`,
                sEmptyTable: "Нет данных"
            }
        });
    };

    getTable() {
        return this.table;
    };

    setTableDelay() {
        const delay = (callback, ms) => {
            var timer = 0;
            return function () {
                var context = this, args = arguments;
                clearTimeout(timer);
                timer = setTimeout(function () {
                    callback.apply(context, args);
                }, ms || 0);
            };
        };
        let myTab = this.table;
    
        $('.dataTables_filter input')
        .unbind() // Unbind previous default bindings
        .bind('input', (delay(function (e) { // Bind our desired behavior
            myTab.search($(this).val()).draw();
            return;
        }, 400))); // Set delay in milliseconds
    };

    toggleHidden(element) {
        $(`#${element}`).toggle();
        return;
    };
    
    setHidden(element) {
        $(`#${element}`).prop('hidden', true);
        $(`#${element}`).css('display', 'none');
        return;
    };
    
    removeHidden(element) {
        $(`#${element}`).prop('hidden', false);
        $(`#${element}`).css('display', 'inline-block');
        return;
    };

    /**
     * 
     * @param {Array<string>} attr [list of attributes from POST form]
     * @param {function} customFunc [custom function after all]
     */
    setRowHandler(
        attr,
        customSelectedFunc=undefined,
        customFunc=undefined
    ) {
        this.table.on('click', 'tbody tr', (e) => {
            let deleted = false;
            let classList = e.currentTarget.classList;
        
            if (classList.contains('selected')) {
                classList.remove('selected');
    
                this.removeHidden(this.addElement);
    
                if (this.deletable) {
                    this.toggleList.forEach((element) => {
                        this.setHidden(element);
                    });
                    this.toggleDeletedList.forEach((element) => {
                        this.setHidden(element);
                    });
                } else {
                    this.toggleList.forEach((element) => {
                        this.setHidden(element);
                    });
                };
    
                attr.forEach((element, i) => {
                    $(`#${element}`).val(undefined);
                });
            } else {
                this.table.rows('.selected').nodes().each((row) => row.classList.remove('selected'));
                classList.add('selected');
    
                this.setHidden(this.addElement);
                
                if (this.deletable) {
                    deleted = e.currentTarget.cells[this.deletedColIndex].innerText == 'Да' ? true : false;
    
                    this.toggleList.forEach((element) => {
                        deleted ? this.setHidden(element) : this.removeHidden(element);
                    });
                    this.toggleDeletedList.forEach((element) => {
                        deleted ? this.removeHidden(element) : this.setHidden(element);
                    });
                } else {
                    this.toggleList.forEach((element) => {
                        this.removeHidden(element);
                    });
                };
                
                attr.forEach((element, i) => {
                    $(`#${element}`).val(e.currentTarget.cells[i].innerText);
                });

                if (customSelectedFunc) {
                    customSelectedFunc();
                };
            };

            if (customFunc) {
                customFunc();
            };
        });
        return;
    };

    resetButtons(attr) {
        this.removeHidden(this.addElement);
        this.toggleList.forEach((element) => {
            this.setHidden(element);
        });
        if (this.deletable) {
            this.toggleDeletedList.forEach((element) => {
                this.setHidden(element);
            });
        };

        attr.forEach((element, i) => {
            $(`#${element}`).val(undefined);
        });
    };
};
