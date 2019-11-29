var ft;
var $globalCheckbox;
var $table = $('#wordsTable');
var style = getComputedStyle(document.body);
var checked_ids = [];

(function($, F){

    // Extend the Row.$create method to add an id attribute to each <tr>.
    F.Row.extend("$create", function(){
        // call the original method
        this._super();
        // get the current row values
        var values = this.val();
        // then add whatever attributes are required
        this.$el.attr({"data-id": values["id"]});
    });

})(jQuery, FooTable);

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
        wordsData.rows[index].difficulty.value = getStars(item.difficulty.value);
        wordsData.rows[index].repetitions.value = getSignal(item.repetitions.value);
        wordsData.rows[index]._checkbox.options = {'id': wordsData.rows[index].id.value};
        if (item.deleted === 'true'){
            wordsData.rows[index].word.options.classes = 'deleted';
            wordsData.rows[index].translation.options.classes = 'deleted';
        }
    });
    if (!ft) {
        ft = FooTable.init('#wordsTable', wordsData);
    } else {
        ft.loadRows(wordsData.rows);
        return
    }
    $table.on('postdraw.ft.table', function (e) {
        $table.simpleCheckboxTable({
            onCheckedStateChanged: function ($checkbox) {
                $checkbox.each(
                    function () {
                        let id = $(this).parent().parent().data('id');
                        let i = checked_ids.indexOf(id);
                        if(i === -1 && this.checked){
                            checked_ids.push(id)
                        }else if(i > -1 && !this.checked){
                            checked_ids.splice(i, 1)
                        }
                        console.log(id, checked_ids)
                    }
                )
            }
        })
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
                ids: checked_ids,
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
