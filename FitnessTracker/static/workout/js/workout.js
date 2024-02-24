function add_set(e) {
    e.target.removeEventListener("click", add_set);
    fetch("add_set", {method: "GET"})
        .then(response => response.text())
        .then(template => {
            const setTemplate = document.createElement("template");
            setTemplate.innerHTML = template.trim();
            const container = e.target.closest(".exercise_container");
            const setElement = setTemplate.content.firstChild
            container.querySelector(".sets").appendChild(setElement);
            update_set_number(container);
            const deleteSetButton = setElement.querySelector(".delete_set");
            deleteSetButton.addEventListener("click", (e) => {
                e.preventDefault();
                delete_set(e)
            });
        })
}

function delete_set(e) {
    e.target.closest(".set").remove();
    e.target.removeEventListener("click", delete_set);
}

function delete_exercise (e)  {
    e.target.removeEventListener("click", delete_exercise);
    e.target.closest(".exercise_container").remove();

    if (!document.querySelector(".add_set")){
        set_message("Please select a workout or add an exercise to get started.");
    }
}


function set_message(message) {
    if (!document.querySelector("#placeholder")){
        const placeholder = document.createElement("div")
        placeholder.id = "placeholder";
        placeholder.style.minHeight = "15rem";
        placeholder.style.display = "flex";
        placeholder.style.alignItems = "center";
        placeholder.style.justifyContent ="center";
        document.querySelector("#exercises").prepend(placeholder);
    }

    placeholder.innerText = message;
}

function selectWorkoutEventListeners(){
    const exercises = document.querySelectorAll(".exercise_container");
    exercises.forEach(exercise => {
        const deleteExerciseButton = exercise.querySelector(".delete_exercise");
        deleteExerciseButton.addEventListener("click", (e) =>{
            e.preventDefault();
            delete_exercise(e);
        });

        const addSetButton = exercise.querySelector(".add_set");
        addSetButton.addEventListener("click", (e) =>{
            e.preventDefault();
            add_set(e);
        });



        const sets = exercise.querySelectorAll(".set");
        sets.forEach((currentSet, index) => {
            if (index > 0){
                deleteSetButton = currentSet.querySelector(".delete_set");
                deleteSetButton.addEventListener("click", (e) =>{
                e.preventDefault();
                delete_set(e);
                });
            }
        });
    });
}
function update_set_number(container) {
    const sets = container.querySelectorAll(".set");
    sets[sets.length - 1].querySelector(".set_number").innerText = "Set " + sets.length + ":";

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
                const exercises = document.querySelector("#exercises");
                exercises.innerHTML = workoutHTML;
                selectWorkoutEventListeners();
            });
        }
    });

    const add_exercise = document.querySelector(".add_exercise");

    add_exercise.addEventListener("click", (e) => {
        e.preventDefault();
        const exercise = document.querySelector(".exercise").value;
        const exercises = document.querySelector("#exercises");

        fetch(("add_exercise/") + exercise, {method: "GET"})
        .then(response => response.text())
        .then(template => {
            const exerciseTemplate = document.createElement("template");
            exerciseTemplate.innerHTML = template.trim();
            const exerciseElement = exerciseTemplate.content.firstChild;
            exercises.appendChild(exerciseElement);
            deleteExerciseButton = exerciseElement.querySelector(".delete_exercise");
            deleteExerciseButton.addEventListener("click", (e) =>{
                e.preventDefault();
                delete_exercise(e);
            });

            addSet = exerciseElement.querySelector(".add_set");
            addSet.addEventListener("click", (e) =>{
                e.preventDefault();
                add_set(e);
            });

        });

        const placeholder = document.querySelector("#placeholder");
        if (placeholder){placeholder.remove();}
    });
    const save_workout = document.querySelector(".save_workout");

    save_workout.addEventListener("click", (e) => {
        e.preventDefault();
        // Check for workout to save
        const exercises = document.querySelectorAll(".exercise_container");
        if (exercises.length == 0) {
            set_message("You must add at least one exercise before saving a workout session.");
            return
        }

        // Create form to gather data
        const workout = new FormData();

        // Get workout name
        const workoutName = document.querySelector(".workout").value;
        workout.append("name", workoutName);

        // Get exercise sets
        const workout_exercises = {"exercises": []}
        exercises.forEach(element => {
            const weights = [];
            const reps = [];
            const exercise_name = element.querySelector("#exercise_name").textContent.trim();

            const sets = element.querySelectorAll(".set");
            sets.forEach(element => {
                var setWeight = element.querySelector(".weight").value;
                if (setWeight === ""){
                    setWeight = 0;
                }
                weights.push(setWeight);

                var setReps = element.querySelector(".reps").value;
                if (setReps === ""){
                    setReps = 0;
                }
                reps.push(setReps);
            });
            var exercise = {};
            exercise[exercise_name] = {"weight": weights, "reps": reps}
            workout_exercises["exercises"].push(exercise);


        });
        workout.append("exercises", JSON.stringify(workout_exercises));


        // Add CSRF token
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        workout.append('csrfmiddlewaretoken', csrftoken);

        var url = "";
        dateInput = document.getElementById("date");
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
