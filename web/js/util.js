var TODAY = new Date();
var YESTERDAY = new Date(TODAY.getTime() - 2 * 24 * 60 * 60 * 1000);
var NEXT_WEEK = new Date(TODAY.getTime() + 7 * 24 * 60 * 60 * 1000);


function search(table_id) {
    var input, filter, table, tr, td, i;

    input = document.getElementById(table_id);
    filter = input.value.toUpperCase();

    table = document.getElementById("table");
    tr = table.getElementsByTagName("tr");

    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[0];

        if (td) {
            if (td.innerHTML.toUpperCase().indexOf(filter) > -1)
                tr[i].style.display = "";
            else
                tr[i].style.display = "none";
        }
    }
}
