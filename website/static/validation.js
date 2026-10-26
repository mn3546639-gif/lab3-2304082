const form = document.getElementById("register-form");
const errorBox = document.getElementById("errors");

form.addEventListener("submit", function (event) {
    const name = form.elements["name"].value.trim();
    const email = form.elements["email"].value.trim();
    const password = form.elements["password"].value;
    const confirmPassword = form.elements["confirm_password"].value;

    const errors = [];

    if (!name) {
        errors.push("Name is required");
    }

    if (!email) {
        errors.push("Email is required");
    }

    if (!password) {
        errors.push("Password is required");
    }

    if (!confirmPassword) {
        errors.push("Confirm password is required");
    }

    if (password && confirmPassword && password !== confirmPassword) {
        errors.push("Passwords do not match");
    }

    errorBox.textContent = "";

    if (errors.length > 0) {
        event.preventDefault();

        for (const error of errors) {
            const paragraph = document.createElement("p");
            paragraph.textContent = error;
            errorBox.appendChild(paragraph);
        }
    }
});