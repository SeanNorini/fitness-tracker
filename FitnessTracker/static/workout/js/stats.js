function loadStats(){
    const selectExerciseDropdown = document.querySelector(".select_container");
    selectExerciseDropdown.addEventListener("change", e =>{
       getGraph();
    });

    document.querySelectorAll(".button_back").forEach(button => {
    button.addEventListener("click", function() {
        const group = this.getAttribute("data-group");
        const buttonsInGroup = document.querySelectorAll(`.button_back[data-group="${group}"]`);


        if (!this.classList.contains("active")) {
            buttonsInGroup.forEach(btn => {
                if (btn !== this) {
                    btn.classList.remove("active");
                }
            });

            this.classList.toggle("active");
        }

        const weightliftingButton = document.querySelector("#weightlifting");
        if (weightliftingButton.classList.contains("active")){
            selectExerciseDropdown.classList.remove("hidden");
        }
        else {
            selectExerciseDropdown.classList.add("hidden");
        }

        getGraph();
    });
});
}

function getGraph(){
    const formData = new FormData();
    const selections = document.querySelectorAll(".active");

    const dateRange = selections[0].value;
    formData.append("date_range", dateRange);

    const stat = selections[1].value;
    formData.append("stat", stat);

    if (stat === "weightlifting"){
        const exercise = document.querySelector(".select_exercise").value;
        formData.append("exercise", exercise);
    }

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    formData.append('csrfmiddlewaretoken', csrftoken)

    fetch(`http://${domain}/stats/`, {method:"POST", body:formData})
        .then(response => response.arrayBuffer())
        .then(buffer => {
        // Convert array buffer to Uint8Array
            const byteArray = new Uint8Array(buffer);

            // Convert bytes data to base64
            const base64String = btoa(String.fromCharCode(...byteArray));

            // Create image element and set src to base64 data
            const img = document.createElement('img');
            img.src = 'data:image/png;base64,' + base64String;
            const graphContainer = document.querySelector(".graph");
            graphContainer.innerHTML = "";
            graphContainer.appendChild(img);
    });
}
