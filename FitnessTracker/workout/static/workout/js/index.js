const controls = document.querySelector("#workout_form");

document.getElementById("date").valueAsDate = new Date();

controls.addEventListener("click", (e) => {
    e.preventDefault()

    if (e.target.classList.contains("delete_exercise")){
        e.target.closest(".exercise_container").remove(); 

        if (!document.querySelector(".add_set")){
            set_message("Please select a workout or add an exercise to get started.");
        }
    } 
    
    if (e.target.classList.contains("add_set")){
        
        fetch("add_set", {method: "GET"})
        .then(response => response.text())
        .then( template => {
            const setRow = document.createElement("template");
            setRow.innerHTML = template.trim();
            const container = e.target.closest(".exercise_container");
            container.querySelector(".sets").appendChild(setRow.content.firstChild);
            update_set_number(container);
        })
    }

    if (e.target.classList.contains("add_exercise")){
        const exercise = document.querySelector(".exercise").value;
        const exercises = document.querySelector("#exercises");

        fetch(("add_exercise/") + exercise, {method: "GET"})
        .then(response => response.text())
        .then(template => {
            const exercise = document.createElement("template");
            exercise.innerHTML = template.trim();    
            exercises.appendChild(exercise.content.firstChild);
        });

        const placeholder = document.querySelector("#placeholder");
        if (placeholder){placeholder.remove();}
    }

    if (e.target.classList.contains("delete_set")){
        e.target.closest(".set").remove();
    }

    if (e.target.classList.contains("save_workout")){
        // Check for workout to save
        const exercises = document.querySelectorAll(".exercise_container");
        if (exercises.length == 0){
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
                const setWeight = element.querySelector(".weight").value;
                weights.push(setWeight);

                const setReps = element.querySelector(".reps").value;
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
        if (document.querySelector("#session").value==="True"){
            url = "save_workout_session"
        }
        else{
            url = "save_workout"
        }


        // Send workout data and display response
        fetch(url, {method: "POST", body: workout})
        .then(response => response.text())
        .then(data => {
            if (data.success){
                set_message("Workout saved.");
            }
        });
    }

    if (e.target.classList.contains("edit_workouts")){
        fetch("edit_workouts", {method:"GET"})
        .then(response => response.text())
        .then(template => {
            const container = document.querySelector(".form_container");
            container.innerHTML = "";
            const editForm = document.createElement("template");
            editForm.innerHTML = template.trim();
            container.appendChild(editForm.content);
        });
    }

    if (e.target.classList.contains("exit_edit")){

        fetch("exit_edit", {method:"GET"})
        .then(response => response.text())
        .then(template => {
            const container = document.querySelector(".form_container");
            container.innerHTML = "";
            const editForm = document.createElement("template");
            editForm.innerHTML = template.trim();
            container.appendChild(editForm.content);
        });
    }

});

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

function update_set_number(container) {
    const sets = container.querySelectorAll(".set");
    sets[sets.length - 1].querySelector(".set_number").innerText = "Set " + sets.length + ":";

    }

controls.addEventListener("change", (e) => {
    if (e.target.classList.contains("workout")){
        workout = document.querySelector(".workout").value;

        const confirm = window.confirm("This will erase the current workout session, are you sure?")

        if (confirm){
            fetch("select_workout/" + workout, {method:"GET"})
            .then(response => response.text())
            .then(workoutHTML => {
                const exercises = document.querySelector("#exercises");
                exercises.innerHTML = workoutHTML;
            });
        }
    }
});