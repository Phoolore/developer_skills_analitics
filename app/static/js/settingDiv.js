window.addEventListener('load', function() {


  var settingsButton = document.getElementById("settings-button");
  var settingsDiv = document.getElementById("settings-div");
  
  settingsButton.addEventListener("click", function() {
    if (settingsDiv.style.display === "none") {
      settingsDiv.style.display = "block";
    } else {
      settingsDiv.style.display = "none";
    }
  });
  });