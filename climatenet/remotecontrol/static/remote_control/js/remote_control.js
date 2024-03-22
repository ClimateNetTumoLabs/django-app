function openForm(formName) {
    var i, formContainer, tablinks;
    formContainer = document.getElementsByClassName("form-container");
    for (i = 0; i < formContainer.length; i++) {
        formContainer[i].style.display = "none";
    }
    document.querySelectorAll('.container button').forEach(button => {
        button.style.backgroundColor = '#417690';
    });

    document.getElementById(formName + "Button").style.backgroundColor = '#1e3744';
    document.getElementById(formName + "Form").style.display = "block";
    document.getElementById(formName + "Result").style.display = "block";
}
async function submitForm(event, resultId) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
    const deviceId = document.getElementById('deviceId').value;
    const respondingTimeout = document.getElementById('respondingTimeout').value;
    const resultTimeout = document.getElementById('resultTimeout').value;
    formData.append('deviceId', deviceId);
    formData.append('csrfmiddlewaretoken', csrfToken);
    formData.append('respondingTimeout', respondingTimeout)
    formData.append('resultTimeout', resultTimeout)

    document.getElementById(resultId).innerText = "";

    const submitButton = form.querySelector("button[type=submit]");
    const originalColor = submitButton.style.backgroundColor;
    submitButton.style.backgroundColor = "#1e3744";
    submitButton.disabled = true;
    document.body.style.cursor = "wait";

    const response = await fetch(form.action, {
        method: 'POST',
        body: formData
    });

    submitButton.style.backgroundColor = originalColor;
    submitButton.disabled = false;
    document.body.style.cursor = "default";

    if (response.ok) {
        let result = await response.text();
        document.getElementById(resultId).innerHTML = result;
    } else if (response.status === 401) {
        window.location.reload();
    } else {
        console.error('Failed to submit form');
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("keydown", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                form.dispatchEvent(new Event("submit"));
            }
        });
    });
});