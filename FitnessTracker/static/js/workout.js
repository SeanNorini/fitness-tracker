class BaseWorkoutManager {
  constructor() {
    this.baseURL = pageManager.baseURL + "/workout";
    this.addExerciseSearchBar = new SearchBar_(this.addExerciseSearchHandler);
    this.selectWorkoutSearchBar = new SearchBar_(
      this.selectWorkoutSearchHandler,
    );
    this.unsavedChanges = false;
    this.dragAndDrop = new DragAndDrop();
    this.pk = null;
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

  initialize() {
    this.selectWorkoutSearchBar.initialize("select-workout-search-bar");
    this.addExerciseSearchBar.initialize("add-exercise-search-bar");
    this.saveWorkoutBtn = document.getElementById("save-workout");
    this.workoutController = document.getElementById("workout-container");
    this.addWorkoutListeners();
  }

  addExerciseSearchHandler = (e) => {
    if (e.target.classList.contains("exercise-option")) {
      const exercisePK = e.target.dataset.pk;
      this.addExercise(exercisePK);
      this.unsavedChanges = true;
      this.addExerciseSearchBar.closeSearchList(e);
    }
  };

  selectWorkoutSearchHandler = (e) => {
    if (e.target.classList.contains("workout-option")) {
      if (
        this.getConfirmation(
          "This will erase the current workout, are you sure?",
        )
      ) {
        this.fetchWorkout(e.target.dataset.pk);
        this.selectWorkoutSearchBar.setValue(e.target.textContent);
        this.unsavedChanges = false;
        this.selectWorkoutSearchBar.closeSearchList(e);
      }
    }
  };

  getConfirmation(message) {
    let confirm = true;
    if (this.unsavedChanges) {
      confirm = window.confirm(message);
    }
    return confirm;
  }

  fetchWorkout(workoutPK) {
    FetchUtils.apiFetch({
      url: `${API.BASE_URL}${API.WORKOUTS}${workoutPK}/?configure=True`,
      method: "GET",
      successHandler: this.fetchWorkoutSuccessHandler.bind(this),
    });
  }

  fetchWorkoutSuccessHandler(data) {
    this.clearWorkout();
    for (let i = 0; i < data["exercises"].length; i++) {
      const exercise = data["exercises"][i];
      this.updateExercises(exercise);
    }
    this.updateRoutineHeader(data);
    this.unsavedChanges = false;
  }

  updateRoutineHeader(data) {
    if (!data["routine_name"]) {
      return;
    }
    const header = document.getElementById("workout-routine");
    header.textContent = `${data["routine_name"]}, Week #${data["week"]}, Day#${data["day"]}`;
    this.selectWorkoutSearchBar.setValue(data["workout_name"]);
  }

  clearWorkout() {
    const exercises = document.querySelectorAll(".exercise");
    exercises.forEach((exercise) => {
      this.deleteExercise(exercise);
    });
  }

  addExercise(exercisePK) {
    //Retrieves exercise information from API and on success updates the exercises in the workout
    FetchUtils.apiFetch({
      url: `${API.BASE_URL}${API.EXERCISES}${exercisePK}`,
      method: "GET",
      successHandler: this.updateExercises,
    });
  }

  updateExercises = (exercise) => {
    const element = pageManager.cloneAndAppend(
      "exercise-template",
      "workout-container",
    );
    this.setExerciseValues(element, exercise);
    this.addExerciseSets(element, exercise["sets"]);
  };

  setExerciseValues(element, values) {
    pageManager.setValues(element, values);
    element.querySelector(".exercise-name").textContent = values["name"];
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

  addExerciseSets(container, exerciseSets = null) {
    let sets = exerciseSets;
    if (!sets) {
      sets = {
        weights: [container.querySelector(".default_weight").value],
        reps: [container.querySelector(".default_reps").value],
      };
    }
    for (let i = 0; i < sets["weights"].length; i++) {
      const element = pageManager.cloneAndAppend(
        "exercise-set-template",
        container.querySelector(".sets"),
      );
      const weight = sets["weights"][i];
      const reps = sets["reps"][i];
      this.setExerciseSetValues(element, container, {
        weight: weight,
        reps: reps,
      });
    }
    this.unsavedChanges = true;
  }

  setExerciseSetValues(element, container, values) {
    pageManager.setValues(element, values);
    this.updateExerciseSetNumber(container);
  }

  deleteExerciseSet(container) {
    const lastSet = container.querySelector(".set:last-child");
    lastSet.remove();
    this.unsavedChanges = true;
  }

  updateExerciseSetNumber(container) {
    // Update set number for last added set in exercise
    const exerciseSets = container.querySelectorAll(".set");
    exerciseSets[exerciseSets.length - 1].querySelector(
      ".set-number",
    ).innerText = "Set " + exerciseSets.length + ":";
  }

  setMessage(message) {
    // Display message to user when no exercises are selected
    const messageContainer = document.querySelector("#message");
    messageContainer.innerText = message;
  }

  addWorkoutListeners() {
    this.workoutController.addEventListener("click", (e) => {
      switch (true) {
        case e.target.classList.contains("delete-exercise"):
          e.stopPropagation();
          this.deleteExercise(e.target.closest(".exercise"));
          break;
        case e.target.classList.contains("add-set"):
          this.addExerciseSets(e.target.closest(".exercise"));
          break;
        case e.target.classList.contains("delete-set"):
          this.deleteExerciseSet(e.target.closest(".exercise"));
          break;
      }
    });

    this.saveWorkoutBtn.addEventListener("click", () => {
      this.saveWorkout();
    });

    this.workoutController.addEventListener("focusout", (e) => {
      if (e.target.dataset.type === "float") {
        InputUtils.roundedFloatHandler(e.target, 0, 1500, 0.5);
      } else if (e.target.dataset.type === "int") {
        InputUtils.roundedIntegerHandler(e.target, 0, 100);
      }
    });
    this.workoutController.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && e.target.dataset.type === "float") {
        InputUtils.roundedFloatHandler(e.target, 0, 1500, 0.5);
      } else if (e.key === "Enter" && e.target.dataset.type === "int") {
        InputUtils.roundedIntegerHandler(e.target, 0, 100);
      }
    });
  }

  saveWorkout() {
    // Verify form has exercises to save
    const exercises = this.validateWorkoutForm();
    if (exercises.length === 0) {
      return;
    }

    // Gather form data
    const formData = this.readWorkout(exercises);

    let url = "";
    if (this.pk) {
      url = `${API.BASE_URL}${API.WORKOUT_LOGS}${this.pk}/`;
    } else {
      url = `${API.BASE_URL}${API.WORKOUT_LOGS}`;
    }

    // Send workout data and display response
    FetchUtils.apiFetch({
      url: url,
      method: !this.pk ? "POST" : "PUT",
      body: formData,
      successHandler: (response) => this.saveWorkoutSuccessHandler(response),
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
    // Check if the workout exists in the workout options and return a boolean
    const workouts = document.querySelectorAll(".workout-option");
    workouts.forEach((workout) => {
      if (workout.textContent.trim() === workoutName) {
        return true;
      }
    });
    return false;
  }

  readWorkout(exercises) {
    // Add workout name
    let workoutName = document.getElementById("select-workout").value;
    if (workoutName === "Rest Day" || this.workoutNotInList()) {
      workoutName = "Custom Workout";
    }
    const workoutData = { workout_name: workoutName, workout_exercises: [] };
    const dateInput = document.getElementById("date");
    workoutData["date"] = dateInput.value;
    workoutData["total_time"] = this.workoutTimer
      ? this.workoutTimer.getDurationSeconds()
      : "0";

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

class WorkoutManager extends BaseWorkoutManager {
  constructor() {
    super();
  }

  initialize() {
    this.dateInput = document.getElementById("date");
    this.showRestTimerSetting =
      document.getElementById("show-rest-timer").value;
    this.showWorkoutTimerSetting =
      document.getElementById("show-workout-timer").value;

    this.routine = document.getElementById("workout-routine");
    if (this.routine) {
      this.navNext = document.getElementById("nav-next");
      this.navPrev = document.getElementById("nav-before");
    }
    this.dateInput.valueAsDate = getCurrentDate();
    this.dragAndDrop.initialize();
    this.initializeTimers();
    super.initialize();
  }

  initializeTimers() {
    if (this.showRestTimerSetting === "True") {
      this.restTimer = new Timer("rest-timer-display");
    } else {
      this.restTimer = null;
    }

    if (this.showWorkoutTimerSetting === "True") {
      this.timerBtn = document.getElementById("timer-btn");
      this.resetTimerBtn = document.getElementById("reset-timer-btn");
      this.timerControl = document.querySelector(".timer-control");
      this.workoutTimer = new Timer("workout-timer", {
        resetOnStop: false,
        showHours: true,
      });
    } else {
      this.workoutTimer = null;
    }
  }

  addWorkoutListeners() {
    super.addWorkoutListeners();
    this.workoutController.addEventListener("click", (e) => {
      if (e.target.classList.contains("set-complete")) {
        this.setComplete(e);
      }
    });

    if (this.routine) {
      this.navNext.addEventListener(
        "click",
        this.navigateRoutineWorkoutHandler,
      );
      this.navPrev.addEventListener(
        "click",
        this.navigateRoutineWorkoutHandler,
      );
    }

    if (this.showWorkoutTimerSetting === "True") {
      this.timerBtn.addEventListener("click", this.workoutTimerHandler);
      this.resetTimerBtn.addEventListener(
        "click",
        this.workoutResetTimerHandler,
      );
    }

    this.dateInput.addEventListener("change", (e) => {
      this.dateHandler();
    });
  }

  workoutTimerHandler = (e) => {
    if (!(e.target === this.timerControl)) {
      return;
    }
    if (this.timerControl.textContent.trim() === "play_circle") {
      this.timerControl.textContent = "pause_circle";
      this.workoutTimer.start();
    } else {
      this.timerControl.textContent = "play_circle";
      this.workoutTimer.stop();
    }
  };

  workoutResetTimerHandler = (e) => {
    if (!e.target.classList.contains("timer-reset-control")) {
      return;
    }
    const confirmation = confirm(
      "Are you sure you want to reset the current workout timer?",
    );
    if (confirmation) {
      this.workoutTimer.stop();
      this.timerControl.textContent = "play_circle";
      this.workoutTimer.resetTimer();
    }
  };

  dateHandler() {
    const date = splitDate(this.dateInput.value);
    if (!validateDate(date)) {
      this.dateInput.valueAsDate = getCurrentDate();
      pageManager.showTempPopupMessage(
        "Cannot set day to a future date.",
        2000,
      );
    }
  }

  navigateRoutineWorkoutHandler = (e) => {
    const direction =
      e.target.id === "nav-before" ? "previous_workout/" : "next_workout/";
    FetchUtils.apiFetch({
      url: `${API.BASE_URL}${API.ROUTINE_SETTINGS}${direction}`,
      method: "GET",
      successHandler: this.fetchWorkoutSuccessHandler.bind(this),
    });
  };

  setComplete(e) {
    if (this.showRestTimerSetting === "True" && e.target.checked) {
      this.showRestTimer();
    }
  }

  showRestTimer() {
    this.restTimer.start();
    pageManager.openPopup(
      "rest-timer-popup",
      this.restTimer.stop.bind(this.restTimer),
    );
  }
}

class WorkoutLogManager extends BaseWorkoutManager {
  constructor(saveWorkoutSuccessHandler) {
    super();
    this.saveWorkoutSuccessHandler = saveWorkoutSuccessHandler;
  }
  initialize(pk) {
    super.initialize();
    this.setDate();
    this.dragAndDrop.initialize("-20rem");
    this.pk = pk;
  }

  setDate() {
    const monthAndYear = document.querySelector("#month-name");
    const month = parseInt(monthAndYear.dataset.month) - 1;
    const year = parseInt(monthAndYear.dataset.year);
    const day = parseInt(logManager.currentLog.dataset.day);
    document.getElementById("date").valueAsDate = new Date(year, month, day);
  }
}

class WorkoutSettingsManager extends BaseWorkoutManager {
  initialize() {
    pageManager
      .fetchData({
        url: `${this.baseURL}/settings`,
        method: "GET",
        responseType: "text",
      })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "settings");
        this.saveWorkoutSettingsBtn = document.getElementById(
          "save-workout-settings",
        );
        this.deleteWorkoutBtn = document.getElementById("delete-workout");
        super.initialize();
        this.dragAndDrop.initialize("-20rem");
      });
  }
  addWorkoutListeners() {
    super.addWorkoutListeners();

    this.workoutController.addEventListener("keyup", (e) => {
      if (e.target.dataset.type === "int") {
        this.updateSet(e.target.closest(".set").querySelector(".amount"));
      } else if (e.target.classList.contains("amount")) {
        this.updateSet(e.target);
      }
    });

    this.workoutController.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && e.target.classList.contains("five_rep_max")) {
        this.fiveRepMaxHandler(e);
      }
    });

    this.workoutController.addEventListener("focusout", (e) => {
      if (e.target.classList.contains("amount")) {
        this.updateSet(e.target);
      } else if (e.target.classList.contains("five_rep_max")) {
        this.fiveRepMaxHandler(e);
      }
    });

    this.workoutController.addEventListener("change", (e) => {
      if (e.target.classList.contains("modifier")) {
        this.modifierInputHandler(e);
      }
    });

    this.saveWorkoutSettingsBtn.addEventListener("click", (e) => {
      this.saveWorkoutSettings();
    });

    this.deleteWorkoutBtn.addEventListener("click", (e) => {
      this.deleteWorkout();
    });
  }

  modifierInputHandler(e) {
    const amountInput = e.target.closest(".set").querySelector(".amount");
    this.updateSet(amountInput);
    this.unsavedChanges = true;
  }

  fiveRepMaxHandler = (e) => {
    // Update set calculations for exercise
    const exerciseSets = e.target.closest(".exercise").querySelectorAll(".set");
    exerciseSets.forEach((exerciseSet) => {
      const amountInput = exerciseSet.querySelector(".amount");
      this.updateSet(amountInput);
    });
  };

  updateSet = (element) => {
    // Get inputs to calculate set
    const amount = parseFloat(element.value);
    const setContainer = element.closest(".set");
    const modifier = setContainer.querySelector(".modifier").value;
    const fiveRepMax = parseFloat(
      element.closest(".exercise").querySelector(".five_rep_max").value,
    );
    const reps = element.closest(".set").querySelector("input.reps").value;

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
        if (amount > fiveRepMax) {
          calculateSetContainer.textContent = `0 ${weightUnit} x ${reps}`;
        } else {
          calculateSetContainer.textContent = `${fiveRepMax - amount} ${weightUnit} x ${reps}`;
        }
        break;
    }
  };

  setExerciseSetValues(element, container, values) {
    super.setExerciseSetValues(element, container, values);
    element.querySelector(".amount").value = 0;
  }

  workoutSettingsFormPostprocessHandler(formData) {
    Object.entries(formData).forEach(([key, value]) => {
      formData[key] = value.replace("id_", "");
    });
    return formData;
  }

  saveWorkoutSettings() {
    // Get settings data
    const formData = FormUtils.getFormData("workout_settings", {
      postprocessFunc: this.workoutSettingsFormPostprocessHandler,
    });

    FetchUtils.apiFetch({
      url: `${API.BASE_URL}${API.WORKOUT_SETTINGS}update_settings/`,
      method: "PUT",
      body: formData,
      successHandler: this.saveWorkoutSettingsSuccessHandler,
    });
  }

  saveWorkoutSettingsSuccessHandler = (response) => {
    const successMessage = document.querySelector(".success-message");
    successMessage.classList.remove("hidden");
    setTimeout(() => {
      successMessage.classList.add("hidden");
    }, 3000);
  };

  saveWorkout(successHandler, errorHandler = null) {
    const exercises = this.validateWorkoutForm();
    if (exercises.length === 0) {
      return;
    }

    // Get data from current workout
    const formData = this.readWorkout();
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
      url: `${API.BASE_URL}${API.WORKOUTS}${pk}`,
      method: method,
      body: formData,
      successHandler: (response) => {
        this.saveWorkoutSuccessHandler(response, formData);
      },
      errorHandler: {},
    });
  }

  saveWorkoutSuccessHandler = (response, formData) => {
    super.saveWorkoutSuccessHandler(response);
    this.selectWorkoutSearchBar.addItem(formData["name"], "workout-option", {
      pk: response["id"],
    });
    document.getElementById("workout-pk").value = response["id"];
  };

  readWorkout() {
    // Get workout name, returns null if user didn't confirm
    const workoutName = this.saveWorkoutConfirmation();
    if (workoutName === null || workoutName.trim() === "") {
      return;
    }
    const workoutData = { name: workoutName, exercises: [], config: [] };

    // Iterate form fields and populate FormData
    const exercises = document.querySelectorAll(".exercise");
    exercises.forEach((exercise) => {
      const exerciseName = exercise
        .querySelector(".exercise-name")
        .textContent.trim();
      const fiveRepMax = parseFloat(
        exercise.querySelector("input.five_rep_max").value,
      );
      const exercisePK = exercise.querySelector(".id").value;
      workoutData["exercises"].push(exercisePK);

      const currentExercise = {
        name: exerciseName,
        id: exercisePK,
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
        currentExercise["default_weight"] =
          exercise.querySelector(".default_weight").value;
        currentExercise["default_reps"] =
          exercise.querySelector(".default_reps").value;
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

  deleteWorkout() {
    const name = document.getElementById("workout-name").value;
    const pk = document.getElementById("workout-pk").value;
    const confirmation = confirm(
      `This will permanently delete ${name}, are you sure?`,
    );
    if (confirmation) {
      FetchUtils.apiFetch({
        url: `${API.BASE_URL}${API.WORKOUTS}${pk}`,
        method: "DELETE",
        successHandler: this.deleteWorkoutSuccessHandler,
        errorHandler: this.deleteWorkoutErrorHandler,
      });
    }
  }

  deleteWorkoutSuccessHandler = (response) => {
    console.log(response);
    pageManager.showTempPopupMessage("Workout deleted.");
    this.clearWorkout();
    const workoutName = document.getElementById("workout-name").value;
    this.selectWorkoutSearchBar.deleteItem(workoutName);
    this.selectWorkoutSearchBar.clearInput();
    this.unsavedChanges = false;
  };
  deleteWorkoutErrorHandler = (response) => {
    pageManager.showTempPopupMessage(response["detail"]);
  };

  fetchWorkoutSuccessHandler = (response) => {
    super.fetchWorkoutSuccessHandler(response);
    document.getElementById("workout-name").value = response["workout_name"];
    document.getElementById("workout-pk").value = response["pk"];
  };
}

class Timer {
  constructor(id, options = {}) {
    this.element = document.getElementById(id);
    this.timerRunning = false;
    this.showHours = options.showHours ?? false;
    this.resetOnStop = options.resetOnStop ?? true;
    this.hours = 0;
    this.minutes = 0;
    this.seconds = 0;
  }

  start() {
    // Set timerRunning to true and start recursive loop of updateTimer
    if (!this.timerRunning) {
      this.timerRunning = true;
      this.timerInterval = setInterval(this.updateTimer.bind(this), 1000);
    }
  }

  stop() {
    // Stops the timer and resets it to zero if resetOnStop is true
    if (this.timerRunning) {
      this.timerRunning = false;
      if (this.resetOnStop) {
        this.resetTimer();
      }
      clearInterval(this.timerInterval);
    }
  }

  resetTimer() {
    // Set timer values to 0
    this.hours = 0;
    this.minutes = 0;
    this.seconds = 0;
    this.element.textContent = this.showHours ? "00:00:00" : "00:00";
  }

  updateTimer() {
    // Updates the timer display every second while timerRunning is true
    this.seconds++;
    if (this.seconds === 60) {
      this.seconds = 0;
      this.minutes++;
    }

    if (this.minutes === 60) {
      this.minutes = 0;
      this.hours++;
    }
    this.updateDisplay();
  }

  updateDisplay() {
    // Sets the timer display
    const formattedMinutes =
      this.minutes < 10 ? "0" + this.minutes : this.minutes;
    const formattedSeconds =
      this.seconds < 10 ? "0" + this.seconds : this.seconds;

    if (this.showHours) {
      const formattedHours = this.hours < 10 ? "0" + this.hours : this.hours;
      this.element.textContent = `${formattedHours}:${formattedMinutes}:${formattedSeconds}`;
    } else {
      this.element.textContent = `${formattedMinutes}:${formattedSeconds}`;
    }
  }

  getDurationSeconds() {
    // Returns the total duration of the timer as seconds
    const timeParts = this.element.textContent.trim().split(":");
    if (this.showHours) {
      return timeParts[0] * 3600 + timeParts[1] * 60 + timeParts[2];
    } else {
      return timeParts[0] * 60 + timeParts[1];
    }
  }
}

window.workoutManager = new WorkoutManager();
window.workoutSettingsManager = new WorkoutSettingsManager();
