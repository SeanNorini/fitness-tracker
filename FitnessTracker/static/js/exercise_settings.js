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
        this.addExerciseSearchBar = new SearchBar_(
          this.addExerciseSearchHandler.bind(this),
        );
        this.addExerciseSearchBar.initialize("add-exercise-search-bar");
      });
  }

  addExerciseSearchHandler = (e) => {
    if (e.target.classList.contains("exercise-option")) {
      const exerciseName = e.target.textContent.trim();
      this.fetchExercise(exerciseName);
    }
  };

  loadExerciseSettingsEventListeners() {
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
    const exerciseName = document.getElementById("exercise-name").value;
    const exercisePK = document.getElementById("exercise-pk").value;

    FetchUtils.apiFetch({
      url: `${pageManager.baseURL}/workout/exercises/${exercisePK}`,
      method: "DELETE",
      successHandler: (response) => {
        this.addExerciseSearchBar.deleteItem(exerciseName);
        document.getElementById("exercise").remove();
      },
      errorHandler: (response) => {
        pageManager.showTempPopupMessage("Error. Please Try Again", 2000);
      },
    });
  }

  addNewExerciseListener() {
    document.getElementById("new-exercise").addEventListener("click", (e) => {
      const exerciseName = capitalize(prompt("Please enter name of exercise:"));

      // Check if a name was entered
      if (exerciseName) {
        if (
          !this.addExerciseSearchBar.addItem(exerciseName, "exercise-option")
        ) {
          pageManager.showTempPopupMessage(
            `${exerciseName} Already Exists`,
            2000,
          );
        }
        this.fetchExercise(exerciseName);
      }
    });
  }

  addSaveExerciseListener() {
    const saveExerciseButton = document.getElementById("save-exercise");
    saveExerciseButton.addEventListener("click", (e) => {
      this.saveExercise();
    });
  }

  exerciseExists() {
    const exercise = document.querySelector(".exercise");
    return !!exercise;
  }

  saveExercise() {
    if (this.exerciseExists()) {
      const formData = FormUtils.getFormData("exercise", true);
      console.log(formData);

      FetchUtils.apiFetch({
        url: `${pageManager.baseURL}/workout/exercises/${formData["exercise-pk"]}/`,
        method: "PUT",
        body: formData,
        successHandler: this.saveExerciseSuccessHandler,
        errorHandler: (response) =>
          pageManager.showTempPopupMessage("Error. Please Try Again", 2000),
      });
    }
  }

  saveExerciseSuccessHandler = (response) => {
    const exercisePK = document.getElementById("exercise-pk");
    exercisePK.value = response["id"];
    pageManager.showTempPopupMessage("Exercise Saved", 2000);
  };

  fetchExercise(exerciseName) {
    pageManager
      .fetchData({
        url: `${pageManager.baseURL}/workout/exercise_settings/edit_exercise/${exerciseName}`,
        method: "GET",
        responseType: "text",
      })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "exercises-container");
      });
  }
}
const exerciseSettingsManager = new ExerciseSettingsManager();
