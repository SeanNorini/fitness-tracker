document.getElementById("registration_form").addEventListener("submit", (e) =>{
    e.preventDefault();

    // Pull data from form
    const formElements = document.querySelector("#registration_form").querySelectorAll("input");
    const formData = new FormData();
    formElements.forEach((element) => {
        formData.append(element.name, element.value);
    });

    gender = document.querySelector("#id_gender_0");
    if (gender.checked) {
      formData.set("gender", gender.value);
    }
    // Add CSRF token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    formData.append('csrfmiddlewaretoken', csrftoken)

    // Send form, redirect to index on success otherwise display error.
    const errorOutput = document.querySelector('#form_error')
    fetch('.', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) 
        {
            window.location.href = "";
        }
        else
        {
            errorOutput.classList.remove("hidden")
            errorOutput.innerHTML = "";
            data['error'].forEach(error => {
                errorOutput.innerHTML += "<li>" + error + "</li>";
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        errorOutput.innerText = "Sorry! There was an error submitting your registration. ";
    });   
});

