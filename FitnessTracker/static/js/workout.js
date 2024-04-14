class WorkoutManager {
  constructor() {
    this.unsavedChanges = false;
    this.restTimerRunning = false;
    this.baseURL = pageManager.baseURL + "/workout";
    this.dragAndDrop = new DragAndDrop();
  }

  initialize() {
    this.setDate();
    this.addSaveWorkoutBtnListener();

    this.showRestTimerSetting =
      document.getElementById("show-rest-timer").value;
    this.showWorkoutTimerSetting =
      document.getElementById("show-workout-timer").value;

    this.dragAndDrop.initialize();

    this.selectWorkoutSearchBar = new SearchBar_(
      this.selectWorkoutSearchHandler,
    );
    this.selectWorkoutSearchBar.initialize("select-workout-search-bar");

    this.addExerciseSearchBar = new SearchBar_(this.addExerciseSearchHandler);
    this.addExerciseSearchBar.initialize("add-exercise-search-bar");

    const routine = document.getElementById("routine");
    if (routine) {
      this.addNavigateRoutineListeners();
    }

    this.addWorkoutListeners();
  }

  addNavigateRoutineListeners() {
    const navNext = document.getElementById("nav-next");
    navNext.addEventListener("click", this.navigateRoutineWorkoutHandler);
    const navPrev = document.getElementById("nav-before");
    navPrev.addEventListener("click", this.navigateRoutineWorkoutHandler);
  }

  navigateRoutineWorkoutHandler = (e) => {
    const direction = e.target.id === "nav-before" ? "prev" : "next";
    pageManager
      .fetchData({
        url: `${this.baseURL}/get_routine_workout/${direction}`,
        method: "GET",
        responseType: "text",
      })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "content");
        this.initialize();
      });
  };

  getSelectWorkoutConfirmation() {
    let confirm = true;
    if (this.unsavedChanges) {
      confirm = window.confirm(
        "This will erase the current workout session, are you sure?",
      );
    }
    return confirm;
  }

  selectWorkoutSearchHandler = (e) => {
    if (e.target.classList.contains("workout-option")) {
      if (this.getSelectWorkoutConfirmation()) {
        this.fetchWorkout(e.target.textContent.trim());
        this.selectWorkoutSearchBar.searchInput.value =
          e.target.textContent.trim();
        this.unsavedChanges = false;
      }
    }
  };

  fetchWorkout(workoutName) {
    pageManager
      .fetchData({
        url: `${this.baseURL}/select_workout/${workoutName}`,
        method: "GET",
        responseType: "text",
      })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "workout-container");
        this.addWorkoutListeners();
      });
  }

  addWorkoutListeners() {
    const exercises = document.querySelectorAll(".exercise");
    exercises.forEach((exercise) => {
      this.addExerciseContainerListeners(exercise);
    });
    if (this.nav) {
      this.addNavigateRoutineListeners();
    }
  }

  fetchExercise(exerciseName) {
    pageManager
      .fetchData({
        url: `${this.baseURL}/add_exercise/${exerciseName}`,
        method: "GET",
        responseType: "text",
      })
      .then((exerciseHTML) => {
        this.updateExercises(exerciseHTML);
      });
  }

  updateExercises(exerciseHTML) {
    const exercisesContainer = document.getElementById("workout-container");
    const newExercise = pageManager.createElementFromHTMLText(exerciseHTML);
    exercisesContainer.appendChild(newExercise);
    this.addExerciseContainerListeners(newExercise);
  }

  addExerciseSearchHandler = (e) => {
    if (e.target.classList.contains("exercise-option")) {
      const exerciseName = e.target.textContent.trim();
      this.fetchExercise(exerciseName);
      this.unsavedChanges = true;
    }
  };

  addExerciseContainerListeners(container) {
    this.addDeleteExerciseSetListener(container);
    this.addAddExerciseSetListener(container);
    this.addDeleteExerciseListener(container);

    if (this.showRestTimerSetting === "True") {
      this.addSetCompleteListeners(container);
    }
  }

  addDeleteExerciseListener(container) {
    container
      .querySelector(".delete-exercise")
      .addEventListener("click", (e) => {
        e.stopPropagation();
        this.deleteExercise(container);
      });
  }

  addAddExerciseSetListener(container) {
    container.querySelector(".add-set").addEventListener("click", (e) => {
      this.addExerciseSet(container);
    });
  }

  addDeleteExerciseSetListener(container) {
    container.querySelector(".delete-set").addEventListener("click", (e) => {
      this.deleteSet(container);
    });
  }

  addSetCompleteListeners(container) {
    container.querySelectorAll(".set").forEach((exerciseSet) => {
      this.addSetCompleteListener(exerciseSet);
    });
  }

  addSetCompleteListener(exerciseSet) {
    // Add listener to set checkbox
    const setCompleteCheckbox = exerciseSet.querySelector(".set-complete");
    setCompleteCheckbox.addEventListener("click", (e) => {
      this.setComplete(e);
    });
  }

  deleteExercise(container) {
    container.remove();

    // Display message if no exercises are selected
    if (!document.querySelector(".exercise")) {
      this.setMessage(
        "Please select a workout or add an exercise to get started.",
      );
    }
    this.unsavedChanges = true;
  }

  addExerciseSet(container) {
    const exerciseName = container.querySelector(".exercise-name").textContent;
    fetch(`${this.baseURL}/add_set/${exerciseName}`, { method: "GET" })
      .then((response) => response.text())
      .then((contentHTML) => {
        // Add new set to exercise
        const newExerciseSetElement =
          pageManager.createElementFromHTMLText(contentHTML);
        container.querySelector(".sets").appendChild(newExerciseSetElement);
        this.updateSetNumber(container);

        if (this.showRestTimerSetting === "True") {
          this.addSetCompleteListener(newExerciseSetElement);
        }
        this.unsavedChanges = true;
      });
  }

  deleteSet(container) {
    // Remove last set from an exercise
    const lastSet = container.querySelector(".set:last-child");
    lastSet.remove();
    this.unsavedChanges = true;
  }

  setComplete(e) {
    if (e.target.checked) {
      this.showRestTimer();
    }
  }

  updateSetNumber(exerciseContainer) {
    // Update set number for last added set in exercise
    const exerciseSets = exerciseContainer.querySelectorAll(".set");
    exerciseSets[exerciseSets.length - 1].querySelector(
      ".set-number",
    ).innerText = "Set " + exerciseSets.length + ":";
  }

  setMessage(message) {
    // Display message to user when no exercises are selected
    const messageContainer = document.querySelector("#message");
    messageContainer.innerText = message;
  }

  restTimer() {
    const restTimerElement = document.getElementById("timer");
    let minutes = 0;
    let seconds = 0;

    // Function to update timer display
    const updateRestTimer = () => {
      seconds++;

      if (seconds === 60) {
        seconds = 0;
        minutes++;
      }

      const formattedMinutes = minutes < 10 ? "0" + minutes : minutes;
      const formattedSeconds = seconds < 10 ? "0" + seconds : seconds;

      restTimerElement.textContent = formattedMinutes + ":" + formattedSeconds;

      if (this.restTimerRunning) {
        setTimeout(updateRestTimer, 1000);
      }
    };

    return {
      stop: () => {
        // Stop timer and reset display
        this.restTimerRunning = false;
        minutes = 0;
        seconds = 0;
        restTimerElement.textContent = "00:00";
      },
      start: () => {
        // Start timer
        this.restTimerRunning = true;
        updateRestTimer();
      },
    };
  }

  showRestTimer() {
    const restTimerInstance = this.restTimer();
    if (!this.restTimerRunning) {
      restTimerInstance.start(); // Start the timer when showing the popup
    }
    pageManager.openPopup("rest-timer-popup", restTimerInstance.stop);
  }

  setDate(date) {
    // Set calendar date on workout, default to current date.
    if (!date) {
      const currentDate = new Date();
      document.getElementById("date").valueAsDate = new Date(
        currentDate.getTime() - currentDate.getTimezoneOffset() * 60000,
      );
    } else {
      document.getElementById("date").valueAsDate = date;
    }
  }

  addSaveWorkoutBtnListener() {
    const saveWorkoutBtn = document.querySelector("#save-workout");
    saveWorkoutBtn.addEventListener("click", () => {
      this.saveWorkout(this.saveWorkoutSuccessHandler);
    });
  }

  validateWorkoutForm() {
    // Check for workout to save
    const exercises = document.querySelectorAll(".exercise");
    if (exercises.length === 0) {
      this.setMessage(
        "You must add at least one exercise before saving a workout session.",
      );
    }
    return exercises;
  }

  saveWorkout(successHandler, errorHandler = null) {
    // Verify form has exercises to save
    const exercises = this.validateWorkoutForm();
    if (exercises.length === 0) {
      return;
    }

    // Gather form data
    const formData = this.readCurrentWorkout(exercises);

    // Send workout data and display response
    FetchUtils.apiFetch({
      url: `${pageManager.baseURL}/log/workout_log/`,
      method: "POST",
      body: formData,
      successHandler: (response) => successHandler(response),
      errorHandler: (response) => {
        this.saveWorkoutErrorHandler(response);
      },
    });
  }

  saveWorkoutSuccessHandler(response) {
    pageManager.showTempPopupMessage("Workout Saved", 2000);
  }

  saveWorkoutErrorHandler = (response) => {
    pageManager.showTempPopupErrorMessages(response, 2000);
  };

  workoutNotInList(workoutName) {
    const workouts = document.querySelectorAll(".workout-option");
    workouts.forEach((workout) => {
      if (workout.textContent.trim() === workoutName) {
        return true;
      }
    });
    return false;
  }

  readCurrentWorkout(exercises) {
    // Add workout name
    let workoutName = document.getElementById("select-workout").value;
    if (workoutName === "Rest Day" || this.workoutNotInList()) {
      workoutName = "Custom Workout";
    }
    const workoutData = { workout_name: workoutName, workout_exercises: [] };
    const dateInput = document.getElementById("date");
    workoutData["date"] = dateInput.value;
    workoutData["total_time"] = "0";

    exercises.forEach((exercise, index) => {
      const exerciseName = exercise
        .querySelector(".exercise-name")
        .textContent.trim();

      workoutData["workout_exercises"].push({
        [exerciseName]: { reps: [], weights: [] },
      });

      const exerciseSets = exercise.querySelectorAll(".set");
      exerciseSets.forEach((exerciseSet) => {
        let setWeight = exerciseSet.querySelector(".weight").value;
        if (setWeight === "") {
          setWeight = 0;
        }

        let setReps = exerciseSet.querySelector(".reps").value;
        if (setReps === "") {
          setReps = 0;
        }
        workoutData["workout_exercises"][index][exerciseName]["weights"].push(
          setWeight,
        );
        workoutData["workout_exercises"][index][exerciseName]["reps"].push(
          setReps,
        );
      });
    });
    return workoutData;
  }
}

class WorkoutSettingsManager extends WorkoutManager {
  constructor() {
    super();
    this.baseURL = pageManager.baseURL + "/workout/workout_settings";
  }

  addExerciseContainerListeners(container) {
    this.addDeleteExerciseSetListener(container);
    this.addAddExerciseSetListener(container);
    this.addDeleteExerciseListener(container);

    // Add input listeners to each exercise set
    const exerciseSets = container.querySelectorAll(".set");
    exerciseSets.forEach((exerciseSet) => {
      this.addWorkoutSettingsInputListeners(exerciseSet);
    });

    // Add input listener to five rep max
    const fiveRepMaxInput = container.querySelector("input.max-rep");
    this.addFiveRepMaxListener(fiveRepMaxInput);
  }

  addWorkoutSettingsInputListeners(exerciseSet) {
    // Add input listeners
    const roundedFloatInput = this.addRoundedFloatInputListener(exerciseSet);
    this.addRoundedIntegerInputListener(exerciseSet);
    this.addModifierInputListener(exerciseSet);

    // Update set calculation
    const event = new KeyboardEvent("keyup", { key: "Enter" });
    roundedFloatInput.dispatchEvent(event);
  }

  addRoundedFloatInputListener(exerciseSet) {
    // On blur or keyup, update weight input to nearest .25 and update set calculation
    const roundedFloatInput = exerciseSet.querySelector("input.round-float");
    roundedFloatInput.addEventListener("blur", (e) => {
      let value = parseFloat(roundedFloatInput.value);
      value = this.validateNumberInput(value, 0, 1500);
      roundedFloatInput.value = Math.round(value / 0.25) * 0.25;
    });

    roundedFloatInput.addEventListener("keyup", (e) => {
      this.updateSet(e);
    });

    // Return input element for initial update
    return roundedFloatInput;
  }

  addRoundedIntegerInputListener(exerciseSet) {
    // On keyup round reps to nearest integer and update set calculation
    const roundedIntegerInput = exerciseSet.querySelector(
      "input.round-integer",
    );
    roundedIntegerInput.addEventListener("keyup", (e) => {
      let value = parseInt(roundedIntegerInput.value);
      value = this.validateNumberInput(value, 0, 100);
      roundedIntegerInput.value = value;
      this.triggerUpdateSet(e);
    });
  }

  validateNumberInput(value, min, max) {
    if (isNaN(value) || value < min) {
      value = min;
    }
    if (value > max) {
      value = max;
    }
    return value;
  }

  addModifierInputListener(exerciseSet) {
    // On modifier change update set calculation
    const modifierInput = exerciseSet.querySelector(".modifier");
    modifierInput.addEventListener("change", (e) => {
      this.triggerUpdateSet(e);
    });
  }

  triggerUpdateSet(e) {
    // Trigger weight input listener to update set
    const weightInput = e.target
      .closest(".set")
      .querySelector("input.round-float");
    const event = new KeyboardEvent("keyup", { key: "Enter" });
    weightInput.dispatchEvent(event);
    this.unsavedChanges = true;
  }

  addFiveRepMaxListener(inputFiveRepMax) {
    //
    inputFiveRepMax.addEventListener("blur", this.fiveRepMaxHandler);
    inputFiveRepMax.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        this.fiveRepMaxHandler(e);
      }
    });
  }

  fiveRepMaxHandler = (e) => {
    let value = parseFloat(e.target.value);
    value = this.validateNumberInput(value, 0, 1500);
    e.target.value = Math.round(value / 0.25) * 0.25;

    // Update set calculations for exercise
    const exerciseSets = e.target.closest(".exercise").querySelectorAll(".set");
    exerciseSets.forEach((exerciseSet) => {
      const amountInput = exerciseSet.querySelector(".amount");
      const event = new KeyboardEvent("keyup", { key: "Enter" });
      amountInput.dispatchEvent(event);
    });
  };

  updateSet(e) {
    // Get inputs to calculate set
    const amount = parseFloat(e.target.value);
    const setContainer = e.target.closest(".set");
    const modifier = setContainer.querySelector(".modifier").value;
    const fiveRepMax = parseFloat(
      e.target.closest(".exercise").querySelector("input.max-rep").value,
    );
    const reps = e.target.closest(".set").querySelector("input.reps").value;

    // Update set calculation
    const calculateSetContainer = setContainer.querySelector(".calculate-set");
    switch (modifier) {
      case "exact":
        calculateSetContainer.textContent = `${amount} ${weightUnit} x ${reps}`;
        break;
      case "percentage":
        calculateSetContainer.textContent =
          `${(Math.round(fiveRepMax * (amount / 100)) * 0.25) / 0.25} ` +
          `${weightUnit} x ${reps}`;
        break;
      case "increment":
        calculateSetContainer.textContent = `${fiveRepMax + amount} ${weightUnit} x ${reps}`;
        break;
      case "decrement":
        calculateSetContainer.textContent = `${fiveRepMax - amount} ${weightUnit} x ${reps}`;
        break;
    }
  }

  initialize() {
    pageManager
      .fetchData({
        url: `${this.baseURL}`,
        method: "GET",
        responseType: "text",
      })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "settings");
        this.addWorkoutContainerListeners();
        this.dragAndDrop.initialize();
        this.selectWorkoutSearchBar = new SearchBar_(
          this.selectWorkoutSearchHandler,
        );
        this.selectWorkoutSearchBar.initialize("select-workout-search-bar");

        this.addExerciseSearchBar = new SearchBar_(
          this.addExerciseSearchHandler,
        );
        this.addExerciseSearchBar.initialize("add-exercise-search-bar");
      });
  }

  addWorkoutContainerListeners() {
    this.addSaveWorkoutSettingsListener();
    this.addSaveWorkoutBtnListener();
  }

  addSaveWorkoutSettingsListener() {
    const saveWorkoutSettingsBtn = document.getElementById(
      "save-workout-settings",
    );
    saveWorkoutSettingsBtn.addEventListener("click", (e) => {
      this.saveWorkoutSettings();
    });
  }

  addExerciseSet(container) {
    const exerciseName = document.querySelector(".exercise-name").textContent;
    fetch(`${this.baseURL}/add_set/${exerciseName}`, { method: "GET" })
      .then((response) => response.text())
      .then((contentHTML) => {
        // Add new set to exercise
        const newExerciseSetElement =
          pageManager.createElementFromHTMLText(contentHTML);
        container.querySelector(".sets").appendChild(newExerciseSetElement);
        this.addWorkoutSettingsInputListeners(newExerciseSetElement);
        this.updateSetNumber(container);
        this.unsavedChanges = true;
      });
  }

  readWorkoutSettings() {
    const formData = new FormData();
    const autoUpdateFiveRepMax = document.getElementById(
      "id_auto_update_five_rep_max",
    );
    const showRestTimer = document.getElementById("id_show_rest_timer");
    const showWorkoutTimer = document.getElementById("id_show_workout_timer");

    formData.append("auto_update_five_rep_max", autoUpdateFiveRepMax.checked);
    formData.append("show_rest_timer", showRestTimer.checked);
    formData.append("show_workout_timer", showWorkoutTimer.checked);

    return formData;
  }

  saveWorkoutSettings() {
    // Get settings data
    const formData = this.readWorkoutSettings();

    pageManager
      .fetchData({
        url: `${this.baseURL}/save_workout_settings/`,
        method: "POST",
        body: formData,
        responseType: "json",
      })
      .then((response) => {
        if (response.success === true) {
          const successMessage = document.querySelector(".success-message");
          successMessage.classList.remove("hidden");
          setTimeout(() => {
            successMessage.classList.add("hidden");
          }, 3000);
        }
      });
  }
  saveWorkout(successHandler, errorHandler = null) {
    const exercises = this.validateWorkoutForm();
    if (exercises.length === 0) {
      return;
    }

    // Get data from current workout
    const formData = this.readCurrentWorkout();
    const method = this.overwrite ? "PUT" : "POST";
    const pk = this.overwrite
      ? document.getElementById("workout-pk").value + "/"
      : "";
    if (!formData) {
      pageManager.showTempPopupMessage(
        "Workout Not Saved. Please Enter A Workout Name",
        2000,
      );
      return;
    }

    FetchUtils.apiFetch({
      url: `${pageManager.baseURL}/workout/workouts/${pk}`,
      method: method,
      body: formData,
      successHandler: (response) => {
        pageManager.showTempPopupMessage("Workout Saved", 2000);
        this.selectWorkoutSearchBar.addItem(formData["name"], "workout-option");
      },
      errorHandler: {},
    });
  }

  readCurrentWorkout(exercises) {
    // Get workout name, returns null if user didn't confirm
    const workoutName = this.saveWorkoutConfirmation();
    if (workoutName === null || workoutName.trim() === "") {
      return;
    }
    const workoutData = { name: workoutName, exercises: [], config: [] };

    // Iterate form fields and populate FormData
    const workoutExercises = document.querySelectorAll(".exercise");
    workoutExercises.forEach((exercise) => {
      const exerciseName = exercise
        .querySelector(".exercise-name")
        .textContent.trim();
      const fiveRepMax = parseFloat(
        exercise.querySelector("input.max-rep").value,
      );
      const exercisePK = exercise.querySelector("[name='exercise-pk']").value;
      workoutData["exercises"].push(exercisePK);

      const currentExercise = {
        name: exerciseName,
        pk: exercisePK,
        five_rep_max: fiveRepMax,
        sets: [],
      };

      const exerciseSets = exercise.querySelectorAll(".set");
      exerciseSets.forEach((exerciseSet) => {
        const currentSet = {};
        currentSet["amount"] = parseFloat(
          exerciseSet.querySelector(".amount").value,
        );
        currentSet["modifier"] = exerciseSet.querySelector(".modifier").value;
        currentSet["reps"] = parseInt(exerciseSet.querySelector(".reps").value);

        currentExercise["sets"].push(currentSet);
      });

      workoutData["config"].push(currentExercise);
    });
    return workoutData;
  }

  saveWorkoutConfirmation() {
    let workoutName = document.getElementById("workout-name").value;
    let confirm = null;
    if (workoutName !== "Custom Workout") {
      confirm = window.confirm(
        `This will save new settings to workout "${workoutName}." Are you sure?`,
      );
    }

    if (!confirm) {
      workoutName = window.prompt(
        `Please enter a name for the new workout or close this window to cancel.`,
      );
    }

    if (
      confirm === null &&
      this.selectWorkoutSearchBar.itemExists(workoutName)
    ) {
      this.saveWorkoutConfirmation();
    }
    if (confirm) {
      this.overwrite = true;
    }
    return workoutName;
  }
}

class WorkoutLogManager extends WorkoutManager {
  initialize() {
    this.setDate();
    this.addSaveWorkoutBtnListener();

    this.dragAndDrop.initialize("-20rem");

    this.selectWorkoutSearchBar = new SearchBar_(
      this.selectWorkoutSearchHandler.bind(this),
    );
    this.selectWorkoutSearchBar.initialize("select-workout-search-bar");

    this.addExerciseSearchBar = new SearchBar_(
      this.addExerciseSearchHandler.bind(this),
    );
    this.addExerciseSearchBar.initialize("add-exercise-search-bar");

    this.addWorkoutListeners();
  }

  setDate() {
    const monthAndYear = document.querySelector("#month-name");
    const month = parseInt(monthAndYear.dataset.month) - 1;
    const year = parseInt(monthAndYear.dataset.year);
    const day = parseInt(logManager.currentLog.dataset.day);
    document.getElementById("date").valueAsDate = new Date(year, month, day);
  }

  updateWorkoutLog(workoutLogPK, successHandler) {
    // Verify form has exercises to save
    const exercises = this.validateWorkoutForm();
    if (exercises.length === 0) {
      return;
    }

    // Gather form data
    const formData = this.readCurrentWorkout(exercises);

    FetchUtils.apiFetch({
      url: `${pageManager.baseURL}/log/workout_log/${workoutLogPK}/`,
      method: "PATCH",
      body: formData,
      successHandler: (response) => successHandler(response),
      errorHandler: (response) =>
        pageManager.showTempPopupMessage(
          "Update Failed. Please Try Again.",
          2000,
        ),
    });
  }

  saveWorkout(successHandler, errorHandler = null) {
    return super.saveWorkout(successHandler);
  }

  addSaveWorkoutBtnListener() {
    return;
  }
}

window.workoutManager = new WorkoutManager();
window.workoutSettingsManager = new WorkoutSettingsManager();
