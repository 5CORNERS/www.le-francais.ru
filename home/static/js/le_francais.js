function getNavRootId() {
  return $('meta[name="nav-root-id"]').attr("data-value")
}

function getPageId() {
  return $('meta[name="page-id"]').attr("data-value")
}


function setNodeState(href, isExpanded) {
  var nodesCollapsedState = localStorage.getItem("nodesCollapsedState") != null ?
    JSON.parse(localStorage.getItem("nodesCollapsedState")) :
    {};
  nodesCollapsedState[href] = isExpanded;
  localStorage.setItem("nodesCollapsedState", JSON.stringify(nodesCollapsedState))
}

function addExpandedStateToNavdata(navData) {
  var state = localStorage.getItem("nodesCollapsedState") != null ?
    JSON.parse(localStorage.getItem("nodesCollapsedState")) :
    {};
  navData.forEach(function (node) {
    var href = navData.href;
    if (href in state) {
      var expanded = state[href];

      node.state.expanded = expanded
    }
    if (node.nodes) {
      addExpandedStateToNavdata(node.nodes);
      node.nodes.forEach(function (child) {
        if (child.state && (child.state.expanded || child.state.selected)) {
          node.state.expanded = true;
        }
      })
    }
    if (node.state && node.state.selected) {
      node.state.expanded = true;
    }
  });
  return navData
}

$(document).ready(function () {
  $.getJSON('/api/nav/?rootId=' + getNavRootId() + '&pageId=' + getPageId(), function (navData) {
    navData = addExpandedStateToNavdata(navData);
    $('#sidebar').treeview({
      levels: 0,
      data: navData,
      onNodeSelected: function (event, data) {
        window.location.href = data.href;
      },
      onNodeExpanded: function (event, data) {
        setNodeState(data.href, true)
      },
      onNodeCollapsed: function (event, data) {
        setNodeState(data.href, false)
      }
    });
  });
  $(".sidebar-collapse-button").click(function () {
    var $target = $($(this).data("target"));
    $target.toggleClass('in');
    $(this).attr('aria-expanded', $target.hasClass('in'));
  });

  $('audio').audioPlayer();

  // Javascript to enable link to tab
  var url = document.location.toString();
  if (url.match('#')) {
    $('.nav-tabs a[href="#' + url.split('#')[1] + '"]').tab('show');
  } else {
    $('.nav-tabs a:first').tab('show');
  }

// Change hash for page-reload
  $('.nav-tabs a').on('shown.bs.tab', function (e) {
    window.location.hash = e.target.hash;
  })
});