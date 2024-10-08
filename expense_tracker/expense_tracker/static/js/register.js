const usernameField = document.getElementById("usernameField");
const feedbackArea = document.querySelector(".invalid-feedback");
const emailField = document.getElementById("emailField");
const emailFeedbackArea = document.querySelector(".emailFeedbackArea");
const passwordField = document.querySelector("#passwordField");
const usernameSuccessOutput = document.querySelector(".usernamesuccessOutput");
const emailsuccessOutput = document.querySelector(".emailsuccessOutput");
const showPasswordToggle = document.querySelector(".showPasswordToggle");
const submitBtn = document.querySelector(".submit-btn");

submitBtn.disabled = true; // 1. Button starts as disabled
let errorUsername = true; // 2. Assume both fields are invalid initially
let errorEmail = true;

const handleToggleInput = (e) => {
    if (showPasswordToggle.textContent === "SHOW") {
        showPasswordToggle.textContent = "HIDE";
        passwordField.setAttribute("type", "text");
    } else {
        showPasswordToggle.textContent = "SHOW";
        passwordField.setAttribute("type", "password");
    }
};

showPasswordToggle.addEventListener('click', handleToggleInput);

// Helper function to check if the button should be enabled
const checkFormValidity = () => {
    if (!errorUsername && !errorEmail) {
        submitBtn.removeAttribute("disabled");
    } else {
        submitBtn.disabled = true;
    }
};

// 3. Listen to the email field
emailField.addEventListener("keyup", (e) => {
    const emailVal = e.target.value;

    // Reset feedback and errors if user clears the input
    emailField.classList.remove("is-invalid");
    emailFeedbackArea.style.display = "none";
    emailsuccessOutput.style.display = "block";
    emailsuccessOutput.textContent = `Checking ${emailVal}`;

    if (emailVal.length >= 0) {  // 5. >= to handle empty case
        fetch("/authentication/validate-email/", {
            body: JSON.stringify({ email: emailVal }),
            method: "POST",
        }).then((res) => res.json()).then((data) => {
            emailsuccessOutput.style.display = "none";

            if (data.email_error) {
                errorEmail = true; // Error in email
                emailField.classList.add("is-invalid");
                emailFeedbackArea.style.display = "block";
                emailFeedbackArea.innerHTML = `<p>${data.email_error}</p>`;
            } else {
                errorEmail = false; // No error in email
            }

            checkFormValidity(); // Check if form can be submitted
        });
    }
});

// 3. Listen to the username field
usernameField.addEventListener("keyup", (e) => {
    const usernameVal = e.target.value;

    // Reset feedback and errors if user clears the input
    usernameField.classList.remove("is-invalid");
    feedbackArea.style.display = "none";
    usernameSuccessOutput.style.display = "block";
    usernameSuccessOutput.textContent = `Checking ${usernameVal} `;

    if (usernameVal.length >= 0) { // 5. >= to handle empty case
        submitBtn.disabled = true; // 5. Disable the button before checking

        fetch("/authentication/validate-username/", {
            body: JSON.stringify({ username: usernameVal }),
            method: "POST",
        }).then((res) => res.json()).then((data) => {
            usernameSuccessOutput.style.display = "none";

            if (data.username_error) {
                errorUsername = true; // Error in username
                usernameField.classList.add("is-invalid");
                feedbackArea.style.display = "block";
                feedbackArea.innerHTML = `<p>${data.username_error}</p>`;
            } else {
                errorUsername = false; // No error in username
            }

            checkFormValidity(); // Check if form can be submitted
        });
    }
});
