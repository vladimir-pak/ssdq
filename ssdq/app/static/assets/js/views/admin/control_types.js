/* DataTable start */
const columns = [
    {data: 'id'},
    {data: 'name'},
    {data: 'description'},
    {
        data: 'deleted_flag',
        render: function (data) {
            return data == 'Y' ? 'Да' : 'Нет';
        }
    }
];

const attr = ['id', 'name', 'description'];
const toggleActiveList = ['update', 'remove', 'hardRemove'];
const toggleDeletedList = ['restore'];

var dataTab = new dataTableHandler(
    'controlTypes',
    columns,
    `api/admin/control-types`,
    'add',
    toggleActiveList,
    true,
    3,
    toggleDeletedList
);
dataTab.setTableDelay();
dataTab.setRowHandler(attr);

var myTable = dataTab.getTable();

/* DataTable end */

/* Ajax to back for CRUD (start) */
const requiredAttributes = ['name', 'description'];

var postRequests = new postRequests(
    'ControlType',
    'Тип контроля',
    ['id', 'name', 'description']
);

$('#add, #update, #remove, #hardRemove, #restore').on('click', function() {
    if (!postRequests.verifyFileds(requiredAttributes)) {
        return;
    };

    postRequests.postRequest(
        'api/admin/control-types' + (this.id != "add" ? `/${$("#id").val()}` : ""),
        this.id,
        this.id == 'hardRemove' ? 'hardDelete=True' : undefined,
        this.id == "add" ? "PUT" : undefined
    );
    dataTab.resetButtons(attr);
    myTable.draw();
});
