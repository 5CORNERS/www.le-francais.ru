var ft;
var $globalCheckbox;
var $table = $('#wordsTable');

function fillTable(wordsData) {
    if (!ft) {
        ft = FooTable.init('#wordsTable', wordsData);
    } else {
        $globalCheckbox = $table.find('.global-checkbox').eq(0);
        let data = wordsData.rows;
        data.forEach(function (item, index, array) {
            if ($globalCheckbox.prop('checked')) {
                data[index]._selection = 'True';
                data[index]._checkbox = '<input type="checkbox" class="row-checkbox" checked >';
            } else {
                data[index]._selection = 'False';
                data[index]._checkbox = '<input type="checkbox" class="row-checkbox">';
            }
        });
        ft.loadRows(wordsData.rows);
    }
    //On Global Checkbox Toggle, set all rows' checkbox to checked and toggle _selection values
    $table.on('change', '.global-checkbox', function () {
        var newValues = {};
        if ($(this).prop("checked")) {
            newValues._selection = 'True';
            newValues._checkbox = '<input type="checkbox" class="row-checkbox" checked>';
        } else {
            newValues._selection = 'False';
            newValues._checkbox = '<input type="checkbox" class="row-checkbox">';
        }
        $.each(ft.rows.all, function (index, values) {
            ft.rows.update(index, newValues, false);
        });
        ft.draw();
    });
    //On Single Row Checkbox Toggle
    $table.on('click', '.row-checkbox', function () {
        $globalCheckbox = $table.find('.global-checkbox').eq(0);
        var newValues = {};
        var row = $(this).closest('tr').data('__FooTableRow__');
        if ($(this).prop('checked')) {
            //Prepare Values
            newValues._selection = 'True';
            newValues._checkbox = '<input type="checkbox" class="row-checkbox" checked>';
        } else {
            //Prepare Values
            newValues._selection = 'False';
            newValues._checkbox = '<input type="checkbox" class="row-checkbox">';

            //Toggle globalCheckbox if checked
            if ($globalCheckbox.prop('checked')) {
                $globalCheckbox.prop('checked', false);
            }
        }
        row.val(newValues, true);
    });
    $('#startApp').show()
}

$(document).ready(function () {
    $('#filterWordsForm').submit(function (ev) {
        ev.preventDefault();
        let form = $(this);
        let url = Urls['dictionary:manage_words']();

        $.ajax(url, {
            type: 'POST',
            data: form.serialize(),
            success: function (r) {
                fillTable(r);
            }
        })
    });
    if (getTable) {
        fillTable(getTable)
    }
    $('#startApp').on('click', function () {
        $.ajax(Urls['dictionary:standalone'](), {
            type: 'POST',
            contentType: "application/json",
            dataType: "json",
            data: JSON.stringify({
                ids: ft.rows.array.filter(row => row.value._selection === "True").map(row => row.value.id),
                csrfmiddlewaretoken: csrf,
            }),
            success: function (r) {
                window.location.href=Urls['dictionary:standalone']()
            }
        })
    })
});
