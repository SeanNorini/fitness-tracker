class ExerciseSettingsManager {
  initialize() {
    pageManager
      .fetchData({
        url: `${pageManager.baseURL}/workout/exercise_settings/`,
        method: "GET",
        responseType: "text",
      })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "settings");
        this.loadExerciseSettingsEventListeners();
      });
  }

  loadExerciseSettingsEventListeners() {
    this.addExerciseSelectMenuListener();
    this.addNewExerciseListener();
    this.addSaveExerciseListener();
  }

  addNewExerciseListener() {
    document.getElementById("new_exercise").addEventListener("click", (e) => {
      this.addNewExercise();
    });
  }

  addNewExercise() {
    const exerciseName = prompt("Please enter name of exercise:");

    // Check if a name was entered
    if (exerciseName) {
      // Create a new option element
      const newOption = document.createElement("option");

      // Set the text content of the option to the entered name
      newOption.textContent = exerciseName;

      // Add the option to the select menu
      const selectMenu = document.getElementById("select_exercise");
      selectMenu.appendChild(newOption);
      newOption.selected = true;
      this.fetchExercise();
    }
  }

  addSaveExerciseListener() {
    const saveExerciseButton = document.getElementById("save_exercise");
    saveExerciseButton.addEventListener("click", (e) => {
      this.saveExerciseSettings();
    });
  }

  readExerciseSettings() {
    const formData = new FormData();
    const fiveRepMax = document.getElementById("five_rep_max");
    const defaultWeight = document.getElementById("default_weight");
    const defaultReps = document.getElementById("default_reps");
    const exerciseName = document.getElementById("select_exercise").value;
    const csrftoken = document.querySelector(
      "[name=csrfmiddlewaretoken]",
    ).value;

    formData.append("csrfmiddlewaretoken", csrftoken);
    formData.append("five_rep_max", fiveRepMax.value);
    formData.append("default_weight", defaultWeight.value);
    formData.append("default_reps", defaultReps.value);
    formData.append("name", exerciseName);

    return formData;
  }

  saveExerciseSettings() {
    const formData = this.readExerciseSettings();
    pageManager
      .fetchData({
        url: `${pageManager.baseURL}/workout/exercise_settings/edit_exercise/${formData.get("exerciseName")}`,
        method: "POST",
        body: formData,
        responseType: "json",
      })
      .then((response) => {
        if (response.success === true) {
          pageManager.showTempPopupMessage("Exercise Saved.", 2000);
        }
      });
  }

  addExerciseSelectMenuListener() {
    const selectMenu = document.getElementById("select_exercise");
    selectMenu.addEventListener("change", (e) => {
      this.fetchExercise();
    });
  }

  fetchExercise() {
    const selectMenu = document.getElementById("select_exercise");
    const exerciseName = selectMenu.value;

    pageManager
      .fetchData({
        url: `${pageManager.baseURL}/workout/exercise_settings/edit_exercise/${exerciseName}`,
        method: "GET",
        responseType: "text",
      })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "exercise");
      });
  }
}
const exerciseSettingsManager = new ExerciseSettingsManager();
