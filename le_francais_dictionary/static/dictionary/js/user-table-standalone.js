$(document).ready(function () {
    $(document).on('tableComplete', function () {
        showDeleted(true);
        visibleCheckboxes(false);
        if (!USER_IS_AUTHENTICATED === false){
            visibleWordData(false)
        }
    })
})

