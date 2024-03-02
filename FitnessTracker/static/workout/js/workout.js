let unsavedChanges = false;
function deleteSet(e) {
    const container = e.target.closest(".exercise_container");
    const containerSets = container.querySelectorAll(".set");
    const lastSet = containerSets[containerSets.length - 1];
    lastSet.remove();
    unsavedChanges = true;
}

function deleteExercise (e)  {
    e.target.closest(".exercise_container").remove();
    if (!document.querySelector(".add_set")){
        setMessage("Please select a workout or add an exercise to get started.");
    }
    unsavedChanges = true;
}

function setMessage(message) {
    const messageContainer = document.querySelector("#message");
    messageContainer.innerText = message;
    messageContainer.style.display = "flex";
}

function updateSetNumber(container) {
    const sets = container.querySelectorAll(".set");
    sets[sets.length - 1].querySelector(".set_number").innerText = "Set " + sets.length + ":";
}

function showPopupWorkoutSaved(message, duration) {
    // Create a new popup element
    const popup = document.getElementById('popup');
    popup.textContent = message;
    popup.style.display = 'block';

    // Automatically close the popup after the specified duration
    setTimeout(function() {
        popup.style.display = 'none';
    }, duration);
}

function addSet(e, url, addListeners) {
    fetch(`${url}`, {method: "GET"})
        .then(response => response.text())
        .then(template => {
            const setTemplate = document.createElement("template");
            setTemplate.innerHTML = template.trim();
            const container = e.target.closest(".exercise_container");
            const setElement = setTemplate.content.firstChild
            container.querySelector(".sets").appendChild(setElement);
            updateSetNumber(container);

            if (addListeners && typeof addInputListeners === 'function'){
                addInputListeners(setElement);
            } else {
                const setCompleteCheckbox = setElement.querySelector(".set_complete");
                addCheckboxListener(setCompleteCheckbox);
            }
        });
    unsavedChanges = true;
}



function selectWorkoutEventListeners(){
    const exercises = document.querySelectorAll(".exercise_container");
    exercises.forEach(exercise => {
        const deleteExerciseButton = exercise.querySelector(".delete_exercise");
        deleteExerciseButton.addEventListener("click", (e) =>{
            e.preventDefault();
            deleteExercise(e);
        });

        const addSetButton = exercise.querySelector(".add_set");
        addSetButton.addEventListener("click", (e) =>{
            const url = 'add_set';
            const addListeners = false;
            addSet(e, url, addListeners);
        });

        const deleteSetButton = exercise.querySelector(".delete_set");
        deleteSetButton.addEventListener("click", (e) =>{
            deleteSet(e);
        });

        const setCompleteCheckbox = exercise.querySelector(".set_complete");
        addCheckboxListener(setCompleteCheckbox);

    });
}

let timerRunning = false; // Variable to track timer status

function restTimer() {
    const clockElement = document.getElementById('clock');
    let minutes = 0;
    let seconds = 0;

    function updateClock() {
        seconds++;

        if (seconds === 60) {
            seconds = 0;
            minutes++;
        }

        const formattedMinutes = minutes < 10 ? '0' + minutes : minutes;
        const formattedSeconds = seconds < 10 ? '0' + seconds : seconds;

        clockElement.textContent = formattedMinutes + ':' + formattedSeconds;

        if (timerRunning) {
            setTimeout(updateClock, 1000);
        }
    }

    updateClock();

    return {
        stop: function() {
            timerRunning = false; // Stop the timer
            minutes = 0; // Reset minutes
            seconds = 0; // Reset seconds
            clockElement.textContent = '00:00'; // Reset clock display
        },
        start: function() {
            timerRunning = true; // Start the timer
            updateClock(); // Start updating the clock
        }
    };
}

function showRestTimer() {
    const popup = document.querySelector('.clock_popup');
    popup.style.display = 'block';

    const closePopup = document.getElementById('close');
    closePopup.addEventListener("click", e => {
        popup.style.display = 'none';
        restTimerInstance.stop(); // Stop the timer when closing the popup
    });

    const restTimerInstance = restTimer();
    restTimerInstance.start(); // Start the timer when showing the popup
}

function addCheckboxListener(checkbox){
    checkbox.addEventListener("change", e => {
        if (checkbox.checked){
            showRestTimer();
            restTimer();
        }
    });
}

function loadWorkout(){
    const currentDate = new Date();
    document.getElementById("date").valueAsDate = new Date(
        currentDate.getTime() - currentDate.getTimezoneOffset() * 60000 );


    const workout = document.querySelector(".workout");
    workout.addEventListener("change", (e) => {
        const confirm = window.confirm("This will erase the current workout session, are you sure?")

        if (confirm){
            fetch(`http://${domain}/workout/select_workout/${workout.value}`, {method:"GET"})
            .then(response => response.text())
            .then(workoutHTML => {
                const exercises = document.querySelector(".exercises");
                exercises.innerHTML = workoutHTML;
                selectWorkoutEventListeners();
            });
        }
    });

    const addExercise = document.querySelector(".add_exercise");

    addExercise.addEventListener("click", (e) => {
        e.preventDefault();
        const exercise = document.querySelector(".exercise").value;
        const exercises = document.querySelector(".exercises");

        fetch(("add_exercise/") + exercise, {method: "GET"})
        .then(response => response.text())
        .then(template => {
            const exerciseTemplate = document.createElement("template");
            exerciseTemplate.innerHTML = template.trim();
            const exerciseElement = exerciseTemplate.content.firstChild;
            exercises.appendChild(exerciseElement);
            const deleteExerciseButton = exerciseElement.querySelector(".delete_exercise");
            deleteExerciseButton.addEventListener("click", (e) =>{
                e.preventDefault();
                deleteExercise(e);
            });

            const addSetButton = exerciseElement.querySelector(".add_set");
            addSetButton.addEventListener("click", (e) =>{
                const url = 'add_set';
                const addListeners = false;
                addSet(e, url, addListeners);
            });

            const deleteSetButton = exerciseElement.querySelector(".delete_set");
            deleteSetButton.addEventListener("click", (e) => {
                deleteSet(e);
            });

            const setCompleteCheckbox = exerciseElement.querySelector(".set_complete");
            addCheckboxListener(setCompleteCheckbox);

        });

        const messageContainer = document.querySelector("#message");
        messageContainer.style.display = "none";

        unsavedChanges = true;
    });
    const saveWorkout = document.querySelector(".save_workout");

    saveWorkout.addEventListener("click", (e) => {
        e.preventDefault();
        // Check for workout to save
        const exercises = document.querySelectorAll(".exercise_container");
        if (exercises.length === 0) {
            setMessage("You must add at least one exercise before saving a workout session.");
            return
        }

        // Create form to gather data
        const workout = new FormData();

        // Get workout name
        const workoutName = document.querySelector(".workout").value;
        workout.append("workout_name", workoutName);

        // Get exercise sets
        const workoutExercises = [];
        exercises.forEach(element => {
            const weights = [];
            const reps = [];
            const exerciseName = element.querySelector("#exercise_name").textContent.trim();

            const sets = element.querySelectorAll(".set");
            sets.forEach(element => {
                let setWeight = element.querySelector(".weight").value;
                if (setWeight === ""){
                    setWeight = 0;
                }
                weights.push(setWeight);

                let setReps = element.querySelector(".reps").value;
                if (setReps === ""){
                    setReps = 0;
                }
                reps.push(setReps);
            });
            let exercise = {};
            exercise[exerciseName] = {"weight": weights, "reps": reps}
            workoutExercises.push(exercise);


        });
        workout.append("exercises", JSON.stringify(workoutExercises));

        workout.append("total_time", "0");

        // Add CSRF token
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        workout.append('csrfmiddlewaretoken', csrftoken);

        let url = "";
        const dateInput = document.getElementById("date");
        if (dateInput !== null) {
            workout.append("date", dateInput.value)
            url = "save_workout_session"
        }
        else {url = "save_workout"}


        // Send workout data and display response
        fetch(url, {method: "POST", body: workout})
            .then(response => response.json())
            .then(data => {
                if (data.success === true) {
                    showPopupWorkoutSaved("Workout saved.", 2500);
                }

            });
    });
}
