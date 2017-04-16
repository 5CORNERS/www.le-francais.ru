$(document).ready(function () {
    $(".sidebar-collapse-button").click(function () {
        var $target = $($(this).data("target"));
        $target.toggleClass('in');
        $(this).attr('aria-expanded', $target.hasClass('in'));
    });

    $('audio').audioPlayer();
});