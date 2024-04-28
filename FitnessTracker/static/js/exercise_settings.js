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
      this.fetchExercise(e.target.dataset.pk);
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
      url: `${API.BASE_URL}${API.EXERCISES}${exercisePK}`,
      method: "DELETE",
      successHandler: (response) => {
        this.addExerciseSearchBar.deleteItem(exerciseName);
        this.clearExercise();
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
        this.createExercise(exerciseName);
      }
    });
  }

  clearExercise() {
    const element = document.getElementById("exercise");
    if (element) {
      element.remove();
    }
  }

  createExercise(name) {
    FetchUtils.apiFetch({
      url: `${API.BASE_URL}${API.EXERCISES}`,
      method: "POST",
      body: { name: name },
      successHandler: this.fetchExerciseSuccessHandler,
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
        url: `${API.BASE_URL}${API.EXERCISES}${formData["exercise-pk"]}/`,
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

  fetchExercise(pk) {
    FetchUtils.apiFetch({
      url: `${API.BASE_URL}${API.EXERCISES}${pk}`,
      method: "GET",
      successHandler: this.fetchExerciseSuccessHandler,
    });
  }

  fetchExerciseSuccessHandler = (data) => {
    this.clearExercise();
    const element = pageManager.cloneAndAppend(
      "exercise-template",
      "exercise-container",
    );
    pageManager.setValues(element, data);
    document.querySelector(".exercise-name").textContent = data["name"];
  };
}
const exerciseSettingsManager = new ExerciseSettingsManager();
