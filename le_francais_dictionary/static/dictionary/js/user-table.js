var dt;
var $globalCheckbox;
var $selectStars;
var $table = $('#wordsTable');
var style = getComputedStyle(document.body);
var checked_ids = [];


function updateTable() {
    let form = $('#filterWordsForm');
    let url = Urls['dictionary:manage_words']();

    $.ajax(url, {
        type: 'POST',
        dataType: 'json',
        data: form.serialize(),
        success: function (r) {
            $table.html(r.table);
            if (dt !== undefined) {
                dt.api().destroy();
                $selectStars.remove();
            }
            $table.DataTable({
                'columnDefs': [
                    {
                        'targets': 0,
                        'checkboxes': {
                            'selectRow': true
                        }
                    }
                ],
                'select': {
                    'style': 'multi+shift'
                },
                'searching': false,
                'ordering':  false,
                'paging': false,
                initComplete: function () {
                    dt = this;
                    // adding star filter
                    this.api().columns(-1).every(function () {
                        var column = this;
                        $(column.header()).empty();
                        $(starFilterHtml).appendTo($(column.header())).selectpicker({
                            'noneSelectedText': "Оценка",
                            'selectedTextFormat': 'static',
                            'header': 'Оценка',
                        }).on('change', function () {
                            let pattern = $(this).find(':selected').map(function () {
                                return $(this).text()
                            }).get().join('|');
                            column.search(pattern, true, false).draw();
                        });
                        $selectStars = $('#starFilter');
                    });
                }
            })
        }
    })
}

$(document).ready(function () {
    $('#filterWordsForm').submit(function (ev) {
        ev.preventDefault();
        updateTable();
    });
    $('#startApp').on('click', function () {
        $.ajax(Urls['dictionary:standalone'](), {
            type: 'POST',
            contentType: "application/json",
            dataType: "json",
            data: JSON.stringify({
                ids: checked_ids,
                csrfmiddlewaretoken: csrf,
            }),
            success: function (r) {
                window.location.href = Urls['dictionary:standalone']()
            }
        })
    });
    // Handle form submission event
    $('#main-frm').on('submit', function (e) {
        var form = this;

        var rows_selected = dt.api().column(0).checkboxes.selected();

        // Iterate over all selected checkboxes
        $.each(rows_selected, function (index, rowId) {
            // Create a hidden element
            $(form).append(
                $('<input>')
                    .attr('type', 'hidden')
                    .attr('name', 'id[]')
                    .val(rowId)
            );
        });
        // Prevent actual form submission
        e.preventDefault();
    });
    $('#markWords').on('click', function () {
        $.ajax(Urls['dictionary:mark_words'](), {
            type: 'POST',
            contentType: "application/json",
            dataType: "json",
            data: JSON.stringify({
                'words': checked_ids
            }),
            success: function (r) {
                updateTable()
            }
        })
    });
    // $('#forgetWords').on('click', function () {
    //     $.ajax(Urls['dictionary:mark_words'](), {
    //         type: 'POST',
    //         contentType: "application/json",
    //         dataType: "json",
    //         data: JSON.stringify({
    //             'words': ft.rows.array.filter(row => row.value._selection === "True").map(row => row.value.id)
    //         }),
    //         success: function (r) {
    //             updateTable()
    //         }
    //     })
    // });
});
