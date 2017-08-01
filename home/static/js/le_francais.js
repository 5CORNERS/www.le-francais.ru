$(document).ready(function () {

    $.getJSON('/api/nav/?rootId=11', function (navData) {
       $('#sidebar').treeview({
         enableLinks: true,
         data: navData
       });
    });
    $(".sidebar-collapse-button").click(function () {
        var $target = $($(this).data("target"));
        $target.toggleClass('in');
        $(this).attr('aria-expanded', $target.hasClass('in'));
    });

    $('audio').audioPlayer();
});