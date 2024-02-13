
document.querySelector(".container").addEventListener("submit", (e) =>{
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
    fetch('.', {
        method: 'POST',
        body: formData
    })
        .then(response => response.text())
        .then(data => {
            const container = document.querySelector(".container");
            container.innerHTML = data;
        });

});

