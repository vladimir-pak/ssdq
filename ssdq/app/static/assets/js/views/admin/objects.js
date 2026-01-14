/* DataTable start */
const columns = [
    {data: 'id'},
    {data: 'base_name'},
    {data: 'schema'},
    {data: 'table_name'},
    {data: 'description'},
    {
        data: 'deleted_flag',
        render: function (data) {
            return data == 'Y' ? 'Да' : 'Нет';
        }
    }
];

const attr = ['id', 'base_name', 'schema', 'table_name', 'description'];
const toggleActiveList = ['update', 'remove', 'hardRemove'];
const toggleDeletedList = ['restore'];

var dataTab = new dataTableHandler(
    'objects',
    columns,
    `api/admin/objects`,
    'add',
    toggleActiveList,
    true,
    5,
    toggleDeletedList
);
dataTab.setTableDelay();
dataTab.setRowHandler(attr);

var myTable = dataTab.getTable();

/* DataTable end */

/* Ajax to back for CRUD (start) */
const requiredAttributes = ['base_name', 'schema', 'table_name', 'description'];

var postRequests = new postRequests(
    'Objects',
    'Объект БД',
    ['id', 'base_name', 'schema', 'table_name', 'description']
);

$('#add, #update, #remove, #hardRemove, #restore').on('click', function() {
    if (!postRequests.verifyFileds(requiredAttributes)) {
        return;
    };

    postRequests.postRequest(
        'api/admin/objects' + (this.id != "add" ? `/${$("#id").val()}` : ""),
        this.id,
        this.id == 'hardRemove' ? 'hardDelete=True' : undefined,
        this.id == "add" ? "PUT" : undefined
    );
    dataTab.resetButtons(attr);
    myTable.draw();
});
