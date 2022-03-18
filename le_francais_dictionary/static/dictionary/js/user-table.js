let dt;
let $globalCheckbox;
let $selectStars;
let $table = $('#wordsTable');
let style = getComputedStyle(document.body);
let checked_ids = [];
let colorCodingEnabled = true;

const isVerbs = function () {
    return tableType === "verbs"
}

function showDeleted(checked) {
    if (checked) {
        let pattern = '^True|False$';
        dt.api().column(2).search(pattern, true, false).draw()
    } else {
        let pattern = '^False$';
        dt.api().column(2).search(pattern, true, false).draw()
    }
    switchColorCoding(colorCodingEnabled)
}

function hideRegular(checked) {
    if (checked) {
        let pattern = '^False$';
        dt.api().column(3).search(pattern, true, false).draw()
    } else {
        let pattern = '^True|False$';
        dt.api().column(3).search(pattern, true, false).draw()
    }
}

function hideNegative(checked) {
    if (checked) {
        let pattern = '^0$';
        dt.api().column(2).search(pattern, true, false).draw()
    } else {
        let pattern = '^0|1$';
        dt.api().column(2).search(pattern, true, false).draw()
    }
}

function visibleCheckboxes(x) {
    dt.api().column(0).visible(x);
}

function visibleWordData(x) {
    dt.api().column(5).visible(x);
    dt.api().column(6).visible(x);
}

function switchColorCoding(x){
    if (x === true) {
        $('.genre-cc-disabled').removeClass('genre-cc-disabled').addClass('genre-cc-enabled')
        $('.pos-cc-disabled').removeClass('pos-cc-disabled').addClass('pos-cc-enabled')
    } else if (x === false) {
        $('.genre-cc-enabled').removeClass('genre-cc-enabled').addClass('genre-cc-disabled')
        $('.pos-cc-enabled').removeClass('pos-cc-enabled').addClass('pos-cc-disabled')
    }
    colorCodingEnabled = x;
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
        'Не удалось получить список слов :(' +
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

let tableFiltersInit = {
    beforeLoad:{},
    afterLoad:{},
    selectAfterFilter:{},
};
let tableFilters = tableFiltersInit.valueOf();
let tableFiltersLoaded = false;
let savingFiltersEnabled = true;

let loadFilterButton = {
    init: function () {
        this.$button = $('#getAndApplyFilters');
        this.$button.on('click', this.loadAndFilter);
        this.readyText = 'Повторить последнюю выборку';
        this.loadingText = `<i class="fa fa-sync fa-spin"></i> ${this.readyText}`;
        this.savingText = `<i class="fa fa-sync fa-spin"></i> ${this.readyText}`;
        this.savedText = this.readyText;
        this.errorText = `<i class="fa fa-exclamation-triangle text-danger"></i> ${this.readyText}`;
        this.setStateLoading();
        this.getFilters(function () {
            if (!tableFiltersLoaded) {
                loadFilterButton.setStateNoFilters();
            } else {
                loadFilterButton.setStateReady();
            }
        });
    },
    getFilters: function(after_complete, args=[]){
        if (FILTER_SAVING_ON === false){
            tableFilters = tableFiltersInit.valueOf();
                    tableFiltersLoaded = false;
            return;
        }
        $.ajax(Urls['dictionary:get_filters'](), {
            method: 'POST',
            dataType: 'json',
            async: false,
            statusCode: {
                200: function (r) {
                    tableFilters = r;
                    tableFiltersLoaded = true;
                },
                404: function () {
                    tableFilters = tableFiltersInit.valueOf();
                    tableFiltersLoaded = false;
                },
                500: function () {
                    tableFilters = tableFiltersInit.valueOf();
                    tableFiltersLoaded = false;
                }
            },
            complete: function () {
                after_complete(...args)
            }
        })
    },
    saveFilters: function(){
        if (FILTER_SAVING_ON === false){
            loadFilterButton.afterSavingError();
            return;
        }
        $.ajax(Urls['dictionary:save_filters'](), {
            method: 'POST',
            data: JSON.stringify({
                filters: tableFilters
            }),
            contentType: "application/json",
            dataType: "json",
            beforeSend: function () {
                loadFilterButton.setStateSaving();
            },
            statusCode:{
                200: function () {
                    loadFilterButton.afterSavingFilters()
                },
                500: function () {
                    loadFilterButton.afterSavingError();
                },
            },
        })
    },
    filter: function () {
        savingFiltersEnabled = false;
        applyFilters('beforeLoad', tableFilters);
        updateTable(function () {
            applyFilters('afterLoad', tableFilters);
            applyFilters('selectAfterFilter', tableFilters);
            savingFiltersEnabled = true;
        }, -1); // FIXME: find a way to select checkboxes on hidden pages
        loadFilterButton.setStateNoFilters()
        switchColorCoding(colorCodingEnabled)
    },
    loadAndFilter: function () {
        loadFilterButton.setStateLoading();
        loadFilterButton.getFilters(loadFilterButton.filter);
    },
    disable: function () {
        this.$button.attr('disabled', '').addClass('disabled')
    },
    setText: function (text) {
        this.$button.empty().html(text)
    },
    setStateReady: function () {
        this.setText(this.readyText)
    },
    setStateSaving: function () {
        this.setText(this.savingText)
    },
    setStateSaved: function () {
        this.setText(this.savedText);
        this.disable();
    },
    setStateLoading: function () {
        this.setText(this.loadingText)
    },
    setStateNoFilters: function () {
        this.setText(this.readyText);
        this.disable()
    },
    afterSavingFilters() {
        this.setStateSaved();
    },
    afterSavingError() {
        this.setStateError(function () {
            loadFilterButton.saveFilters()
        });
    },
    setStateError(callback) {
        this.setText(this.errorText);
        setTimeout(callback, 2000)
    }
};


function toggle(elm, checked){
    if (checked !== elm.prop('checked')) {
        elm.click();
  }
}

function select(elm, value){
    if (value !== elm.val()){
        elm.val(value);
        elm.change()
    }
}

function saveFilters(process, filterIds, filterAttrs, value=undefined, checked=undefined){
    if (!savingFiltersEnabled || isVerbs()){
        return
    }
    $.each(filterIds, function (i, filterId) {
        tableFilters[process][filterId] = {};
        tableFilters[process][filterId]['attrs'] = {};
        let elem = $('#' + filterId);
        $.each(filterAttrs, function (i, attributeName) {
            let attributeValue = elem.attr(attributeName);
            if (!attributeValue) {
                attributeValue = null
            }
            tableFilters[process][filterId]['attrs'][attributeName] = attributeValue
        });
        if (elem.val()) {
            tableFilters[process][filterId]['value'] = elem.val()
        }else if(typeof value !== 'undefined') {
            tableFilters[process][filterId]['value'] = value
        } else {
            tableFilters[process][filterId]['value'] = undefined
        }
        if (typeof elem.prop('checked') !== 'undefined') {
            tableFilters[process][filterId]['checked'] = elem.prop('checked')
        }else if(typeof checked !== 'undefined') {
            tableFilters[process][filterId]['checked'] = checked
        } else {
            tableFilters[process][filterId]['checked'] = undefined
        }
    });
    loadFilterButton.saveFilters()
}


function applyFilters(process, filters){
    $.each(filters[process], function (id, filter) {
        let elm = $('#' + id);
        $.each(filter.attrs, function (attributeName, attributeValue) {
            elm.attr(attributeName, attributeValue)
        });
        if (typeof filter.value !== "undefined"){
            select(elm, filter.value)
        }
        if (typeof filter.checked !== 'undefined'){
            toggle(elm, filter.checked);
        }
    });
}

function updateTable(afterInit=undefined, initialPageLength=50) {
    let form = $('#filterWordsForm');
    let url;
    url = isVerbs() ? Urls['dictionary:my_verbs']() : Urls['dictionary:my_words']();

    $.ajax(url, {
        type: 'POST',
        dataType: 'json',
        data: form.serialize(),
        success: function (r) {
            $table.html(r.table);
            if (dt !== undefined) {
                dt.api().destroy();
                if (!isVerbs()) {
                    $selectStars.remove();
                }
            }
            $table.DataTable({
                'dom':
                    "<'row'" +
                        "<'col-sm-12 mb-2'tr>" +
                    ">" +
                    "<'row mb-2'" +
                        "<'#alert.col-12'>" +
                        "<'#info.col-12 mb-2'i>" +
                        "<'col-sm-12 col-md-5'l>" +
                        "<'col-sm-12 col-md-7'p>" +
                    ">",
                'columnDefs': [
                    {
                        'targets': 0,
                        'render': function (data, type, row, meta) {
                            if (type === 'display') {
                                data = `<div class="checkbox"><input type="checkbox" id="checkbox-select-${data}" class="dt-checkboxes"><label></label></div>`;
                            }

                            return data;
                        },
                        'checkboxes': {
                            'selectRow': true,
                            'selectAllRender': '<div class="checkbox"><input type="checkbox" id="checkbox-select-all" class="dt-checkboxes"><label></label></div>'
                        },
                        'orderable': false
                    }
                ],
                'select': 'multi+shift',
                'searching': true,
                'ordering':  isVerbs(),
                'paging': true,
                "pageLength": initialPageLength,
                "lengthMenu": [ [50, 100, 250, 500, -1], [50, 100, 250, 500, "Все"] ],
                "language": {
                    "processing": "Подождите...",
                    "search": "Поиск:",
                    "lengthMenu": "Показывать: _MENU_",
                    "info": `${isVerbs() ? 'Глаголы' : 'Слова'} с _START_ до _END_ из _TOTAL_`,
                    "infoEmpty": `${isVerbs() ? 'Глаголы' : 'Слова'} с 0 до 0 из 0`,
                    "infoFiltered": "(отфильтровано из _MAX_ записей)",
                    "infoPostFix": "",
                    "loadingRecords": `Загрузка ${isVerbs() ? 'глаголов' : 'слов'}...`,
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
                            "_": `Выбрано ${isVerbs() ? 'глаголов' : 'слов'}: %d`,
                            "0": `Кликните по ${isVerbs() ? 'глаголу' : 'слову'} для выбора`,
                            "1": isVerbs() ? "Выбран один глагол" : "Выбрано одно слово"
                        }
                    }
                },
                initComplete: function () {
                    dt = this;
                    let $dt = $(dt)
                    let tableCompleteEvent = new Event('tableComplete')
                    document.dispatchEvent(tableCompleteEvent)
                    if (!isVerbs()) {
                        saveFilters('beforeLoad', ['id_packets'], []);
                        // adding star filter
                        this.api().columns(-1).every(function () {
                            let column = this;
                            $(column.header()).empty();
                            $(starFilterHtml).appendTo($(column.header())).selectpicker({
                                'noneSelectedText': "Оценка",
                                'header': 'Оценка',
                                'selectedTextFormat': 'count > 1'
                            }).on('change', function () {
                                saveFilters('afterLoad', [this.id], []);
                                let pattern = $(this).find(':selected').map(function () {
                                    return $(this).text()
                                }).get().join('|');
                                if (pattern === '') {
                                    dt.api().column(-1).search(pattern, false, true).draw();
                                } else {
                                    pattern = `^${pattern}$`;
                                    dt.api().column(-1).search(pattern, true, false).draw();
                                }
                                add_selected_filtered_alert(dt)
                            });
                            $selectStars = $('#starFilter');
                        });
                        showDeleted($('#showDeleted')[0].checked);
                        $('#showDeleted').on('change', function (e) {
                            e.preventDefault();
                            saveFilters('afterLoad', [this.id], ['checked']);
                            showDeleted(this.checked);
                            add_selected_filtered_alert(dt)
                        });

                        let $enableColorCodingInput = $('#enableColorCoding')
                        switchColorCoding($enableColorCodingInput[0].checked)
                        $enableColorCodingInput.on('change', function (e) {
                            e.preventDefault();
                            switchColorCoding(this.checked)
                        })
                        switchColorCoding(colorCodingEnabled)
                    }else{
                        let $hideRegularCheckbox = $('#hideRegular')
                        hideRegular($hideRegularCheckbox[0].checked)
                        $hideRegularCheckbox.on('change', function (e) {
                            e.preventDefault();
                            hideRegular(this.checked)
                        });
                        let $hideNegativeCheckbox = $('#hideNegative');
                        hideNegative($hideNegativeCheckbox[0].checked);
                        $hideNegativeCheckbox.on('change', function (e){
                            e.preventDefault();
                            hideNegative(this.checked)
                        })
                    }


                    bind_play_icons();
                    $dt.on('page.dt', (e, settings) => {
                        setTimeout(bind_play_icons, 1000)
                    });

                    $dt.on('user-select.dt.dtCheckboxes', function (e, api, type, indexes, originalEvent) {
                        if ($(originalEvent.target).hasClass('play')){
                            e.preventDefault()
                        }
                    });
                    $dt.on("select.dt.dtCheckboxes deselect.dt.dtCheckboxes", function(e, api, type, indexes, originalEvent) {
                        if (savingFiltersEnabled) {
                            tableFilters.selectAfterFilter = {};
                            let filterIds = [];
                            $.each(get_selected_filtered(dt), function (i, value) {
                                filterIds.push(`checkbox-select-${value}`)
                            });
                            saveFilters('selectAfterFilter', filterIds, ['checked'], 'on', true)
                        }
                    });
                    if (afterInit !== undefined) {
                        afterInit()
                    }

                }
            })
        },
        error: errorLoading,
        beforeSend: tableReloading,
    });

    $('.undertable').show();
    $('.uppertable').show();
}

function add_selected_filtered_alert(dt){
    if (get_selected(dt).sort().join(',') !== get_filtered(dt).sort().join(',')){
        $('#alert').html(
            '<div class="alert alert-info d-flex flex-row" role="alert">' +
                '<i class="fas fa-fw fa-info-circle mr-3 mt-1 mb-1"></i>' +
                '<div>' +
                    'К выбранным, но скрытым фильтрами элементам действия не применяются.' +
                '</div>' +
            '</div>'
        ).show()
    }else{
        $('#alert').hide()
    }
}

function get_selected(dt) {
    let rows_selected = dt.api().column(0).checkboxes.selected();
    let selected_ids = [];
    $.each(rows_selected, function (index, rowId) {
        selected_ids.push(rowId)
    });
    return selected_ids
}

function get_selected_filtered(dt){
    let selected_ids = get_selected(dt);
    let filtered_ids = get_filtered(dt);
    let selected_filtered_ids = [];
    selected_ids.forEach(function (value) {
        if(filtered_ids.includes(value)){
            selected_filtered_ids.push(value)
        }
    });
    return selected_filtered_ids
}

function get_filtered(dt){
    return  dt.api().rows({search:"applied"}).data().pluck(0).toArray();
}

$(document).ready(function () {
    let getParams = new URLSearchParams(window.location.search)
    $('#filterWordsForm').submit(function (ev) {
        ev.preventDefault();
        updateTable();
    });
    $('#startApp').on('click', function () {
        let ids=get_selected_filtered(dt);
        if(ids.length === 0){
            $('#startApp').popover({
                'content': `Вы не выбрали ни одного ${isVerbs() ? 'глагола' : 'слова'}`,
                'placement': 'auto',
                'trigger': 'manual',
                'container': 'body',
                'boundary': 'viewport'
            }).popover('show');
            setTimeout(function () {
                $('#startApp').popover('hide').popover('dispose')
            }, 2000)
        }else if (!isVerbs()){
            $('#startApp').popover('dispose');
            $.ajax(Urls['dictionary:app'](), {
            type: 'POST',
            contentType: "application/json",
            dataType: "json",
            data: JSON.stringify({
                words: ids,
                csrfmiddlewaretoken: csrf,
            }),
            error: errorLoading,
            success: function (r) {
                window.location.href = Urls['dictionary:app']()
            },
            beforeSend: emptyTable('')

        })} else {
            let url = Urls['dictionary:app_verbs']()
            let getParams = new URLSearchParams()
            ids.forEach(function (id, i) {
                getParams.append('v', id.toString())
            })
            url += '?' + getParams.toString()
            window.location.href = url
        }
    });
    $('#markWords').on('click', function () {
        let ids=get_selected_filtered(dt);
        if (ids.length === 0) {
            $('#markWords').popover({
                'content': "Вы не выбрали ни одного слова",
                'placement': 'auto',
                'trigger': 'manual',
                'container': 'body',
                'boundary': 'viewport'
            }).popover('show');
            setTimeout(function () {
                $('#markWords').popover('hide').popover('dispose')
            }, 2000)
        } else {
            $('#markWords').popover('dispose');
            $.ajax(Urls['dictionary:mark_words'](), {
                type: 'POST',
                contentType: "application/json",
                dataType: "json",
                data: JSON.stringify({
                    words: get_selected_filtered(dt),
                    csrfmiddlewaretoken: csrf,
                }),
                success: function (r) {
                    updateTable()
                },
                error: errorLoading,
                beforeSend: tableReloading,
            })
        }
    });
    $('#unmarkWords').on('click', function () {
        let ids=get_selected_filtered(dt);
        if (ids.length === 0) {
            $('#unmarkWords').popover({
                'content': "Вы не выбрали ни одного слова",
                'placement': 'auto',
                'trigger': 'manual',
                'container': 'body',
                'boundary': 'viewport'
            }).popover('show');
            setTimeout(function () {
                $('#unmarkWords').popover('hide').popover('dispose')
            }, 2000)
        } else {
            $('#unmarkWords').popover('dispose');
            $.ajax(Urls['dictionary:unmark_words'](), {
                type: 'POST',
                contentType: "application/json",
                dataType: "json",
                data: JSON.stringify({
                    words: get_selected_filtered(dt),
                    csrfmiddlewaretoken: csrf,
                }),
                success: function (r) {
                    updateTable()
                },
                error: errorLoading,
                beforeSend: tableReloading,
            })
        }
    });
    // Handle form submission event
    $('#main-frm').on('submit', function (e) {
        let form = this;
        let rows_selected = dt.api().column(0).checkboxes.selected();

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
    if (init_packets){
        $('#id_packets').selectpicker('val', init_packets)
        updateTable();
    }
    loadFilterButton.init();
    if(getParams.has('last') && getParams.get('last') === 'true'){
        loadFilterButton.loadAndFilter()
    }
});
