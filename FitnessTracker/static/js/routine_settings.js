class RoutineSettingsManager {
  constructor() {
    this.baseURL = pageManager.baseURL + "/workout/routine_settings";
    this.routineData = {
      weeks: [],
      name: "",
    };
  }
  initialize() {
    pageManager
      .fetchData({
        url: this.baseURL,
        method: "GET",
        responseType: "text",
      })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "settings");
        this.currentWeek = document.getElementById("current-week");
        this.currentRoutine = document.getElementById("current-routine");
        this.popup = document.getElementById("workout-popup");
        this.addListeners();
        this.activeRoutineSearchBar = new SearchBar_(
          this.activeRoutineSearchHandler.bind(this),
        );
        this.activeRoutineSearchBar.initialize("active-routine-search-bar");

        this.editRoutineSearchBar = new SearchBar_(
          this.editRoutineSearchHandler.bind(this),
        );
        this.editRoutineSearchBar.initialize("edit-routine-search-bar");

        this.activeWorkoutSearchBar = new SearchBar_(
          this.activeWorkoutSearchHandler.bind(this),
        );
        this.activeWorkoutSearchBar.initialize("active-workout-search-bar");
      });
  }

  activeWorkoutSearchHandler = (e) => {
    if (e.target.classList.contains("workout")) {
      this.activeWorkoutSearchBar.searchInput.placeholder =
        e.target.textContent.trim();
      this.activeWorkoutSearchBar.closeSearchList();

      const activeWorkout = {
        week_number: parseInt(e.target.dataset.week),
        day_number: parseInt(e.target.dataset.day),
        workout_index: parseInt(e.target.dataset.index),
      };

      this.updateActiveWorkout(activeWorkout);
    }
  };

  updateActiveWorkout = (activeWorkout = null) => {
    if (!activeWorkout) {
      activeWorkout = activeWorkout = {
        week_number: 1,
        day_number: 1,
        workout_index: 0,
      };
    }
    pageManager
      .fetchData({
        url: `${this.baseURL}/update_routine_settings/`,
        method: "PATCH",
        responseType: "json",
        body: JSON.stringify(activeWorkout),
        headers: { "Content-Type": "application/json" },
      })
      .then((response) => {
        pageManager.showTempPopupMessage("Active Workout Updated.", 2000);
      });
  };

  editRoutineSearchHandler = (e) => {
    if (e.target.classList.contains("routine")) {
      const routinePK = e.target.dataset.pk;

      pageManager
        .fetchData({
          url: `${pageManager.baseURL}/workout/get_routine/${routinePK}`,
          method: "GET",
          responseType: "json",
        })
        .then((response) => {
          this.routineData = response;
          this.currentWeek.textContent = "Week #1";
          this.currentRoutine.textContent = this.routineData["name"];
          this.updateWeek(1);
          this.editRoutineSearchBar.closeSearchList();
          this.activeWorkoutSearchHandler(e);
        });
    }
  };

  activeRoutineSearchHandler = (e) => {
    if (e.target.classList.contains("routine")) {
      const routinePK = e.target.dataset.pk;

      pageManager
        .fetchData({
          url: `${this.baseURL}/update_routine_settings/`,
          method: "PATCH",
          responseType: "json",
          body: JSON.stringify({
            routine: routinePK,
            week_number: 1,
            day_number: 1,
            workout_index: 0,
          }),
          headers: { "Content-Type": "application/json" },
        })
        .then((response) => {
          this.activeRoutineSearchBar.searchInput.placeholder =
            e.target.textContent.trim();
          this.activeRoutineSearchBar.closeSearchList();
          this.updateActiveWorkoutSearchList();
        });
    }
  };

  updateActiveWorkoutSearchList() {
    pageManager
      .fetchData({
        url: `${this.baseURL}/get_active_workout_search_list/`,
        method: "GET",
        responseType: "text",
      })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "active-search-list");
        this.activeWorkoutSearchBar.initialize("active-workout-search-bar");
      });
  }

  addListeners() {
    const weekContainer = document.getElementById("week");
    weekContainer.addEventListener("click", this.onClickHandler);

    const navPrev = document.getElementById("nav-prev");
    navPrev.addEventListener("click", this.weekNavigationHandler);

    const navNext = document.getElementById("nav-next");
    navNext.addEventListener("click", this.weekNavigationHandler);

    const saveBtn = document.getElementById("save-routine");
    saveBtn.addEventListener("click", this.saveRoutine);
  }

  getWeek() {
    return parseInt(this.currentWeek.textContent.match(/\d+/)[0]);
  }

  onClickHandler = (e) => {
    if (e.target.classList.contains("add-workout")) {
      this.openAddWorkoutPopup(e);
    } else if (e.target.classList.contains("delete-workout")) {
      this.day = e.target.closest(".day");
      this.deleteWorkout(e);
    }
  };

  deleteWorkout = (e) => {
    const workouts = this.day.querySelectorAll(".workout");
    if (workouts.length === 1) {
      this.addWorkout("Rest Day");
    } else {
      e.target.closest(".workout-container").remove();
    }
  };

  weekNavigationHandler = (e) => {
    const currentWeek = this.getWeek();
    const direction = e.target.id;

    if (this.canNavigate(direction, currentWeek)) {
      const newWeek = this.getNewWeek(direction, currentWeek);
      this.updateWeek(newWeek);
    }
  };

  canNavigate(direction, currentWeek) {
    if (direction === "nav-prev" && currentWeek === 1) {
      pageManager.showTempPopupMessage("Already At First Week", 2000);
      return false;
    }
    if (direction === "nav-next" && this.isWeekEmpty()) {
      pageManager.showTempPopupMessage(
        "Week Must Have At Least 1 Workout",
        2500,
      );
      return false;
    }
    return true;
  }

  isWeekEmpty() {
    let weekEmpty = true;
    const weekdays = document.querySelectorAll(".day");

    for (let i = 0; i < weekdays.length - 1; i++) {
      const workout = weekdays[i].querySelector(".workout").textContent.trim();
      if (!(workout === "Rest Day")) {
        weekEmpty = false;
        break;
      }
    }
    return weekEmpty;
  }

  saveCurrentWeek(currentWeek) {
    if (this.routineData["weeks"][currentWeek - 1]) {
      this.routineData["weeks"][currentWeek - 1] = {
        week_number: currentWeek,
        days: [],
      };
    } else {
      this.routineData["weeks"].push({ week_number: currentWeek, days: [] });
    }

    // Iterate over week and append new workout data for each day of the week
    const week = document.querySelectorAll(".day");
    week.forEach((weekday, index) => {
      this.routineData["weeks"][currentWeek - 1]["days"].push(
        this.getWorkouts(weekday, index + 1),
      );
    });
  }

  getWorkouts(weekday, index) {
    // Get workouts for weekday and return dictionary with list of workouts
    const currentDayWorkouts = { day_number: index, workouts: [] };
    const workouts = weekday.querySelectorAll(".workout");
    workouts.forEach((workout) => {
      currentDayWorkouts["workouts"].push(workout.textContent.trim());
    });

    return currentDayWorkouts;
  }

  getNewWeek(direction, currentWeek) {
    if (direction) {
      const newWeek =
        direction === "nav-prev" ? currentWeek - 1 : currentWeek + 1;
      this.currentWeek.textContent = `Week #${newWeek}`;
      return newWeek;
    }
    return currentWeek;
  }
  updateWeek(newWeek) {
    const week = document.querySelectorAll(".day");
    for (let i = 0; i < 7; i++) {
      this.day = week[i];
      this.day.querySelector(".workouts").innerHTML = "";

      if (this.routineData["weeks"][newWeek - 1]) {
        this.routineData["weeks"][newWeek - 1]["days"][i]["workouts"].forEach(
          (workout) => {
            this.addWorkout(workout);
          },
        );
      } else {
        this.addWorkout("Rest Day");
      }
    }
  }

  openAddWorkoutPopup(e) {
    this.day = e.target.closest(".day");
    pageManager.openPopup("workout-popup", this.popupCleanupCallback);
    this.popup.addEventListener("click", this.addWorkoutHandler);
  }

  addWorkoutHandler = (e) => {
    if (
      e.target.classList.contains("workout") &&
      this.popup.contains(e.target)
    ) {
      const workout = this.day.querySelector(".workout");

      const workoutName = e.target.textContent.trim();
      const closePopup = true;
      this.addWorkout(workoutName, closePopup);

      if (workout.textContent.trim() === "Rest Day") {
        const container = workout.closest(".workout-container");
        container.remove();
      }
    }
    this.saveCurrentWeek(this.getWeek());
  };

  popupCleanupCallback = () => {
    this.popup.removeEventListener("click", this.addWorkoutHandler);
  };

  addWorkout(workoutName, closePopup = false) {
    const row = this.createWorkoutRow(workoutName);
    const parent = this.day.querySelector(".workouts");

    if (workoutName === "Rest Day") {
      parent.innerHTML = "";
    }

    parent.appendChild(row);

    if (closePopup) {
      document.querySelector(".close-popup-container").click();
    }
  }

  createWorkoutRow(workoutName) {
    // Create container for row
    const row = document.createElement("div");
    row.classList.add(
      "workout-container",
      "row",
      "row-center",
      "full-width",
      "gap-md",
    );

    // Create div for workout
    const workoutDiv = document.createElement("div");
    workoutDiv.classList.add("row", "row-center", "full-width", "gap-md");

    if (workoutName === "Rest Day") {
      workoutDiv.innerHTML = `<div class="workout">${workoutName}</div>`;
    } else {
      workoutDiv.innerHTML = `<div class="workout">${workoutName}</div><div><span class="material-symbols-outlined delete-workout hover-red text-xxl">
            delete
          </span></div>`;
    }

    row.appendChild(workoutDiv);

    return row;
  }

  routineExists(routineName) {
    if (!routineName) {
      return false;
    }

    const routineOptions = document
      .getElementById("active-routine-search-bar")
      .querySelectorAll(".routine");

    for (let i = 0; i < routineOptions.length; i++) {
      if (
        routineOptions[i].textContent.trim().toLowerCase() ===
        routineName.toLowerCase()
      ) {
        return true;
      }
    }

    return false;
  }

  updateRoutineOptions(routineName, pk) {
    if (this.routineExists(routineName)) {
      return;
    }
    const routineOptions = document
      .getElementById("active-routine-search-bar")
      .querySelector(".search-list");
    const newOption = document.createElement("div");
    newOption.dataset.pk = pk;
    newOption.textContent = routineName;
    newOption.classList.add("row", "row-center", "hover", "border", "routine");
    routineOptions.appendChild(newOption);
  }

  saveRoutine = (e) => {
    if (this.routineData["weeks"].length === 0) {
      pageManager.showTempPopupMessage(
        "Routine Must Have At Least 1 Workout.",
        2000,
      );
      return;
    }

    this.routineData["name"] = prompt("Please Enter Routine Name:");
    const routineExists = this.routineExists(this.routineData["name"]);

    let confirmation = true;
    if (routineExists && this.routineData["name"]) {
      confirmation = confirm(
        `This will overwrite the existing ${this.routineData["name"]} routine. Are you sure?`,
      );
    }

    if (!confirmation || !this.routineData["name"]) {
      pageManager.showTempPopupMessage("Routine Not Saved.", 2000);
      return;
    }

    pageManager
      .fetchData({
        url: `${this.baseURL}/save_routine/`,
        method: "POST",
        responseType: "json",
        body: JSON.stringify(this.routineData),
        headers: { "Content-Type": "application/json" },
      })
      .then((response) => {
        if (!routineExists) {
          this.updateRoutineOptions(this.routineData["name"], response["pk"]);
        }
        pageManager.showTempPopupMessage("Routine Saved.", 2000);
      });
  };
}

window.routineSettingsManager = new RoutineSettingsManager();
