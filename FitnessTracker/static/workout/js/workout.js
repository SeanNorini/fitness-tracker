class WorkoutManager {
  constructor() {
    this.unsavedChanges = false;
    this.restTimerRunning = false;
    this.baseURL = pageManager.baseURL + "/workout";
  }
  addSelectWorkoutListener() {
    // Add listener to select workout menu
    const selectWorkoutMenu = document.getElementById("select_workout");
    selectWorkoutMenu.addEventListener("change", (e) => {
      // Confirm select workout if unsaved changes
      let confirm = true;
      if (this.unsavedChanges) {
        confirm = window.confirm(
          "This will erase the current workout session, are you sure?",
        );
      }

      // Load workout on confirmation else change menu option back to previous workout
      const currentWorkout = selectWorkoutMenu.value;
      if (confirm) {
        this.fetchWorkout(currentWorkout);
        this.unsavedChanges = false;
        this.previousWorkoutSelectValue = currentWorkout;
      } else {
        selectWorkoutMenu.value = this.previousWorkoutSelectValue;
      }
    });
  }

  fetchWorkout(workoutName) {
    fetch(`${this.baseURL}/select_workout/${workoutName}`, {
      method: "GET",
    })
      .then((response) => response.text())
      .then((workoutHTML) => {
        // Add workout to page
        const exerciseContainers = document.querySelector(".exercises");
        exerciseContainers.innerHTML = workoutHTML;

        // Add event listeners to current workout
        this.addWorkoutListeners();

        if (workoutName === "Custom Workout") {
          this.setMessage(
            "Please select a workout or add an exercise to get started.",
          );
        } else {
          this.setMessage(null);
        }
      });
  }

  addWorkoutListeners() {
    const exercises = document.querySelectorAll(".exercise_container");
    exercises.forEach((exercise) => {
      this.addExerciseContainerListeners(exercise);
    });
  }

  addExerciseBtnListener() {
    const addExerciseBtn = document.querySelector(".add_exercise");
    addExerciseBtn.addEventListener("click", (e) => {
      const exerciseName = document.querySelector(".exercise").value;
      const exercisesContainer = document.querySelector(".exercises");

      fetch(`${this.baseURL}/add_exercise/${exerciseName}`, {
        method: "GET",
      })
        .then((response) => response.text())
        .then((exerciseHTML) => {
          // Add new exercise to current workout
          const exerciseTemplate = document.createElement("template");
          exerciseTemplate.innerHTML = exerciseHTML.trim();
          const newExercise = exerciseTemplate.content.firstChild;
          exercisesContainer.appendChild(newExercise);

          // Select new exercise and add listeners
          const exerciseContainer = exercisesContainer.querySelector(
            ".exercise_container:last-child",
          );
          this.addExerciseContainerListeners(exerciseContainer);
        });

      this.setMessage(null);
      this.unsavedChanges = true;
    });
  }

  addExerciseContainerListeners(exerciseContainer) {
    // Add listener to delete button
    exerciseContainer
      .querySelector(".delete_exercise")
      .addEventListener("click", (e) => {
        this.deleteExercise(e);
      });

    // Add listener to add set button
    exerciseContainer
      .querySelector(".add_set")
      .addEventListener("click", (e) => {
        this.addSet(e);
      });

    // Add listener to delete button
    exerciseContainer
      .querySelector(".delete_set")
      .addEventListener("click", (e) => {
        this.deleteSet(e);
      });

    // Add listener to set complete checkboxes
    exerciseContainer
      .querySelectorAll(".set_complete")
      .forEach((setCompleteCheckbox) => {
        setCompleteCheckbox.addEventListener("click", (e) => {
          this.setComplete(e);
        });
      });
  }

  deleteExercise(e) {
    // Remove last exercise in a workout
    e.target.closest(".exercise_container").remove();

    // Display message if no exercises are selected
    if (!document.querySelector(".exercise_container")) {
      this.setMessage(
        "Please select a workout or add an exercise to get started.",
      );
    }
    this.unsavedChanges = true;
  }

  addSet(e) {
    const exerciseName = document.querySelector(".exercise").value;
    fetch(`${this.baseURL}/add_set/${exerciseName}`, { method: "GET" })
      .then((response) => response.text())
      .then((setHTML) => {
        // Add new set to exercise
        const setTemplate = document.createElement("template");
        setTemplate.innerHTML = setHTML.trim();
        const exerciseContainer = e.target.closest(".exercise_container");
        const newSet = setTemplate.content.firstChild;
        exerciseContainer.querySelector(".sets").appendChild(newSet);
        this.updateSetNumber(exerciseContainer);

        this.addSetPostFetch(newSet);

        this.unsavedChanges = true;
      });
  }

  addSetPostFetch(newSet) {
    // Add listener to set checkbox
    const setCompleteCheckbox = newSet.querySelector(".set_complete");
    setCompleteCheckbox.addEventListener("click", (e) => {
      this.setComplete(e);
    });
  }

  deleteSet(e) {
    // Remove last set from an exercise
    const lastSet = e.target
      .closest(".exercise_container")
      .querySelector(".set:last-child");
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
      ".set_number",
    ).innerText = "Set " + exerciseSets.length + ":";
  }

  setMessage(message) {
    // Display message to user when no exercises are selected
    const messageContainer = document.querySelector("#message");
    if (message) {
      messageContainer.innerText = message;
      messageContainer.style.display = "flex";
    } else {
      messageContainer.style.display = "none";
    }
  }

  showPopupMessage(message, duration) {
    // Display popup message
    const popup = document.getElementById("popup");
    popup.textContent = message;
    popup.style.display = "block";

    // Close message after duration
    setTimeout(function () {
      popup.style.display = "none";
    }, duration);
  }

  restTimer() {
    const clockElement = document.getElementById("clock");
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

      clockElement.textContent = formattedMinutes + ":" + formattedSeconds;

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
        clockElement.textContent = "00:00";
      },
      start: () => {
        // Start timer
        this.restTimerRunning = true;
        updateRestTimer();
      },
    };
  }

  showRestTimer() {
    const popup = document.querySelector(".clock_popup");
    popup.style.display = "block";

    pageManager.disablePageExcept(popup);

    const closePopup = document.getElementById("close");
    closePopup.addEventListener("click", (e) => {
      popup.style.display = "none";
      restTimerInstance.stop(); // Stop the timer when closing the popup
      pageManager.enablePage(popup);
    });

    pageManager.addReEnablePageListener(popup, closePopup);

    const restTimerInstance = this.restTimer();
    if (!this.restTimerRunning) {
      restTimerInstance.start(); // Start the timer when showing the popup
    }
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
    const saveWorkoutBtn = document.querySelector("#save_workout");
    saveWorkoutBtn.addEventListener("click", (e) => {
      this.saveWorkout();
    });
  }

  saveWorkout() {
    // Check for workout to save
    const exercises = document.querySelectorAll(".exercise_container");
    if (exercises.length === 0) {
      this.setMessage(
        "You must add at least one exercise before saving a workout session.",
      );
      return;
    }

    // Gather form data
    const workoutFormData = this.readCurrentWorkout(exercises);

    // Send workout data and display response
    fetch(`${this.baseURL}/save_workout_session`, {
      method: "POST",
      body: workoutFormData,
    })
      .then((response) => response.json())
      .then((response) => {
        if (response.success === true) {
          this.showPopupMessage("Workout saved.", 2500);
        } else {
          this.showPopupMessage(
            "Problem saving workout, please try again.",
            2500,
          );
        }
      });
  }

  readCurrentWorkout(exercises) {
    const workoutFormData = new FormData();

    // Add workout name
    const workoutName = document.querySelector(".workout").value;
    workoutFormData.append("workout_name", workoutName);

    // Add exercise sets
    const workoutExercises = [];
    exercises.forEach((exercise) => {
      const weights = [];
      const reps = [];
      const exerciseName = exercise
        .querySelector("#exercise_name")
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

  initialize() {
    this.addSelectWorkoutListener();
    this.addExerciseBtnListener();
    this.setDate();
    this.addSaveWorkoutBtnListener();
    this.previousWorkoutSelectValue =
      document.getElementById("select_workout").value;
  }
}

class WorkoutSettingsManager extends WorkoutManager {
  constructor() {
    super();
    this.baseURL = pageManager.baseURL + "/workout/workout_settings";
    this.newWorkout = false;
  }

  setDate() {
    // Override set date for workout settings
  }

  addExerciseContainerListeners(exerciseContainer) {
    super.addExerciseContainerListeners(exerciseContainer);

    // Add input listeners to each exercise set
    const exerciseSets = exerciseContainer.querySelectorAll(".set");
    exerciseSets.forEach((exerciseSet) => {
      this.addWorkoutSettingsInputListeners(exerciseSet);
    });

    // Add input listener to five rep max
    const fiveRepMaxInput = exerciseContainer.querySelector("input.max_rep");
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
    const roundedFloatInput = exerciseSet.querySelector("input.round_float");
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
      "input.round_integer",
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
      .querySelector("input.round_float");
    const event = new KeyboardEvent("keyup", { key: "Enter" });
    weightInput.dispatchEvent(event);
    this.unsavedChanges = true;
  }

  addSetPostFetch(newSet) {
    this.addWorkoutSettingsInputListeners(newSet);
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
        .closest(".exercise_container")
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
      e.target.closest(".exercise_container").querySelector("input.max_rep")
        .value,
    );
    const reps = e.target.closest(".set").querySelector("input.reps").value;

    // Update set calculation
    const calculateSetContainer = setContainer.querySelector(".calculate_set");
    switch (modifier) {
      case "exact":
        calculateSetContainer.textContent = `${amount} ${this.unitOfMeasurement} x ${reps}`;
        break;
      case "percentage":
        calculateSetContainer.textContent =
          `${(fiveRepMax * (amount / 100)).toFixed(2)} ` +
          `${this.unitOfMeasurement} x ${reps}`;
        break;
      case "increment":
        calculateSetContainer.textContent = `${fiveRepMax + amount} ${this.unitOfMeasurement} x ${reps}`;
        break;
      case "decrement":
        calculateSetContainer.textContent = `${fiveRepMax - amount} ${this.unitOfMeasurement} x ${reps}`;
        break;
    }
  }

  initialize() {
    fetch(`${this.baseURL}`, {
      method: "GET",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .then((response) => response.text())
      .then((contentHTML) => {
        const settingsContent = document.querySelector(".settings");
        settingsContent.innerHTML = contentHTML;

        super.initialize();

        const saveWorkoutSettingsBtn = document.getElementById(
          "save_workout_settings",
        );
        saveWorkoutSettingsBtn.addEventListener("click", (e) => {
          this.saveWorkoutSettings();
        });

        const unitOfMeasurement = document.getElementById(
          "unit_of_measurement",
        ).value;
        if (unitOfMeasurement === "Imperial") {
          this.unitOfMeasurement = "Lbs";
        } else {
          this.unitOfMeasurement = "Kg";
        }
      });
  }

  saveWorkoutSettings() {
    // Get settings data
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

    // Update settings and display response
    fetch(`${this.baseURL}/save_workout_settings/`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((response) => {
        if (response.success === true) {
          const successMessage = document.querySelector(".success_message");
          successMessage.classList.remove("hidden");
          setTimeout(() => {
            successMessage.classList.add("hidden");
          }, 3000);
        }
      });
  }
  saveWorkout() {
    // Get data from current workout
    const workoutData = this.readCurrentWorkout();
    const workoutName = workoutData.get("workout_name");

    // Send workout data and display response
    fetch(`${this.baseURL}/save_workout/`, {
      method: "POST",
      body: workoutData,
    })
      .then((response) => response.json())
      .then((response) => {
        if (response.success) {
          this.showPopupMessage("Workout saved.", 2500);

          // Update workout menu if new workout
          if (this.newWorkout) {
            const selectOption = document.createElement("option");
            selectOption.value = workoutName;
            selectOption.innerText = workoutName;
            const selectWorkoutMenu = document.getElementById("select_workout");
            selectWorkoutMenu.appendChild(selectOption);
            selectWorkoutMenu.value = workoutName;
            this.newWorkout = false;
            this.unsavedChanges = false;
          }
        }
      });
  }

  readCurrentWorkout(exercises) {
    const workoutData = new FormData();
    const csrftoken = document.querySelector(
      "[name=csrfmiddlewaretoken]",
    ).value;
    workoutData.append("csrfmiddlewaretoken", csrftoken);
    const workoutSelect = document.getElementById("select_workout");

    // Get workout name, returns null if user didn't confirm
    const workoutName = this.saveWorkoutConfirmation(workoutSelect);
    if (workoutName === null || workoutName.trim() === "") {
      return;
    }
    workoutData.append("workout_name", workoutName);

    // Iterate form fields and populate FormData
    const workoutExercises = document.querySelectorAll(".exercise_container");
    workoutExercises.forEach((exercise) => {
      const exerciseName = exercise
        .querySelector("#exercise_name")
        .textContent.trim();
      const fiveRepMax = parseFloat(
        exercise.querySelector("input.max_rep").value,
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
    if (workoutName !== "Custom Workout") {
      const confirm = window.confirm(
        `This will save new settings to workout "${workoutName}." Are you sure?`,
      );
      if (!confirm) {
        workoutName = window.prompt(
          `Please enter a name for the new workout or close this window to cancel.`,
        );
        this.newWorkout = true;
      }
    } else {
      workoutName = window.prompt(
        `Please enter a name for the new workout or close this window to cancel.`,
      );
      this.newWorkout = true;
    }
    return workoutName;
  }
}

const workoutManager = new WorkoutManager();
const workoutSettingsManager = new WorkoutSettingsManager();
