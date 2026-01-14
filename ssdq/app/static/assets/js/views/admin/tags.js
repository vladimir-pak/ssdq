/* DataTable start */
const columns = [
    {data: 'id'},
    {data: 'name'},
    {data: 'description'}
];

const attr = ['id', 'name', 'description'];
const toggleActiveList = ['update', 'remove'];
var team_id = $('#team_id').val();

var dataTab = new dataTableHandler(
    'tags',
    columns,
    `api/admin/tags?teamId=${team_id}`,
    'add',
    toggleActiveList
);
dataTab.setTableDelay();
dataTab.setRowHandler(attr);

var myTable = dataTab.getTable();

/* DataTable end */

/* Ajax to back for CRUD (start) */
const requiredAttributes = ['name', 'description'];

var postRequests = new postRequests(
    'Tags',
    'Теги',
    ['id', 'team_id', 'name', 'description']
);

$('#add, #update, #remove').on('click', function() {
    if (!postRequests.verifyFileds(requiredAttributes)) {
        return;
    };

    postRequests.postRequest(
        'api/admin/tags' + (this.id != "add" ? `/${$("#id").val()}` : ""), 
        this.id,
        undefined,
        this.id == "add" ? "PUT" : undefined
    );
    dataTab.resetButtons(attr);
    myTable.draw();
});

$('#team_id').on('change', function() {
    team_id = $(this).val();
    myTable.ajax.url(`/api/admin/tags?teamId=${team_id}`);
    toggleActiveList.forEach((e) => {dataTab.setHidden(e)});
    dataTab.removeHidden('add');
    myTable.ajax.reload();
    //myTable.draw();
});
