$('[data-cardSelectButton]').click(function() {
  $('.is-selected').each(function (i,e) {
    $(e).toggleClass('is-selected')
  });
  $(this).parent('[data-cardSelect]').toggleClass('is-selected');
});
