// init() executes after DOMContent has been loaded
function init() {
    // find form and validation items in the page
    const forms = document.querySelectorAll("form");
    const dropdown_menu = document.querySelector("#drop_menu");
    const dropdown_link = document.querySelector("#drop_link");
    const navbar = document.querySelector("#nav_menu");

    // loop over each form
    forms.forEach(function(form) {
        // check if required fields are empty upon submitting and stop it if that's the case
        form.addEventListener('submit', function(event) {
            // find the items to validate in the form
            const validation_items = event.target.closest("form").querySelectorAll(".form-control");
            
            // for each to be validated item validate
            for (const item of validation_items) {
                if (item.value === "") {
                    event.preventDefault();
                    event.stopPropagation();
                }
            }

            // give was-validated class to form if validation was completed
            form.className = "was-validated";

            // keep the login dropdown showing after validation
            if (form.parentElement.id == "drop_menu") {
                dropdown_menu.classList.add("show");
                navbar.classList.add("show");
                dropdown_link.getAttribute("aria-expanded") = true;
            };
        }, false);
    });
}
// make sure DOMContent is loaded before the code runs
document.addEventListener("DOMContentLoaded", init, false);