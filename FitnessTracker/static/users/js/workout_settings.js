class WorkoutSettingsManager extends WorkoutManager {
  constructor() {
    super();
    this.url = `http://${domain}/workout/workout_settings`;
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
        calculateSetContainer.textContent = `${(fiveRepMax * (amount / 100)).toFixed(2)} ${this.unitOfMeasurement} x ${reps}`;
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
    fetch(`http://${domain}/workout/workout_settings`, {
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
    fetch(`${this.url}/save_workout_settings/`, {
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
    fetch(`${this.url}/save_workout/`, {
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
workoutSettingsManager = new WorkoutSettingsManager();
