$(document).ready(function () {
    $(document).on('tableComplete', function () {
        $('#showDeleted').prop('checked', true);
        // $('#showDeleted')[0].checked = true;
        showDeleted(true);
        visibleCheckboxes(false);
        if (USER_IS_AUTHENTICATED === false){
            visibleWordData(false)
        }
    })
})

