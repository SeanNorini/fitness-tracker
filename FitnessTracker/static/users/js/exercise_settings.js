function loadExerciseSettings(){
    fetch(`http://${domain}/workout/exercise_settings/`, {method:"GET", headers: {
        "X-Requested-With": "XMLHttpRequest",
        }})
            .then(response => response.text())
            .then(contentHTML => {
                const settingsContent = document.querySelector(".settings");
                settingsContent.innerHTML = contentHTML;
                loadExerciseSettingsEventListeners();
            });

}

function fetchExercise(){
    const selectMenu = document.getElementById("select_exercise");
    const exerciseName = selectMenu.value;
    fetch(`http://${domain}/workout/exercise_settings/edit_exercise/${exerciseName}`, {method:"GET", headers: {
    "X-Requested-With": "XMLHttpRequest",
    }})
        .then(response => response.text())
        .then(contentHTML => {
            const exerciseContainer = document.querySelector(".exercises");
            exerciseContainer.innerHTML = contentHTML;

            const messageContainer = document.getElementById("message");
            messageContainer.style.display = "none";
        });
}

function addExerciseSelectMenuListener(){
    const selectMenu = document.getElementById("select_exercise");
    selectMenu.addEventListener("change", e =>{
        fetchExercise();
    });
}

function loadExerciseSettingsEventListeners(){
    addExerciseSelectMenuListener();
    addNewExerciseListener();
    addSaveExerciseListener();
}

function addNewExerciseListener(){
    document.getElementById('new_exercise').addEventListener('click', function() {
    // Prompt for a name
    const exerciseName = prompt('Please enter name of exercise:');

    // Check if a name was entered
    if (exerciseName) {
        // Create a new option element
        const newOption = document.createElement('option');

        // Set the text content of the option to the entered name
        newOption.textContent = exerciseName;

        // Add the option to the select menu
        const selectMenu = document.getElementById('select_exercise');
        selectMenu.appendChild(newOption);
        newOption.selected = true;
        fetchExercise();
    }
});
}

function saveExerciseSettings(){
    const formData = new FormData();
    const fiveRepMax = document.getElementById('five_rep_max');
    const defaultWeight = document.getElementById('default_weight');
    const defaultReps = document.getElementById('default_reps');
    const exerciseName = document.getElementById("select_exercise").value;
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    formData.append('csrfmiddlewaretoken', csrftoken);
    formData.append('five_rep_max', fiveRepMax.value);
    formData.append('default_weight', defaultWeight.value);
    formData.append('default_reps', defaultReps.value);
    formData.append('name', exerciseName);

    fetch(`http://${domain}/workout/exercise_settings/edit_exercise/${exerciseName}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success === true) {
            showPopupExerciseSaved("Exercise Saved.", 3000);
        }
    })
}

function addSaveExerciseListener(){
    const saveExerciseButton = document.getElementById("save_exercise");
    saveExerciseButton.addEventListener("click", e => {
        saveExerciseSettings();
    });
}

function showPopupExerciseSaved(message, duration) {
    // Create a new popup element
    const popup = document.getElementById('popup');
    popup.textContent = message;
    popup.style.display = 'block';

    // Automatically close the popup after the specified duration
    setTimeout(function() {
        popup.style.display = 'none';
    }, duration);
}