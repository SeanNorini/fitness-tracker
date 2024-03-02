function loadSettings() {
    let scriptLoaded = null;
    document.querySelectorAll(".button_back").forEach(button => {
        button.addEventListener("click", function() {
            const group = this.getAttribute("data-group");
            const buttonsInGroup = document.querySelectorAll(
                `.button_back[data-group="${group}"]`
            );

            if (!this.classList.contains("active")) {
                buttonsInGroup.forEach(btn => {
                    if (btn !== this) {
                        btn.classList.remove("active");
                    }
                });

                this.classList.toggle("active");
            }
            switch(this.getAttribute("id")) {
                case "user":
                    loadUserSettings();
                    break;
                case "workouts":
                    scriptLoaded = addScript("/static/users/js/workout_settings.js");
                    if (scriptLoaded){
                        scriptLoaded.onload = function(){loadWorkoutsSettings();}
                    }
                    else{
                        loadWorkoutsSettings();
                    }
                    break;
                case "exercises":
                    scriptLoaded = addScript("/static/users/js/exercise_settings.js");
                    if (scriptLoaded){
                        scriptLoaded.onload = function(){loadExerciseSettings();}
                    }
                    else{
                        loadExerciseSettings();
                    }
                    break;
                case "routine":
                    break;
            }
        });
    });

    accountSettingsListeners();
    bodyCompositionSettingsListeners();
}

function changePasswordEventListeners(){
    returnToSettings();
    const changePassword = document.querySelector("#change_password");
    changePassword.addEventListener("click", e =>{
        e.preventDefault();

        const formData = new FormData();
        const formElements = document.querySelector("#change_password_form").querySelectorAll("input");
        formElements.forEach((element) => {
            formData.append(element.name, element.value);
        });

        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        formData.append('csrfmiddlewaretoken', csrftoken)

        fetch(`http://${domain}/user/change_password/`, {method:"POST", headers: {
        "X-Requested-With": "XMLHttpRequest",
        }, body: formData})
            .then(response => response.text())
            .then(contentHTML => {
                const settingsContent = document.querySelector(".settings");
                settingsContent.innerHTML = contentHTML;

                const error = document.querySelector(".errorlist");
                if (error){
                    changePasswordEventListeners();
                } else {
                    returnToSettings();
                }
            });

    });
}

function loadUserSettings() {
    fetch(`http://${domain}/user/settings`, {method:"GET", headers: {
        "X-Requested-With": "XMLHttpRequest",
        }})
            .then(response => response.text())
            .then(contentHTML => {
                const settingsContent = document.querySelector("#content");
                settingsContent.innerHTML = contentHTML;
                loadSettings();
            });
}

function returnToSettings(){
    const returnToSettingsLink = document.querySelector("#return_to_settings");
    returnToSettingsLink.addEventListener("click", e =>{
        e.preventDefault();
        loadUserSettings();
    });
}

function accountSettingsListeners() {
    const deleteAccount = document.querySelector("#delete_account");
    deleteAccount.addEventListener("click", e => {
        let confirm;
        do {
            confirm = window.prompt("WARNING! This will permanently delete your account and any " +
            "associated records. Type 'delete' to confirm.");
            if (confirm !== null){
                confirm = confirm.toLowerCase();
            }
            if (confirm === "delete"){
                window.location.href = `http://${domain}/user/delete_account`;
            }
        } while (confirm !== "delete" && confirm !== null);
    });

    const changePassword = document.querySelector("#change_password");
    changePassword.addEventListener("click", e=>{
        fetch(`http://${domain}/user/change_password`, {method:"GET", headers: {
        "X-Requested-With": "XMLHttpRequest",
        }})
            .then(response => response.text())
            .then(contentHTML => {
                const settingsContent = document.querySelector(".settings");
                settingsContent.innerHTML = contentHTML;
                changePasswordEventListeners();
            });
    });

    const updateAccountSettings = document.querySelector("#update_settings");
    updateAccountSettings.addEventListener("click", e=>{
        const formData = new FormData();
        const formElements = document.querySelector("#account_settings_form").querySelectorAll("input");
        formElements.forEach((element) => {
            formData.append(element.name, element.value);
        });

        fetch(`http://${domain}/user/settings/update_account_settings/`, {method:"POST", headers: {
        "X-Requested-With": "XMLHttpRequest",
        }, body: formData})
            .then(response => response.text())
            .then(contentHTML => {
                const accountSettingsContainer = document.querySelector(".account_settings");
                accountSettingsContainer.innerHTML = contentHTML;
                accountSettingsListeners();
            });
    });

}

function bodyCompositionSettingsListeners() {
    const measurementRadios = document.querySelectorAll('input[name="unit_of_measurement"]');
    measurementRadios.forEach(radio => {
    radio.addEventListener("change", e=> {
        const heightLabel = document.querySelector('label[for="height"]');
        const heightInput = document.querySelector('input[name="height"]');
        const weightLabel = document.querySelector('label[for="weight"]');
        const weightInput = document.querySelector('input[name="weight"]');

        if (e.target.value === "Imperial"){
            heightLabel.textContent = heightLabel.textContent.replace("(cm)", "(in.)");
            heightInput.placeholder = "70";
            weightLabel.textContent = weightLabel.textContent.replace("(kg)", "(lbs)");
            weightInput.placeholder = "160";
        } else {
            heightLabel.textContent = heightLabel.textContent.replace("(in.)", "(cm)");
            heightInput.placeholder = "175";
            weightLabel.textContent = weightLabel.textContent.replace("(lbs)", "(kg)");
            weightInput.placeholder = "70";
            }
        });
    });

    const updateBodyCompositionSettings = document.querySelector("#update_body_composition");
    updateBodyCompositionSettings.addEventListener("click", e=>{
        const formData = new FormData();
        const formElements = document.querySelector("#body_composition_form").querySelectorAll("input");
        formElements.forEach((element) => {
            formData.append(element.name, element.value);
        });

        const gender = document.querySelector("#gender_0");
        if (gender.checked) {
            formData.set("gender", "M");
        } else {
            formData.set("gender", "F");
        }

        const unitOfMeasurement = document.querySelector("#unit_of_measurement_0");
        if (unitOfMeasurement.checked) {
            formData.set("unit_of_measurement", "Imperial");
        } else {
            formData.set("unit_of_measurement", "Metric");
        }

        fetch(`http://${domain}/user/settings/update_body_composition_settings/`, {method:"POST", headers: {
        "X-Requested-With": "XMLHttpRequest",
        }, body: formData})
            .then(response => response.text())
            .then(contentHTML => {
                const bodyCompositionSettingsContainer = document.querySelector(".body_composition_settings");
                bodyCompositionSettingsContainer.innerHTML = contentHTML;
                bodyCompositionSettingsListeners();
            });
    });
}
