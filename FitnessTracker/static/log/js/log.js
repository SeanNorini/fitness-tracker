// noinspection JSUnusedLocalSymbols

class LogManager {
  constructor() {
    this.baseURL = pageManager.baseURL + "/log";
    this.currentLog = null;
    if (document.getElementById("unit_of_measurement").value === "Imperial") {
      this.unitOfMeasurement = "Lbs";
    } else {
      this.unitOfMeasurement = "Kg";
    }
    this.currentYear = new Date().getFullYear();
    this.currentMonth = new Date().getMonth() + 1;
    this.currentDay = new Date().getDate();
  }

  initialize() {
    const navPrev = document.querySelector("#nav_prev");
    // noinspection JSUnusedLocalSymbols
    navPrev.addEventListener("click", (e) => {
      this.getCalendar("prev");
    });

    const navNext = document.querySelector("#nav_next");
    // noinspection JSUnusedLocalSymbols
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
    const monthAndYear = document.querySelector("#month_name");
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
      if (currentCalendarDate.month === 12) {
        currentCalendarDate.month = 1;
        currentCalendarDate.year++;
      }
    }
    return currentCalendarDate;
  }
  getCurrentLogDate() {
    const monthAndYear = document.querySelector("#month_name");
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
        pageManager.updateContent(dailyLogHTML, "log_popup_content");
        pageManager.openPopup("daily_log_popup");
        this.addDailyLogPopupListeners();
      });
  }

  addDailyLogPopupListeners() {
    this.addWeightLogBtnListener();
    this.deleteWeightLogBtnListener();
    this.addWorkoutLogListeners();
  }

  addDeleteWorkoutLogBtnListener(workoutLogElement) {
    const deleteWorkoutLogBtn = workoutLogElement.querySelector(
      ".delete_workout_log",
    );
    deleteWorkoutLogBtn.addEventListener("click", (e) => {
      this.deleteWorkoutLog(e);
    });
  }

  addEditWorkoutLogBtnListener(workoutLogElement) {
    const editWorkoutLogBtn =
      workoutLogElement.querySelector(".edit_workout_log");
    editWorkoutLogBtn.addEventListener("click", (e) => {
      this.openEditWorkoutLogPopup(e);
    });
  }

  openEditWorkoutLogPopup(e) {
    const workoutLog = e.target.parentNode.parentNode;
    const workoutLogPK = workoutLog.querySelector(".workout_log_pk").value;
    const url = `${this.baseURL}/edit_workout_log/${workoutLogPK}`;
    pageManager
      .fetchData({ url: url, method: "GET", responseType: "text" })
      .then((editWorkoutLogHTML) => {
        pageManager.updateContent(editWorkoutLogHTML, "add_log_content");
        pageManager.openPopup("add_log_popup");
        document.getElementById("date").style.pointerEvents = "none";
        this.loadWorkoutLogManager();
        this.addUpdateWorkoutLogBtnListener();
      });
  }
  addUpdateWorkoutLogBtnListener() {
    const updateWorkoutBtn = document.getElementById("save_workout");
    updateWorkoutBtn.textContent = "Update Workout Session";
    updateWorkoutBtn.addEventListener("click", (e) => {
      this.updateWorkoutLog(e);
    });
  }

  updateWorkoutLog(e) {
    const workoutContainer = document.querySelector(".exercises");
    const workoutLogPK =
      workoutContainer.querySelector(".workout_log_pk").value;
    this.workoutLogManager.updateWorkoutLog(workoutLogPK).then((response) => {
      if (response.success) {
        pageManager.currentPopup
          .querySelector(".close_popup_container")
          .click();
        this.updateWorkoutLogInfo(workoutLogPK);
      }
    });
  }

  updateWorkoutLogInfo(updatedWorkoutLogPK) {
    this.getWorkoutLog(updatedWorkoutLogPK).then((updatedWorkoutLog) => {
      const workoutLogs = document.querySelectorAll(".workout");
      workoutLogs.forEach((workoutLog) => {
        const workoutLogPK = workoutLog.querySelector(".workout_log_pk").value;
        if (workoutLogPK === updatedWorkoutLogPK) {
          const workoutLogTemplate = document.createElement("template");

          workoutLogTemplate.innerHTML = updatedWorkoutLog.trim();
          const workoutLogElement = workoutLogTemplate.content.firstChild;
          workoutLog.replaceWith(workoutLogElement);
          this.addDeleteWorkoutLogBtnListener(workoutLogElement);
          this.addEditWorkoutLogBtnListener(workoutLogElement);
          pageManager.addCollapsibleListener(
            workoutLogElement,
            ".workout_name",
            ".workout_info",
          );
        }
      });
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
          ".workout_name",
          ".workout_info",
        );
      });
    }

    this.addAddWorkoutLogBtnListener();
  }

  deleteWorkoutLog(e) {
    const workoutLog = e.target.parentNode.parentNode;
    const workoutLogPK = workoutLog.querySelector(".workout_log_pk").value;
    const csrftoken = document.querySelector(
      "[name=csrfmiddlewaretoken]",
    ).value;

    const formData = new FormData();
    formData.append("csrfmiddlewaretoken", csrftoken);

    const url = `${this.baseURL}/delete_workout_log/${workoutLogPK}`;
    pageManager
      .fetchData({
        url: url,
        method: "POST",
        body: formData,
        responseType: "json",
      })
      .then((response) => {
        if (response.success) {
          workoutLog.remove();
          if (!document.querySelector(".workout")) {
            this.updateLogIcons("exercise", "delete");
            document
              .querySelector(".workout_log_placeholder")
              .classList.remove("hidden");
          }
        } else {
          throw new Error("Failed to save weight log");
        }
      });
  }
  updateWorkoutLogs(workoutLogPK) {
    this.getWorkoutLog(workoutLogPK).then((workoutLogHTML) => {
      const workoutLogsContainer = document.getElementById("workout_log_info");
      workoutLogsContainer.insertAdjacentHTML("beforeend", workoutLogHTML);

      const newWorkoutLog = workoutLogsContainer.lastElementChild;
      this.addEditWorkoutLogBtnListener(newWorkoutLog);
      this.addDeleteWorkoutLogBtnListener(newWorkoutLog);
      pageManager.addCollapsibleListener(
        newWorkoutLog,
        ".workout_name",
        ".workout_info",
      );

      const worklogLogPlaceholder = document.querySelector(
        ".workout_log_placeholder",
      );
      worklogLogPlaceholder.classList.add("hidden");
    });
  }

  getWorkoutLog(workoutLogPK) {
    const url = `${this.baseURL}/get_workout_log/${workoutLogPK}`;
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

  addWeightLogBtnListener() {
    const addWeightLogBtn = document.querySelector(".add_weight_log");
    addWeightLogBtn.addEventListener("click", (e) => {
      const url = `${this.baseURL}/save_weight_log/`;
      pageManager
        .fetchData({ url: url, method: "GET", responseType: "text" })
        .then((addWeightLogHTML) => {
          pageManager.updateContent(addWeightLogHTML, "add_log_content");
          pageManager.openPopup("add_log_popup");
          this.updateWeightLogHeader();
          this.addSaveWeightLogListener();
        });
    });
  }

  deleteWeightLogBtnListener() {
    const deleteWeightLogBtn = document.querySelector(".delete_weight_log");
    deleteWeightLogBtn.addEventListener("click", (e) => {
      this.deleteWeightLog();
    });
  }

  deleteWeightLog() {
    const weightLogPK = document.getElementById("weight_log_pk");
    const csrftoken = document.querySelector(
      "[name=csrfmiddlewaretoken]",
    ).value;

    const formData = new FormData();
    formData.append("csrfmiddlewaretoken", csrftoken);

    const url = `${this.baseURL}/delete_weight_log/${weightLogPK.value}`;
    pageManager
      .fetchData({
        url: url,
        method: "POST",
        body: formData,
        responseType: "json",
      })
      .then((response) => {
        if (response.success) {
          this.updateLogIcons("monitor_weight", "delete");
          this.toggleInfoPlaceholder("weight_log", "on");
          const addWeightLogBtn = document.querySelector(".add_weight_log");
          addWeightLogBtn.textContent = "Add Weight Entry";
        } else {
          throw new Error("Failed to save weight log");
        }
      });
  }

  addAddWorkoutLogBtnListener() {
    const addWorkoutLogButton = document.querySelector(".add_workout_log");
    addWorkoutLogButton.addEventListener("click", (e) => {
      this.openAddWorkoutLogPopup();
    });
  }

  openAddWorkoutLogPopup() {
    const url = `${pageManager.baseURL}/workout`;
    pageManager
      .fetchData({ url: url, method: "GET", responseType: "text" })
      .then((addWorkoutLogHTML) => {
        pageManager.updateContent(addWorkoutLogHTML, "add_log_content");
        pageManager.openPopup("add_log_popup");
        this.loadWorkoutLogManager();
        this.addSaveWorkoutBtnListener();
      });
  }

  loadWorkoutLogManager() {
    const script = pageManager.addScript("/static/workout/js/workout.js");
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
    const dailyLogDate = document.getElementById("log_popup_date").textContent;
    const weightLogHeaderText = document.getElementById(
      "weight_log_header_text",
    );
    weightLogHeaderText.innerHTML = `Weight Log - ` + dailyLogDate;
  }

  addSaveWorkoutBtnListener() {
    const saveWorkoutBtn = document.querySelector("#save_workout");
    saveWorkoutBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      this.saveWorkout();
    });
  }

  saveWorkout() {
    this.workoutLogManager.saveWorkout().then((workoutSaved) => {
      if (workoutSaved.success) {
        pageManager.currentPopup
          .querySelector(".close_popup_container")
          .click();
        this.updateLogIcons("exercise", "add");
        this.updateWorkoutLogs(workoutSaved.pk);
      }
    });
  }

  saveWeightLog() {
    const bodyWeight = document.getElementById("body_weight").value;
    const bodyFat = document.getElementById("body_fat").value;
    const date = document.getElementById("log_popup_date").textContent;
    const csrftoken = document.querySelector(
      "[name=csrfmiddlewaretoken]",
    ).value;

    const formData = new FormData();
    formData.append("body_weight", bodyWeight);
    formData.append("body_fat", bodyFat);
    formData.append("date", date);
    formData.append("csrfmiddlewaretoken", csrftoken);

    const url = `${this.baseURL}/save_weight_log/`;
    pageManager
      .fetchData({
        url: url,
        method: "POST",
        body: formData,
        responseType: "json",
      })
      .then((response) => {
        if (response.success) {
          this.updateWeightLog(bodyWeight, bodyFat, response["pk"]);
          this.updateLogIcons("monitor_weight", "add");
        } else {
          throw new Error("Failed to save weight log");
        }
      });
  }

  updateWeightLog(bodyWeight, bodyFat, pk) {
    const bodyWeightElement = document.querySelector(".body_weight");
    bodyWeightElement.innerHTML = `Body Weight - ${bodyWeight} ${this.unitOfMeasurement}`;

    const bodyFatElement = document.querySelector(".body_fat");
    bodyFatElement.innerHTML = `Body Fat - ${bodyFat}%`;

    const weightLogPK = document.getElementById("weight_log_pk");
    weightLogPK.value = pk;

    this.toggleInfoPlaceholder("weight_log", "off");

    const addWeightLogBtn = document.querySelector(".add_weight_log");
    addWeightLogBtn.textContent = "Edit Weight Entry";
  }

  toggleInfoPlaceholder(infoName, toggleStatus) {
    const infoContainer = document.querySelector(`.${infoName}_info`);
    const placeholderContainer = document.querySelector(
      `.${infoName}_placeholder`,
    );
    const deleteBtn = document.querySelector(`.delete_${infoName}`);
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
  addSaveWeightLogListener() {
    const saveWeightLogButton = document.getElementById("save_weight_log");
    saveWeightLogButton.addEventListener("click", (e) => {
      e.stopPropagation();
      pageManager.currentPopup.querySelector(".close_popup_container").click();
      this.saveWeightLog();
    });
  }

  updateLogIcons(iconName, actionType) {
    const currentIcon = this.currentLog.querySelector(`.${iconName}`);
    if (actionType === "add") {
      if (!currentIcon) {
        this.currentLog.innerHTML +=
          `<div><span class="material-symbols-outlined ${iconName}">` +
          `${iconName}</span></div>`;
      }
    } else {
      currentIcon.parentNode.remove();
    }
  }
}

window.logManager = new LogManager();
