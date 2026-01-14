/* DataTable start */
const columns = [
    {data: 'id'},
    {data: 'name'},
    {data: 'description'},
    {data: 'host'},
    {data: 'port'},
    {data: 'db_name'},
    {data: 'dbtype'},
    {data: 'sslmode'},
    {
        data: 'deleted_flag',
        render: function (data) {
            return data == 'Y' ? 'Да' : 'Нет';
        }
    },
];

const attr = ['id', 'name', 'description', 'host', 'port', 'db_name', 'dbtype', 'sslmode'];
const toggleActiveList = ['update', 'remove', 'hardRemove'];
const toggleDeletedList = ['restore'];

var dataTab = new dataTableHandler(
    'sources',
    columns,
    `api/admin/sources`,
    'add',
    toggleActiveList,
    true,
    6,
    toggleDeletedList
);
dataTab.setTableDelay();
dataTab.setRowHandler(attr);

var myTable = dataTab.getTable();

/* DataTable end */

/* Ajax to back for CRUD (start) */
const requiredAttributes = ['name', 'description', 'host', 'port', 'dbtype'];

var postRequests = new postRequests(
    'Sources',
    'Источник',
    ['id', 'name', 'description', 'host', 'port', 'db_name', 'dbtype', 'sslmode']
);

$('#add, #update, #remove, #hardRemove, #restore').on('click', function() {
    if (!postRequests.verifyFileds(requiredAttributes)) {
        return;
    };

    postRequests.postRequest(
        'api/admin/sources' + (this.id != "add" ? `/${$("#id").val()}` : ""),
        this.id,
        this.id == 'hardRemove' ? 'hardDelete=True' : undefined,
        this.id == "add" ? "PUT" : undefined
    );
    dataTab.resetButtons(attr);
    myTable.draw();
});
