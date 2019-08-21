$(document).ready(function() {
  $(".team").click(function() {
    $(this).toggleClass("selected")
  });

  $(".submit-button").click(function() {
    selected = $(".selected");
    abbrs = _.map(selected, function(team) {
      return team.innerText
    });
    console.log(abbrs)
    $.ajax("/calculate", {
      method: "POST",
      contentType: 'application/json',
      data: JSON.stringify({
        "abbrs": abbrs
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