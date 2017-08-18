function getNavRootId() {
  return $('meta[name="nav-root-id"]').attr("data-value")
}

$(document).ready(function () {
  $.getJSON('/api/nav/?rootId=' + getNavRootId(), function (navData) {
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