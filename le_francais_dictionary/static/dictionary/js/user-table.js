var dt;
var $globalCheckbox;
var $selectStars;
var $table = $('#wordsTable');
var style = getComputedStyle(document.body);
var checked_ids = [];


function showDeleted(checked) {
    if (checked) {
        let pattern = '^True|False$';
        dt.api().column(2).search(pattern, true, false).draw()
    } else {
        let pattern = '^False$';
        dt.api().column(2).search(pattern, true, false).draw()
    }
}


function emptyTable(s) {
    $table.find('tbody').empty().html(
        '<tr>' +
        '<td colspan="5" style="text-align:center">' +
        s +
        '</td>' +
        '</tr>');
}


function errorLoading() {
    emptyTable(
        '<div class="row">' +
        '<div class="col-12">' +
        '<h5 style="margin:1rem">' +
        'Ошибка :(' +
        '</h5>' +
        '</div> ' +
        '</div>'
    )
}


function tableReloading() {
    $table.find('tbody').empty().html(
        '<tr>' +
        '<td colspan="5" style="text-align:center">' +
        '<div class="row">' +
        '<div class="col-12">' +
        '<h5 style="margin:1rem">' +
        'Загружаем слова...' +
        '</h5>' +
        '</div>' +
        '<div class="col-12">' +
        '<img src="/static/images/loading_icon.gif">' +
        '</div>' +
        '</div>' +
        '</td>' +
        '</tr>'
    )
}

function updateTable() {
    let form = $('#filterWordsForm');
    let url = Urls['dictionary:my_words']();

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
                'dom':
                    /*"<'row'<'col-sm-12 col-md-6'f>>" + */"<'row'<'col-sm-12'tr>>" + "<'row'<'col-sm-12 col-md-12'i><'col-sm-12 col-md-5'l><'col-sm-12 col-md-7'p>>",
                'columnDefs': [
                    {
                        'targets': 0,
                        'render': function (data, type, row, meta) {
                            if (type === 'display') {
                                data = '<div class="checkbox"><input type="checkbox" class="dt-checkboxes"><label></label></div>';
                            }

                            return data;
                        },
                        'checkboxes': {
                            'selectRow': true,
                            'selectAllRender': '<div class="checkbox"><input type="checkbox" class="dt-checkboxes"><label></label></div>'
                        }
                    }
                ],
                'select': 'multi+shift',
                'searching': true,
                'ordering':  false,
                'paging': true,
                "pageLength": 50,
                "lengthMenu": [ [50, 100, 250, 500, -1], [50, 100, 250, 500, "Все"] ],
                "language": {
                    "processing": "Подождите...",
                    "search": "Поиск:",
                    "lengthMenu": "Показывать: _MENU_",
                    "info": "Слова с _START_ до _END_ из _TOTAL_",
                    "infoEmpty": "Слова с 0 до 0 из 0",
                    "infoFiltered": "(отфильтровано из _MAX_ записей)",
                    "infoPostFix": "",
                    "loadingRecords": "Загрузка слов...",
                    "zeroRecords": "Слова отсутствуют.",
                    "emptyTable": "В таблице отсутствуют данные",
                    "paginate": {
                        "first": "Первая",
                        "previous": "Предыдущая",
                        "next": "Следующая",
                        "last": "Последняя"
                    },
                    "aria": {
                        "sortAscending": ": активировать для сортировки столбца по возрастанию",
                        "sortDescending": ": активировать для сортировки столбца по убыванию"
                    },
                    "select": {
                        "rows": {
                            "_": "Выбрано слов: %d",
                            "0": "Кликните по слову для выбора",
                            "1": "Выбрано одно слово"
                        }
                    }
                },
                initComplete: function () {
                    dt = this;
                    // adding star filter
                    this.api().columns(-1).every(function () {
                        var column = this;
                        $(column.header()).empty();
                        $(starFilterHtml).appendTo($(column.header())).selectpicker({
                            'noneSelectedText': "Оценка",
                            'header': 'Оценка',
                            'selectedTextFormat': 'count > 1',
                        }).on('change', function () {
                            let pattern = $(this).find(':selected').map(function () {
                                return $(this).text()
                            }).get().join('|');
                            if (pattern === ''){
                                dt.api().column(-1).search(pattern, false, true).draw();
                            }else {
                                pattern = `^${pattern}$`;
                                dt.api().column(-1).search(pattern, true, false).draw();
                            }
                        });
                        $selectStars = $('#starFilter');
                    });
                    showDeleted($('#showDeleted')[0].checked);
                    $('#showDeleted').on('change', function (e) {
                        e.preventDefault();
                        showDeleted(this.checked)
                    })
                }
            })
        },
        error: errorLoading,
        beforeSend: tableReloading,
    });

    $('.undertable').show();
    $('.uppertable').show();
}

function get_selected(dt){
    let rows_selected = dt.api().column(0).checkboxes.selected();
    let ids = [];
    $.each(rows_selected, function(index, rowId){
         // Create a hidden element
        ids.push(rowId)
      });
    return ids
}

$(document).ready(function () {
    $('#filterWordsForm').submit(function (ev) {
        ev.preventDefault();
        updateTable();
    });
    $('#startApp').on('click', function () {
        $.ajax(Urls['dictionary:app'](), {
            type: 'POST',
            contentType: "application/json",
            dataType: "json",
            data: JSON.stringify({
                words: get_selected(dt),
                csrfmiddlewaretoken: csrf,
            }),
            error: errorLoading,
            success: function (r) {
                window.location.href = Urls['dictionary:app']()
            },
            beforeSend: emptyTable('')

        })
    });
    $('#markWords').on('click', function () {
        var rows_selected = dt.api().column(0).checkboxes.selected();
       $.ajax(Urls['dictionary:mark_words'](), {
           type: 'POST',
            contentType: "application/json",
            dataType: "json",
            data: JSON.stringify({
                words: get_selected(dt),
                csrfmiddlewaretoken: csrf,
            }),
            success: function (r) {
                updateTable()
            },
           error: errorLoading,
           beforeSend: tableReloading,
       })
    });
    $('#unmarkWords').on('click', function () {
        var rows_selected = dt.api().column(0).checkboxes.selected();
       $.ajax(Urls['dictionary:unmark_words'](), {
           type: 'POST',
            contentType: "application/json",
            dataType: "json",
            data: JSON.stringify({
                words: get_selected(dt),
                csrfmiddlewaretoken: csrf,
            }),
            success: function (r) {
                updateTable()
            },
           error: errorLoading,
           beforeSend: tableReloading,
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
});
