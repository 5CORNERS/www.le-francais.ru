$(document).ready(function () {
    $(document).on('tableComplete', function () {
        $('#showDeleted').prop('checked', true);
        // $('#showDeleted')[0].checked = true;
        if (CROSS_SITE_KEY==null){
            showDeleted(true);
            visibleCheckboxes(false);
        }
        if (USER_IS_AUTHENTICATED === false){
            visibleWordData(false)
        }
    })
})

