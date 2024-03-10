function loadWorkoutsSettings() {
    fetch(`http://${domain}/workout/workout_settings`, {method:"GET", headers: {
        "X-Requested-With": "XMLHttpRequest",
    }})
        .then(response => response.text())
        .then(contentHTML => {
            const settingsContent = document.querySelector(".settings");
            settingsContent.innerHTML = contentHTML;
            loadWorkoutsSettingsListeners();

            let unitOfMeasurement = document.getElementById("unit_of_measurement").value;
            if (unitOfMeasurement === "Imperial"){
                unitOfMeasurement = "lbs";
            } else {
                unitOfMeasurement = "kg";
            }
    });
}

function addFiveRepMaxEventListener(inputFiveRepMax){
    inputFiveRepMax.addEventListener('blur', e => {
        if (inputFiveRepMax.value && !isNaN(parseFloat(inputFiveRepMax.value))) {
            const roundedValue = Math.round(parseFloat(inputFiveRepMax.value) * 4) / 4;
            inputFiveRepMax.value = roundedValue.toFixed(2);
        }
    });

    inputFiveRepMax.addEventListener('keyup', e => {
        const exerciseSets = inputFiveRepMax.closest(".exercise_container").querySelectorAll(".set");
        exerciseSets.forEach(exerciseSet => {
            const amountInput = exerciseSet.querySelector(".amount");
            const event = new KeyboardEvent('keyup', { key: 'Enter' });
            amountInput.dispatchEvent(event);
        });
    });
}

let previousSelectValue;
function loadWorkoutsSettingsListeners() {
    const saveWorkoutButton = document.getElementById("save_workout");
    saveWorkoutButton.addEventListener("click", e => {
        saveWorkout();
    });

    const selectWorkout = document.getElementById("select_workout");
    previousSelectValue = selectWorkout.value;
    selectWorkout.addEventListener("change", e => {
        const currentWorkout = selectWorkout.value;
        let confirm = fetchSelectedWorkout(selectWorkout);
        if (!confirm) {
            selectWorkout.value = previousSelectValue;
        }
        else{
            previousSelectValue = currentWorkout;
        }
    });

    const addExercise = document.querySelector(".add_exercise");
    addExercise.addEventListener("click", (e) => {
        unsavedChanges = true;
        e.preventDefault();
        const exerciseName = document.querySelector(".exercise").value;
        const exercises = document.querySelector(".exercises");

        fetch(`http://${domain}/workout/workout_settings/select_exercise/${exerciseName}`, {method: "GET"})
        .then(response => response.text())
        .then(template => {
            const exerciseTemplate = document.createElement("template");
            exerciseTemplate.innerHTML = template.trim();
            const exerciseElement = exerciseTemplate.content.firstChild;
            exercises.appendChild(exerciseElement);

            const deleteExerciseButton = exerciseElement.querySelector(".delete_exercise");
            deleteExerciseButton.addEventListener("click", (e) =>{
                deleteExercise(e);
                unsavedChanges = true;
            });

            const addSetButton = exerciseElement.querySelector(".add_set");
            addSetButton.addEventListener("click", (e) =>{
                const url = `http://${domain}/workout/workout_settings/add_set/${exerciseName}`
                const addListeners = true;
                addSet(e, url, addListeners);
                unsavedChanges = true;
            });

            const deleteSetButton = exerciseElement.querySelector(".delete_set");
            deleteSetButton.addEventListener("click", (e) => {
                deleteSet(e);
                unsavedChanges = true;
            });

            const exerciseSet = exerciseElement.querySelector(".set");
            addInputListeners(exerciseSet);

            const fiveRepMaxInput = exerciseElement.querySelector('input.max_rep');
            addFiveRepMaxEventListener(fiveRepMaxInput);


        });


        const messageContainer = document.querySelector("#message");
        messageContainer.style.display = "none";
    });

    const saveWorkoutSettingsButton = document.getElementById("save_workout_settings");
    saveWorkoutSettingsButton.addEventListener("click", e =>{
        saveWorkoutSettings();
    });
}

function saveWorkoutSettings(){
    const formData = new FormData();
    const autoUpdateFiveRepMax = document.getElementById('id_auto_update_five_rep_max');
    const showRestTimer = document.getElementById('id_show_rest_timer');
    const showWorkoutTimer = document.getElementById('id_show_workout_timer');
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    formData.append('csrfmiddlewaretoken', csrftoken);
    formData.append('auto_update_five_rep_max', autoUpdateFiveRepMax.checked);
    formData.append('show_rest_timer', showRestTimer.checked);
    formData.append('show_workout_timer', showWorkoutTimer.checked);

    fetch(`http://${domain}/workout/workout_settings/save_workout_settings/`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success === true) {
            const successMessage = document.querySelector('.success_message');
            successMessage.classList.remove('hidden');
            setTimeout(() => {
                successMessage.classList.add('hidden');
            }, 3000);
        }
    })
}

function addInputListeners (exerciseSet){
    const roundedFloatInput = exerciseSet.querySelector('input.round_float');
    roundedFloatInput.addEventListener('blur', e => {
        if (roundedFloatInput.value && !isNaN(parseFloat(roundedFloatInput.value))) {
            const roundedValue = Math.round(parseFloat(roundedFloatInput.value) * 4) / 4;
            roundedFloatInput.value = roundedValue.toFixed(2);
        }
    });

    roundedFloatInput.addEventListener('keyup', e => {
        updateWeight(e);
    });

    const roundedIntegerInput = exerciseSet.querySelector('input.round_integer');
    roundedIntegerInput.addEventListener('keyup', e => {
        if (roundedIntegerInput.value && !isNaN(parseFloat(roundedIntegerInput.value))) {
            const roundedValue = Math.round(parseFloat(roundedIntegerInput.value) * 4) / 4;
            roundedIntegerInput.value = roundedValue.toFixed(0);
        }
        const weightInput = e.target.closest('.set').querySelector('input.round_float');
        const event = new KeyboardEvent('keyup', { key: 'Enter' });
        weightInput.dispatchEvent(event);
        unsavedChanges = true;
    });


    const modifierInput = exerciseSet.querySelector(".modifier");
    modifierInput.addEventListener("change", e => {
        const weightInput = e.target.closest('.set').querySelector('input.round_float');
        const event = new KeyboardEvent('keyup', { key: 'Enter' });
        weightInput.dispatchEvent(event);
        unsavedChanges = true;
    });

    const event = new KeyboardEvent('keyup', { key: 'Enter' });
    roundedFloatInput.dispatchEvent(event);

}

function updateWeight(e){
    const amount = parseFloat(e.target.value);
    const setContainer = e.target.closest('.set');
    const modifier = setContainer.querySelector('.modifier').value;
    const fiveRepMax = parseFloat(e.target.closest('.exercise_container').querySelector('input.max_rep').value);
    const calculateWeightContainer = setContainer.querySelector('.calculate_weight');
    const reps = e.target.closest('.set').querySelector('input.reps').value;

    switch (modifier){
        case "exact":
            calculateWeightContainer.textContent = `${amount} ${unitOfMeasurement} x ${reps}`;
            break;
        case "percentage":
            calculateWeightContainer.textContent = `${(fiveRepMax * (amount/100)).toFixed(2)} ${unitOfMeasurement} x ${reps}`;
            break;
        case "increment":
            calculateWeightContainer.textContent = `${fiveRepMax + amount} ${unitOfMeasurement} x ${reps}`;
            break;
        case "decrement":
            calculateWeightContainer.textContent = `${fiveRepMax - amount} ${unitOfMeasurement} x ${reps}`;
            break;
    }

}

function fetchSelectedWorkout(selectWorkout){
    if (unsavedChanges === true) {
    let confirm = window.confirm("This will discard any unsaved changes. Are you sure?");
        if (!confirm) {
            return false;
        }
    }
    unsavedChanges = false;

    const workout_name = selectWorkout.value;
    fetch(`http://${domain}/workout/workout_settings/select_workout/${workout_name}`, {method: "GET"})
        .then(response => response.text())
        .then(contentHTML => {
            const exerciseContainer = document.querySelector(".exercises");
            exerciseContainer.innerHTML = contentHTML;
            settingsSelectWorkoutEventListeners();

            const messageContainer = document.querySelector("#message");

            if (workout_name === "Custom Workout") {
                messageContainer.style.display = "flex";
            }
            else {
                messageContainer.style.display = "none";
            }
        });
    return true;
}


function saveWorkout(){
    let newWorkout = false;
    const workoutData = new FormData();
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    workoutData.append('csrfmiddlewaretoken', csrftoken);

    const workoutSelect = document.getElementById("select_workout");
    let workoutName = workoutSelect.value.trim();
    if (workoutName !== "Custom Workout"){
        const confirm = window.confirm(`This will save new settings to workout "${workoutName}." Are you sure?`);
        if (!confirm) {
            workoutName = window.prompt(`Please enter a name for the new workout or close this window to cancel.`);
            newWorkout = true;
        }
    }
    else {
        workoutName = window.prompt(`Please enter a name for the new workout or close this window to cancel.`);
        newWorkout = true;
    }

    if (workoutName === null || workoutName.trim() === ""){
        return;
    }

    workoutData.append("workout_name", workoutName);

    const workoutExercises = document.querySelectorAll('.exercise_container');
    workoutExercises.forEach(exercise => {
        const exerciseName = exercise.querySelector('#exercise_name').textContent.trim();
        const fiveRepMax = parseFloat(exercise.querySelector("input.max_rep").value);
        const currentExercise = {"name": exerciseName, "five_rep_max": fiveRepMax, "sets": []};

        const exerciseSets = exercise.querySelectorAll(".set");
        exerciseSets.forEach(exerciseSet => {
            const currentSet = {};
            currentSet["amount"] = parseFloat(exerciseSet.querySelector(".amount").value);
            currentSet["modifier"] = exerciseSet.querySelector(".modifier").value;
            currentSet["reps"] = parseInt(exerciseSet.querySelector(".reps").value);

            currentExercise["sets"].push(currentSet)
        });

        workoutData.append("exercises", JSON.stringify(currentExercise));
    });

    // Send workouts data and display response
    fetch(`http://${domain}/workout/workout_settings/save_workout/`, {method: "POST", body: workoutData})
    .then(response => response.json())
    .then(data => {
        if (data.success){
            showPopupWorkoutSaved("Workout saved.", 2500);

            if (newWorkout){
                const selectOption = document.createElement("option");
                selectOption.value = workoutName;
                selectOption.innerText = workoutName;
                workoutSelect.appendChild(selectOption);
            }

        }
    });

}

function settingsSelectWorkoutEventListeners(){
    const exercises = document.querySelectorAll(".exercise_container");
    exercises.forEach(exercise => {
        const deleteExerciseButton = exercise.querySelector(".delete_exercise");
        deleteExerciseButton.addEventListener("click", (e) =>{
            deleteExercise(e);
            unsavedChanges = true;
        });

        const addSetButton = exercise.querySelector(".add_set");
        addSetButton.addEventListener("click", (e) =>{
            const container = e.target.closest(".exercise_container");
            const exerciseName = container.querySelector("#exercise_name").textContent.trim();
            const url = `http://${domain}/workout/workout_settings/add_set/${exerciseName}`
            const addListeners = true;
            addSet(e, url, addListeners);
            unsavedChanges = true;
        });

        const deleteSetButton = exercise.querySelector(".delete_set");
        deleteSetButton.addEventListener("click", (e) =>{
            deleteSet(e);
            unsavedChanges = true;
        });

        const exerciseSets = exercise.querySelectorAll(".set");
        exerciseSets.forEach(exerciseSet => addInputListeners(exerciseSet));

        const fiveRepMaxInput = exercise.querySelector('input.max_rep');
        addFiveRepMaxEventListener(fiveRepMaxInput);

    });

}