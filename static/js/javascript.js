// init() executes after DOMContent has been loaded
function init() {
    // find form and validation items in the page
    var form = document.querySelector(".needs-validation");
    var validation_items = document.querySelectorAll(".form-control");

    // check if required fields are empty upon submitting and stop it if that's the case
    form.addEventListener('submit', function(event) {
        for (const item of validation_items) {
            if (item.value === "") {
                event.preventDefault();
                event.stopPropagation();
            }
        }

        // give was-validated class to form if validation was completed
        form.className = "was-validated";
    }, false);
}
// make sure DOMContent is loaded before the code runs
document.addEventListener("DOMContentLoaded", init, false);