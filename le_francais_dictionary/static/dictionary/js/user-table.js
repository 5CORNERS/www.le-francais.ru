var ft;
var $globalCheckbox;
var $table = $('#wordsTable');
var style = getComputedStyle(document.body);

function getStars(rating) {

  rating = Math.round(rating * 2) / 2;
  let output = [];

  for (var i = rating; i >= 1; i--)
    output.push(`<i class="fas fa-star" aria-hidden="true" style="color:${style.getPropertyValue('--blue')};"></i>&nbsp;`);

  if (i === .5) output.push(`<i class="fas fa-star-half-alt" aria-hidden="true" style="color:${style.getPropertyValue('--blue')};"></i>&nbsp;`);

  for (let i = (5 - rating); i >= 1; i--)
    output.push(`<i class="far fa-star" aria-hidden="true" style="color:${style.getPropertyValue('--blue')};"></i>&nbsp;`);

  return output.join('');
}

function getSignal(n) {
    return `<i class="signal signal-${n}"></i>`
}

function getBars(rating) {
    rating = Math.round(rating);
    let output = [];
    for (let i = 0; i<rating; i++){
        if(i<5){
            output.push(`<span style="color:${style.getPropertyValue('--danger')}">|</span>`)
        }else if(i<15){
            output.push(`<span style="color:${style.getPropertyValue('--warning')}">|</span>`)
        }else{
            output.push(`<span style="color:${style.getPropertyValue('--success')}">|</span>`)
        }
    }
    for (let i= 20 - rating; i >= 0; i--){
        output.push(`<span style="color:#a2a9b0">|</span>`)
    }
    return output.join('')

}

function fillTable(wordsData) {
    wordsData.rows.forEach(function (item, index, array) {
        wordsData.rows[index].difficulty = getBars(item.difficulty);
        wordsData.rows[index].repetitions = getSignal(item.repetitions);
        if (item.deleted === 'true'){
            wordsData.rows[index].style = {'text-decoration': 'line-through'}
        }
    });
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
        return
    }
    //On Global Checkbox Toggle, set all rows' checkbox to checked and toggle _selection values
    $table.on('change', '.global-checkbox', function (ev) {
        ev.preventDefault();
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
    $table.on('click', '.row-checkbox', function (ev) {
        ev.preventDefault();
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
    $('.undertable').show()
}

function updateTable() {
    let form = $('#filterWordsForm');
    let url = Urls['dictionary:manage_words']();

    $.ajax(url, {
        type: 'POST',
        data: form.serialize(),
        success: function (r) {
            fillTable(r.table);
        }
    })
}

$(document).ready(function () {
    $('#filterWordsForm').submit(function (ev) {
        ev.preventDefault();
        updateTable();
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
    });
    $('#markWords').on('click', function () {
       $.ajax(Urls['dictionary:mark_words'](), {
            type: 'POST',
            contentType: "application/json",
            dataType: "json",
            data: JSON.stringify({
                'words': ft.rows.array.filter(row => row.value._selection === "True").map(row => row.value.id)
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
