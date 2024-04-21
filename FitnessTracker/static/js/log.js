class LogManager {
  constructor() {
    this.baseURL = pageManager.baseURL + "/log";
    this.currentLog = null;

    this.currentYear = new Date().getFullYear();
    this.currentMonth = new Date().getMonth() + 1;
    this.currentDay = new Date().getDate();
  }

  initialize() {
    const navPrev = document.querySelector("#nav-prev");
    navPrev.addEventListener("click", (e) => {
      this.getCalendar("prev");
    });

    const navNext = document.querySelector("#nav-next");
    navNext.addEventListener("click", (e) => {
      this.getCalendar("next");
    });

    const days = document.querySelectorAll(".day");
    days.forEach((day) => {
      // Verify that date is on or before current date
      if (this.validDate(day)) {
        // noinspection JSUnusedLocalSymbols
        day.addEventListener("click", (e) => {
          // Set current log to selection and retrieve log
          this.currentLog = day;
          this.getLog();
        });
      } else {
        // For future dates don't add event listeners and remove day class to prevent hover styling
        day.classList.remove("day");
      }
    });
  }

  validDate(day) {
    const calendarDate = this.getCalendarDate();
    return (
      calendarDate.year < this.currentYear ||
      (calendarDate.year === this.currentYear &&
        calendarDate.month < this.currentMonth) ||
      (calendarDate.year === this.currentYear &&
        calendarDate.month === this.currentMonth &&
        day.dataset.day <= this.currentDay)
    );
  }

  getCalendarDate() {
    const monthAndYear = document.querySelector("#month-name");
    let month = parseInt(monthAndYear.dataset.month);
    let year = parseInt(monthAndYear.dataset.year);
    return { year: year, month: month };
  }
  getCalendar(calendarNav) {
    const navDate = this.getCalendarNavDate(calendarNav);
    const url = `${this.baseURL}/${navDate.year}/${navDate.month}/`;
    pageManager
      .fetchData({ url: url, method: "GET", responseType: "text" })
      .then((calendarHTML) => {
        pageManager.updateContent(calendarHTML, "content");
        this.initialize();
      });
  }

  getCalendarNavDate(calendarNav) {
    const currentCalendarDate = this.getCalendarDate();
    if (calendarNav === "prev") {
      currentCalendarDate.month--;
      if (currentCalendarDate.month === 0) {
        currentCalendarDate.month = 12;
        currentCalendarDate.year--;
      }
    } else {
      currentCalendarDate.month++;
      if (currentCalendarDate.month === 13) {
        currentCalendarDate.month = 1;
        currentCalendarDate.year++;
      }
    }
    return currentCalendarDate;
  }
  getCurrentLogDate() {
    const monthAndYear = document.querySelector("#month-name");
    const year = monthAndYear.dataset.year;
    const month = monthAndYear.dataset.month;
    const day = this.currentLog.dataset.day;
    return { year: year, month: month, day: day };
  }

  getLog() {
    // Get info from currently selected log
    const logDate = this.getCurrentLogDate();
    const url = `${this.baseURL}/${logDate.year}/${logDate.month}/${logDate.day}`;

    // Fetch page and open log popup
    pageManager
      .fetchData({ url: url, method: "GET", responseType: "text" })
      .then((dailyLogHTML) => {
        pageManager.updateContent(dailyLogHTML, "log-popup-content");
        pageManager.openPopup("daily-log-popup");
        this.addDailyLogPopupListeners();
      });
  }

  openUpdateWorkoutLogPopup(e) {
    const workoutLog = e.target.closest(".workout");
    this.workoutLogPK = workoutLog.querySelector(".workout-log-pk").value;
    const url = `${this.baseURL}/update_workout_log_template/${this.workoutLogPK}/`;
    pageManager
      .fetchData({ url: url, method: "GET", responseType: "text" })
      .then((updateWorkoutLogHTML) => {
        pageManager.updateContent(updateWorkoutLogHTML, "add-log-content");
        pageManager.openPopup("add-log-popup");
        document.getElementById("date").style.pointerEvents = "none";
        this.loadWorkoutLogManager();
        this.addUpdateWorkoutLogBtnListener();
      });
  }

  addDailyLogPopupListeners() {
    this.addWeightLogBtnListener();
    this.deleteWeightLogBtnListener();
    this.addWorkoutLogListeners();
  }

  addDeleteWorkoutLogBtnListener(workoutLogElement) {
    const deleteWorkoutLogBtn = workoutLogElement.querySelector(
      ".delete-workout-log",
    );
    deleteWorkoutLogBtn.addEventListener("click", (e) => {
      this.deleteWorkoutLog(e);
    });
  }

  addEditWorkoutLogBtnListener(workoutLogElement) {
    const updateWorkoutLogBtn =
      workoutLogElement.querySelector(".edit-workout-log");
    updateWorkoutLogBtn.addEventListener("click", (e) => {
      this.openUpdateWorkoutLogPopup(e);
    });
  }

  addUpdateWorkoutLogBtnListener() {
    const updateWorkoutBtn = document.getElementById("save-workout");
    updateWorkoutBtn.textContent = "Update Workout Log";
    updateWorkoutBtn.addEventListener("click", (e) => {
      this.updateWorkoutLog(e);
    });
  }

  addWorkoutLogListeners() {
    const workoutLogElements = document.querySelectorAll(".workout");
    if (workoutLogElements) {
      workoutLogElements.forEach((workoutLogElement) => {
        this.addDeleteWorkoutLogBtnListener(workoutLogElement);
        this.addEditWorkoutLogBtnListener(workoutLogElement);
        pageManager.addCollapsibleListener(
          workoutLogElement,
          ".workout-name",
          ".workout-info",
        );
      });
    }

    this.addAddWorkoutLogBtnListener();
  }

  updateWorkoutLog(e) {
    this.workoutLogManager.updateWorkoutLog(
      this.workoutLogPK,
      this.updateWorkoutLogSuccessHandler,
    );
  }

  updateWorkoutLogSuccessHandler = (response) => {
    pageManager.currentPopup.querySelector(".close-popup-container").click();
    this.updateWorkoutLogInfo(response);
  };

  updateWorkoutLogInfo(response) {
    this.getWorkoutLog(response["pk"]).then((updatedLog) => {
      const workoutLogs = document.querySelectorAll(".workout");
      workoutLogs.forEach((workoutLog) => {
        const workoutLogPK = workoutLog.querySelector(".workout-log-pk").value;
        if (workoutLogPK === response["pk"]) {
          const workoutLogTemplate = document.createElement("template");

          workoutLogTemplate.innerHTML = updatedLog.trim();
          const workoutLogElement = workoutLogTemplate.content.firstChild;
          workoutLog.replaceWith(workoutLogElement);
          this.addDeleteWorkoutLogBtnListener(workoutLogElement);
          this.addEditWorkoutLogBtnListener(workoutLogElement);
          pageManager.addCollapsibleListener(
            workoutLogElement,
            ".workout-name",
            ".workout-info",
          );
        }
      });
    });
  }

  updateWorkoutLogs(workoutLogPK) {
    this.getWorkoutLog(workoutLogPK).then((workoutLogHTML) => {
      const workoutLogsContainer = document.getElementById("workout-log-info");
      workoutLogsContainer.insertAdjacentHTML("beforeend", workoutLogHTML);

      const newWorkoutLog = workoutLogsContainer.lastElementChild;
      this.addEditWorkoutLogBtnListener(newWorkoutLog);
      this.addDeleteWorkoutLogBtnListener(newWorkoutLog);
      pageManager.addCollapsibleListener(
        newWorkoutLog,
        ".workout-name",
        ".workout-info",
      );

      const worklogLogPlaceholder = document.querySelector(
        ".workout-log-placeholder",
      );
      worklogLogPlaceholder.classList.add("hidden");
    });
  }

  getWorkoutLog(workoutLogPK) {
    const url = `${this.baseURL}/workout_log_template/${workoutLogPK}`;
    return pageManager
      .fetchData({
        url: url,
        method: "GET",
        responseType: "text",
      })
      .then((workoutLogHTML) => {
        return workoutLogHTML;
      });
  }

  deleteWorkoutLog(e) {
    const workoutLog = e.target.closest(".workout");
    const workoutLogPK = workoutLog.querySelector(".workout-log-pk").value;

    FetchUtils.apiFetch({
      url: `${this.baseURL}/workout_log/${workoutLogPK}`,
      method: "DELETE",
      successHandler: (response) => {
        this.deleteWorkoutLogSuccessHandler(workoutLog);
      },
      errorHandler: (response) =>
        pageManager.showTempPopupMessage("Error. Please Try Again.", 2000),
    });
  }

  deleteWorkoutLogSuccessHandler = (workoutLog) => {
    workoutLog.remove();
    if (!document.querySelector(".workout")) {
      this.updateLogIcons("exercise", "delete");
      document
        .querySelector(".workout-log-placeholder")
        .classList.remove("hidden");
    }
  };

  saveWorkout() {
    this.workoutLogManager.saveWorkout(this.saveWorkoutSuccessHandler);
  }

  saveWorkoutSuccessHandler = (response) => {
    pageManager.currentPopup.querySelector(".close-popup-container").click();
    this.updateLogIcons("exercise", "add");
    this.updateWorkoutLogs(response.pk);
  };

  addWeightLogBtnListener() {
    const addWeightLogBtn = document.querySelector(".add-weight-log");
    addWeightLogBtn.addEventListener("click", (e) => {
      const url = `${this.baseURL}/weight_log_template/`;
      pageManager
        .fetchData({ url: url, method: "GET", responseType: "text" })
        .then((addWeightLogHTML) => {
          pageManager.updateContent(addWeightLogHTML, "add-log-content");
          pageManager.openPopup("add-log-popup");
          this.updateWeightLogHeader();
          this.addUpsertWeightLogListener();
        });
    });
  }

  deleteWeightLogBtnListener() {
    const deleteWeightLogBtn = document.querySelector(".delete-weight-log");
    deleteWeightLogBtn.addEventListener("click", (e) => {
      this.deleteWeightLog();
    });
  }

  deleteWeightLogSuccessHandler = (response) => {
    this.updateLogIcons("monitor_weight", "delete");
    this.toggleInfoPlaceholder("weight-log", "on");
    document.getElementById("weight-log-pk").value = "";
    const addWeightLogBtn = document.querySelector(".add-weight-log");
    addWeightLogBtn.textContent = "Add Weight Entry";
  };

  deleteWeightLog(e) {
    const weightLogPK = document.getElementById("weight-log-pk").value;

    FetchUtils.apiFetch({
      url: `${this.baseURL}/weight_log/${weightLogPK}`,
      method: "DELETE",
      successHandler: (response) => {
        this.deleteWeightLogSuccessHandler(response);
      },
      errorHandler: (response) =>
        pageManager.showTempPopupMessage("Error. Please Try Again.", 2000),
    });
  }

  addAddWorkoutLogBtnListener() {
    const addWorkoutLogButton = document.querySelector(".add-workout-log");
    addWorkoutLogButton.addEventListener("click", (e) => {
      this.openAddWorkoutLogPopup();
    });
  }

  openAddWorkoutLogPopup() {
    const url = `${pageManager.baseURL}/workout`;
    pageManager
      .fetchData({ url: url, method: "GET", responseType: "text" })
      .then((addWorkoutLogHTML) => {
        pageManager.updateContent(addWorkoutLogHTML, "add-log-content");
        pageManager.openPopup("add-log-popup");
        this.loadWorkoutLogManager();
        this.addSaveWorkoutBtnListener();
      });
  }

  loadWorkoutLogManager() {
    const script = pageManager.addScript("/static/js/workout.js");
    if (script) {
      script.onload = () => {
        this.workoutLogManager = new WorkoutLogManager();
        this.workoutLogManager.initialize();
      };
    } else {
      if (!this.workoutLogManager) {
        this.workoutLogManager = new WorkoutLogManager();
      }
      this.workoutLogManager.initialize();
    }
  }

  updateWeightLogHeader() {
    const dailyLogDate = document.getElementById("log-popup-date").textContent;
    const weightLogHeaderText = document.getElementById(
      "weight-log-header-text",
    );
    weightLogHeaderText.innerHTML = `Weight Log - ` + dailyLogDate;
  }

  addSaveWorkoutBtnListener() {
    const saveWorkoutBtn = document.querySelector("#save-workout");
    saveWorkoutBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      this.saveWorkout();
    });
  }

  upsertWeightLog() {
    let pk = document.querySelector("#weight-log-pk").value;
    const bodyWeight = document.getElementById("body-weight").value;
    const bodyFat = document.getElementById("body-fat").value;
    const date = document.getElementById("log-popup-date").textContent;

    const formData = {
      body_weight: bodyWeight,
      body_fat: bodyFat,
      date: date,
    };

    let method = "POST";
    if (pk) {
      method = "PUT";
      pk = pk + "/";
    }

    FetchUtils.apiFetch({
      url: `${this.baseURL}/weight_log/${pk}`,
      method: method,
      body: formData,
      successHandler: (response) =>
        this.upsertWeightLogSuccessHandler(response, bodyWeight, bodyFat),
      errorHandler: (response) =>
        pageManager.showTempPopupMessage("Error. Please Try Again", 2000),
    });
  }

  upsertWeightLogSuccessHandler = (response, bodyWeight, bodyFat) => {
    this.updateWeightLog(bodyWeight, bodyFat, response["id"]);
    this.updateLogIcons("monitor_weight", "add");
  };

  updateWeightLog(bodyWeight, bodyFat, pk) {
    const bodyWeightElement = document.querySelector(".body-weight");
    bodyWeightElement.innerHTML = `Body Weight - ${bodyWeight} ${weightUnit}`;

    const bodyFatElement = document.querySelector(".body-fat");
    bodyFatElement.innerHTML = `Body Fat - ${bodyFat}%`;

    const weightLogPK = document.getElementById("weight-log-pk");
    weightLogPK.value = pk;

    this.toggleInfoPlaceholder("weight-log", "off");

    const addWeightLogBtn = document.querySelector(".add-weight-log");
    addWeightLogBtn.textContent = "Edit Weight Entry";
  }

  toggleInfoPlaceholder(infoName, toggleStatus) {
    const infoContainer = document.querySelector(`.${infoName}-info`);
    const placeholderContainer = document.querySelector(
      `.${infoName}-placeholder`,
    );
    const deleteBtn = document.querySelector(`.delete-${infoName}`);
    if (toggleStatus === "on") {
      infoContainer.classList.add("hidden");
      placeholderContainer.classList.remove("hidden");
      deleteBtn.classList.add("hidden");
    } else {
      infoContainer.classList.remove("hidden");
      placeholderContainer.classList.add("hidden");
      deleteBtn.classList.remove("hidden");
    }
  }
  addUpsertWeightLogListener() {
    const saveWeightLogButton = document.getElementById("save-weight-log");
    saveWeightLogButton.addEventListener("click", (e) => {
      e.stopPropagation();
      pageManager.currentPopup.querySelector(".close-popup-container").click();
      this.upsertWeightLog();
    });
  }

  updateLogIcons(iconName, actionType) {
    const currentIcon = this.currentLog.querySelector(`.${iconName}-icon`);
    if (actionType === "add") {
      if (!currentIcon) {
        this.currentLog.innerHTML +=
          `<div><span class="material-symbols-outlined ${iconName}-icon text-xl">` +
          `${iconName}</span></div>`;
      }
    } else {
      currentIcon.parentNode.remove();
    }
  }
}

window.logManager = new LogManager();
