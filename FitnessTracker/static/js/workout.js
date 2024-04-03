class WorkoutManager {
  constructor() {
    this.unsavedChanges = false;
    this.restTimerRunning = false;
    this.baseURL = pageManager.baseURL + "/workout";
    this.dragAndDrop = new DragAndDrop();
  }

  initialize() {
    this.addSelectWorkoutListener();
    this.addExerciseBtnListener();
    this.setDate();
    this.addSaveWorkoutBtnListener();
    this.previousWorkoutSelectValue =
      document.getElementById("select-workout").value;

    this.showRestTimerSetting =
      document.getElementById("show-rest-timer").value;
    this.showWorkoutTimerSetting =
      document.getElementById("show-workout-timer").value;

    this.dragAndDrop.initialize();
  }

  addSelectWorkoutListener() {
    // Add listener to select workout menu
    const selectWorkoutMenu = document.getElementById("select-workout");
    selectWorkoutMenu.addEventListener("change", (e) => {
      this.selectWorkout(selectWorkoutMenu);
    });
  }

  getSelectWorkoutConfirmation() {
    let confirm = true;
    if (this.unsavedChanges) {
      confirm = window.confirm(
        "This will erase the current workout session, are you sure?",
      );
    }
    return confirm;
  }

  selectWorkout(selectWorkoutMenu) {
    // Load workout on confirmation else change menu option back to previous workout
    if (this.getSelectWorkoutConfirmation()) {
      this.fetchWorkout(selectWorkoutMenu.value);
      this.unsavedChanges = false;
      this.previousWorkoutSelectValue = selectWorkoutMenu.value;
    } else {
      selectWorkoutMenu.value = this.previousWorkoutSelectValue;
    }
  }

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
  }

  fetchExercise() {
    const exerciseName = document.getElementById("select-exercise").value;

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

  addExerciseBtnListener() {
    const addExerciseBtn = document.getElementById("add-exercise");
    addExerciseBtn.addEventListener("click", (e) => {
      this.fetchExercise();
      this.unsavedChanges = true;
    });
  }

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
        this.addSetCompleteListener(newExerciseSetElement);
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
    const restTimerElement = document.getElementById("rest-timer");
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
      this.saveWorkout();
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

  saveWorkout() {
    // Verify form has exercises to save
    const exercises = this.validateWorkoutForm();
    // Gather form data
    const formData = this.readCurrentWorkout(exercises);

    if (exercises.length === 0) {
      return Promise.resolve({ formEmpty: true });
    }

    // Send workout data and display response
    const url = `${this.baseURL}/save_workout_session`;
    return pageManager
      .fetchData({
        url: url,
        method: "POST",
        responseType: "json",
        body: formData,
      })
      .then((workoutSaved) => {
        if (workoutSaved.formEmpty) {
          return;
        }

        if (workoutSaved) {
          pageManager.showTempPopupMessage("Workout saved.", 2500);
          return { success: true, pk: workoutSaved.pk };
        } else if (!workoutSaved.formEmpty) {
          pageManager.showTempPopupMessage(
            "Problem saving workout, please try again.",
            2500,
          );
        }
      });
  }

  readCurrentWorkout(exercises) {
    const workoutFormData = new FormData();

    // Add workout name
    const workoutName = document.getElementById("select-workout").value;
    workoutFormData.append("workout_name", workoutName);

    // Add exercise sets
    const workoutExercises = [];
    exercises.forEach((exercise) => {
      const weights = [];
      const reps = [];
      const exerciseName = exercise
        .querySelector(".exercise-name")
        .textContent.trim();

      const exerciseSets = exercise.querySelectorAll(".set");
      exerciseSets.forEach((exerciseSet) => {
        let setWeight = exerciseSet.querySelector(".weight").value;
        if (setWeight === "") {
          setWeight = 0;
        }
        weights.push(setWeight);

        let setReps = exerciseSet.querySelector(".reps").value;
        if (setReps === "") {
          setReps = 0;
        }
        reps.push(setReps);
      });
      let currentExercise = {};
      currentExercise[exerciseName] = { weight: weights, reps: reps };
      workoutExercises.push(currentExercise);
    });
    workoutFormData.append("exercises", JSON.stringify(workoutExercises));

    // Add total time
    workoutFormData.append("total_time", "0");

    // Add date
    const dateInput = document.getElementById("date");
    workoutFormData.append("date", dateInput.value);

    // Add CSRF token
    const csrftoken = document.querySelector(
      "[name=csrfmiddlewaretoken]",
    ).value;
    workoutFormData.append("csrfmiddlewaretoken", csrftoken);

    return workoutFormData;
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
      if (
        roundedFloatInput.value &&
        !isNaN(parseFloat(roundedFloatInput.value))
      ) {
        const roundedValue =
          Math.round(parseFloat(roundedFloatInput.value) * 4) / 4;
        roundedFloatInput.value = roundedValue.toFixed(2);
      }
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
      if (
        roundedIntegerInput.value &&
        !isNaN(parseFloat(roundedIntegerInput.value))
      ) {
        const roundedValue =
          Math.round(parseFloat(roundedIntegerInput.value) * 4) / 4;
        roundedIntegerInput.value = roundedValue.toFixed(0);
      }
      this.triggerUpdateSet(e);
    });
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
    inputFiveRepMax.addEventListener("keyup", (e) => {
      // Round five rep max to nearest .25
      if (inputFiveRepMax.value && !isNaN(parseFloat(inputFiveRepMax.value))) {
        const roundedValue =
          Math.round(parseFloat(inputFiveRepMax.value) * 4) / 4;
        inputFiveRepMax.value = roundedValue.toFixed(2);
      }

      // Update set calculations for exercise
      const exerciseSets = inputFiveRepMax
        .closest(".exercise-container")
        .querySelectorAll(".set");
      exerciseSets.forEach((exerciseSet) => {
        const amountInput = exerciseSet.querySelector(".amount");
        const event = new KeyboardEvent("keyup", { key: "Enter" });
        amountInput.dispatchEvent(event);
      });
    });
  }

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
          `${(fiveRepMax * (amount / 100)).toFixed(2)} ` +
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
        this.previousWorkoutSelectValue =
          document.getElementById("select-workout").value;
        this.dragAndDrop.initialize();
      });
  }

  addWorkoutContainerListeners() {
    this.addSelectWorkoutListener();
    this.addExerciseBtnListener();
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
    const csrftoken = document.querySelector(
      "[name=csrfmiddlewaretoken]",
    ).value;

    // Append data to form
    formData.append("csrfmiddlewaretoken", csrftoken);
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
  saveWorkout() {
    // Get data from current workout
    const formData = this.readCurrentWorkout();
    const workoutName = formData.get("workout_name");

    // Send workout data and display response
    pageManager
      .fetchData({
        url: `${this.baseURL}/save_workout/`,
        method: "POST",
        body: formData,
        responseType: "json",
      })
      .then((response) => {
        if (response.success) {
          pageManager.showTempPopupMessage("Workout saved.", 2500);
          if (this.newWorkout) {
            this.updateWorkoutList(workoutName);
          }
        }
      });
  }

  updateWorkoutList(workoutName) {
    const selectOption = document.createElement("option");
    selectOption.value = workoutName;
    selectOption.innerText = workoutName;
    const selectWorkoutMenu = document.getElementById("select-workout");
    selectWorkoutMenu.appendChild(selectOption);
    selectWorkoutMenu.value = workoutName;
    this.newWorkout = false;
    this.unsavedChanges = false;
  }

  readCurrentWorkout(exercises) {
    const workoutData = new FormData();
    const csrftoken = document.querySelector(
      "[name=csrfmiddlewaretoken]",
    ).value;
    workoutData.append("csrfmiddlewaretoken", csrftoken);
    const workoutSelect = document.getElementById("select-workout");

    // Get workout name, returns null if user didn't confirm
    const workoutName = this.saveWorkoutConfirmation(workoutSelect);
    if (workoutName === null || workoutName.trim() === "") {
      return;
    }
    workoutData.append("workout_name", workoutName);

    // Iterate form fields and populate FormData
    const workoutExercises = document.querySelectorAll(".exercise");
    workoutExercises.forEach((exercise) => {
      const exerciseName = exercise
        .querySelector(".exercise-name")
        .textContent.trim();
      const fiveRepMax = parseFloat(
        exercise.querySelector("input.max-rep").value,
      );
      const currentExercise = {
        name: exerciseName,
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

      workoutData.append("exercises", JSON.stringify(currentExercise));
    });
    return workoutData;
  }

  saveWorkoutConfirmation(workoutSelect) {
    let workoutName = workoutSelect.value.trim();
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
      this.newWorkout = true;
    }

    return workoutName;
  }
}

class WorkoutLogManager extends WorkoutManager {
  initialize() {
    this.addSelectWorkoutListener();
    this.addExerciseBtnListener();
    this.addWorkoutListeners();
    this.setDate();
    this.previousWorkoutSelectValue =
      document.getElementById("select-workout").value;
    this.dragAndDrop.initialize("-20rem");
  }

  setDate() {
    const monthAndYear = document.querySelector("#month-name");
    const month = parseInt(monthAndYear.dataset.month) - 1;
    const year = parseInt(monthAndYear.dataset.year);
    const day = parseInt(logManager.currentLog.dataset.day);
    document.getElementById("date").valueAsDate = new Date(year, month, day);
  }

  updateWorkoutLog(workoutLogPK) {
    // Verify form has exercises to save
    const exercises = this.validateWorkoutForm();

    // Gather form data
    const formData = this.readCurrentWorkout(exercises);

    formData.append("pk", document.querySelector(".workout-log-pk").value);

    if (exercises.length === 0) {
      return Promise.resolve({ formEmpty: true });
    }

    // Send workout data and display response
    const url = `${pageManager.baseURL}/log/update_workout_log/${workoutLogPK}/`;
    return pageManager
      .fetchData({
        url: url,
        method: "POST",
        responseType: "json",
        body: formData,
      })
      .then((response) => {
        return response;
      });
  }
}

window.workoutManager = new WorkoutManager();
window.workoutSettingsManager = new WorkoutSettingsManager();
