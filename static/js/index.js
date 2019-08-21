$(document).ready(function() {
  $(".team").click(function() {
    $(this).toggleClass("selected")
  });

  $(".submit-button").click(function() {
    selected = $(".selected");
    abbrs = _.map(selected, function(team) {
      return team.innerText
    });
    includePlayoffs = $("[name='include-playoffs'")[0].checked
    console.log(includePlayoffs)
    $.ajax("/calculate", {
      method: "POST",
      contentType: 'application/json',
      data: JSON.stringify({
        "abbrs": abbrs,
        "include_playoffs": includePlayoffs
      })
    }).then(
      // done
      function(response) {
        $(".data").html(response)
      }
      // TODO: failed
    );
  })
});