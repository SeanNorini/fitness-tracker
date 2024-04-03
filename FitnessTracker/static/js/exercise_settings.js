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
    this.addDeleteExerciseListener();
  }

  addDeleteExerciseListener() {
    document
      .getElementById("delete-exercise")
      .addEventListener("click", (e) => {
        this.deleteExercise();
      });
  }

  deleteExercise() {
    const exercisePK = document.getElementById("exercise-pk").value;
    const exerciseName = document.getElementById("select-exercise").value;
    pageManager
      .fetchData({
        url: `${pageManager.baseURL}/workout/exercise_settings/delete_exercise/${exerciseName}/${exercisePK}`,
        method: "POST",
        responseType: "json",
      })
      .then((response) => {
        if (response.success) {
          pageManager.showTempPopupMessage("Exercise Deleted.", 2000);
          document.querySelector(".exercise").remove();
          pageManager.updateDropdownMenu({
            option: exerciseName,
            action: "remove",
            selector: "#select-exercise",
            placeholder: "Select an Exercise",
          });
        }
      });
  }

  addNewExerciseListener() {
    document.getElementById("new-exercise").addEventListener("click", (e) => {
      this.addNewExercise();
    });
  }

  addNewExercise() {
    const exerciseName = prompt("Please enter name of exercise:");

    // Check if a name was entered
    if (exerciseName) {
      pageManager.updateDropdownMenu({
        option: exerciseName,
        action: "add",
        selector: "#select-exercise",
      });
      this.fetchExercise();
    }
  }

  addSaveExerciseListener() {
    const saveExerciseButton = document.getElementById("save-exercise");
    saveExerciseButton.addEventListener("click", (e) => {
      this.saveExerciseSettings();
    });
  }

  readExerciseSettings() {
    const formData = new FormData();
    const fiveRepMax = document.getElementById("five-rep-max").value;
    const defaultWeight = document.getElementById("default-weight").value;
    const defaultReps = document.getElementById("default-reps").value;
    const exerciseName = document.getElementById("select-exercise").value;

    formData.append("csrfmiddlewaretoken", pageManager.csrftoken);
    formData.append("five_rep_max", fiveRepMax);
    formData.append("default_weight", defaultWeight);
    formData.append("default_reps", defaultReps);
    formData.append("name", exerciseName);

    return formData;
  }

  validExerciseSettings() {
    const exercise = document.querySelector(".exercise");
    return !!exercise;
  }

  saveExerciseSettings() {
    if (this.validExerciseSettings()) {
      const formData = this.readExerciseSettings();
      pageManager
        .fetchData({
          url: `${pageManager.baseURL}/workout/exercise_settings/edit_exercise/${formData.get("name")}`,
          method: "POST",
          body: formData,
          responseType: "json",
        })
        .then((response) => {
          if (response.success === true) {
            pageManager.showTempPopupMessage("Exercise Saved.", 2000);
          }
        });
    } else {
      pageManager.showTempPopupMessage("No Exercise Selected.", 2000);
    }
  }

  addExerciseSelectMenuListener() {
    const selectMenu = document.getElementById("select-exercise");
    selectMenu.addEventListener("change", (e) => {
      this.fetchExercise();
    });
  }

  fetchExercise() {
    const selectMenu = document.getElementById("select-exercise");
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
