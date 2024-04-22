class CardioManager {
  constructor() {
    this.baseURL = `${pageManager.baseURL}/cardio`;
    this.collapsible = new Collapsible();
    this.inputSpinner = new InputSpinner();
  }

  initialize() {
    this.collapsible.initialize();
    this.initializeInputSpinners();
    this.initializeCardioEntryHeaders();
    this.addSaveCardioListener();
    pageManager.addBtnGroupToggleListeners(this.btnGroupHandler);
    this.btnGroupHandler();
  }

  initializeCardioEntryHeaders() {
    this.setupDateHeader();
    this.setupDurationHeader();
    this.setupDistanceHeader();
  }

  setupDateHeader() {
    const dateFields = {};
    dateFields["header"] = document.getElementById("date-header");
    dateFields["input"] = document.getElementById("date");
    dateFields["hours"] = document.getElementById("hours");
    dateFields["minutes"] = document.getElementById("minutes");
    dateFields["period"] = document.getElementById("period");

    this.updateDateHeader(dateFields);
    for (const field in dateFields) {
      if (field !== "header") {
        dateFields[field].addEventListener("input", (e) => {
          this.updateDateHeader(dateFields);
        });
      }
    }
  }

  getDateTimeStr(formData) {
    // Reads the date input on the input spinner and converts it to a string for a python datetime object
    const date = this.inputSpinner.spinners["8"].getDateObj();
    let hours = parseInt(formData["hours"]);
    hours = hours > 0 ? hours : hours + 12;

    if (formData["period"] === "AM") {
      hours = hours < 12 ? hours : 0;
    } else {
      hours = hours === 12 ? 12 : hours + 12;
    }

    date.setHours(hours);
    date.setMinutes(formData["minutes"]);
    return this.toISOWithTimezone(date);
  }

  toISOWithTimezone(date) {
    const tzOffset = -date.getTimezoneOffset();
    const diff = tzOffset >= 0 ? "+" : "-";
    const pad = (num) => (num < 10 ? "0" + num : num);

    const offset = Math.abs(tzOffset);
    const hoursOffset = Math.floor(offset / 60);
    const minutesOffset = offset % 60;

    return (
      date.getFullYear() +
      "-" +
      pad(date.getMonth() + 1) +
      "-" +
      pad(date.getDate()) +
      "T" +
      pad(date.getHours()) +
      ":" +
      pad(date.getMinutes()) +
      ":" +
      pad(date.getSeconds()) +
      diff +
      pad(hoursOffset) +
      ":" +
      pad(minutesOffset)
    );
  }

  postprocessCardioSessionForm = (formData) => {
    const datetime = this.getDateTimeStr(formData);
    const distance = `${formData["distance-integer"]}.${formData["distance-decimal"]}`;
    const duration =
      formData["duration-hours"] * 3600 +
      formData["duration-minutes"] * 60 +
      formData["duration-seconds"] * 1;
    return { datetime: datetime, distance: distance, duration: duration };
  };

  saveCardioSession() {
    const formData = FormUtils.getFormData("cardio-session-form", {
      postprocessFunc: this.postprocessCardioSessionForm,
    });

    FetchUtils.apiFetch({
      url: `${pageManager.baseURL}/log/cardio_log/`,
      method: "POST",
      body: formData,
      successHandler: () =>
        pageManager.showTempPopupMessage("Cardio Session Saved.", 2000),
      errorHandler: () =>
        pageManager.showTempPopupMessage(
          "Error Saving Cardio Session. Please Try Again.",
          2000,
        ),
    });
  }

  addSaveCardioListener() {
    const saveCardioSessionBtn = document.getElementById("save-cardio-session");
    saveCardioSessionBtn.addEventListener("click", (e) => {
      e.preventDefault();
      this.saveCardioSession();
    });
  }
  updateDateHeader(date) {
    date["header"].textContent =
      this.inputSpinner.spinners["8"].getDate() +
      ", " +
      date["hours"].value +
      ":" +
      date["minutes"].value +
      date["period"].value;
  }

  setupDurationHeader() {
    const durationHours = document.querySelector(".hours");
    const hoursInput = document.getElementById("dur-hours");
    durationHours.textContent = hoursInput.value;
    hoursInput.addEventListener("input", (e) => {
      durationHours.textContent = hoursInput.value;
    });

    const durationMinutes = document.querySelector(".minutes");
    const minutesInput = document.getElementById("dur-minutes");
    durationMinutes.textContent = minutesInput.value;
    minutesInput.addEventListener("input", (e) => {
      durationMinutes.textContent = minutesInput.value;
    });

    const durationSeconds = document.querySelector(".seconds");
    const secondsInput = document.getElementById("dur-seconds");
    durationSeconds.textContent = secondsInput.value;
    secondsInput.addEventListener("input", (e) => {
      durationSeconds.textContent = secondsInput.value;
    });
  }
  setupDistanceHeader() {
    const distanceInteger = document.getElementById("dist-int");
    const distanceDecimal = document.getElementById("dist-dec");
    const distanceHeader = document.getElementById("distance");
    distanceHeader.textContent =
      distanceInteger.value + "." + distanceDecimal.value;
    distanceInteger.addEventListener("input", (e) => {
      distanceHeader.textContent =
        distanceInteger.value + "." + distanceDecimal.value;
    });
    distanceDecimal.addEventListener("input", (e) => {
      distanceHeader.textContent =
        distanceInteger.value + "." + distanceDecimal.value;
    });
  }

  initializeInputSpinners() {
    this.inputSpinner.timePreset();
    this.inputSpinner.durationPreset(3);
    this.inputSpinner.new({
      id: 6,
      valueRange: [0, 99],
      inputStartValue: 0,
      inputIndex: 1,
    }); // Distance integer
    this.inputSpinner.new({
      id: 7,
      valueRange: [0, 99],
      inputStartValue: 0,
      inputIndex: 1,
      leadingZeroes: [true, 2],
    }); // Distance decimal
    this.inputSpinner.new({
      id: 8,
      type: "date",
      inputIndex: 1,
      noWrap: true,
    });

    const now = new Date();
    if (now.getHours() === 0 && now.getMinutes() < 30) {
      this.inputSpinner.spinners[8].update(-1);
    }
  }

  getSummaries(selectedRange) {
    return pageManager
      .fetchData({
        url: `${this.baseURL}/cardio_log_summaries/${selectedRange}/`,
        method: "GET",
        responseType: "json",
      })
      .then((summaries) => {
        return summaries;
      });
  }

  btnGroupHandler = (e) => {
    const selectedRange = document.querySelector(".active");
    this.updateCardioSummaries(selectedRange.value);
  };

  updateCardioSummaries(selectedRange) {
    this.getSummaries(selectedRange).then((response) => {
      pageManager.updateGraph(response["graph"], "cardio-chart");
      this.updateSummaryContainers(selectedRange, response);
    });
  }

  updateSummaryContainers(selectedRange, response) {
    const containers = document.querySelectorAll(".summary");
    this.updateSummaryHeaders(selectedRange, containers);
    containers.forEach((container, index) => {
      const distance = container.querySelector(".distance");
      distance.textContent = `${response["summaries"][index]["average_distance"]} ${distanceUnit}`;
      const duration = container.querySelector(".duration");
      duration.textContent = response["summaries"][index]["average_duration"];
      const pace = container.querySelector(".pace");
      pace.textContent = response["summaries"][index]["pace"];
      const calories = container.querySelector(".calories");
      calories.textContent = response["summaries"][index]["calories_burned"];
    });
  }

  updateSummaryHeaders(selectedRange, containers) {
    const currentHeader = containers[0].querySelector(".header");
    const previousHeader = containers[1].querySelector(".header");
    const extendedHeader = containers[2].querySelector(".header");

    if (selectedRange === "week") {
      currentHeader.textContent = "Current Day:";
      previousHeader.textContent = "Previous Day:";
      extendedHeader.textContent = "Weekly Summary (Avg. Daily):";
    } else if (selectedRange === "month") {
      currentHeader.textContent = "Current Month:";
      previousHeader.textContent = "Previous Month:";
      extendedHeader.textContent = "6-Month Summary (Avg. Daily):";
    } else if (selectedRange === "year") {
      currentHeader.textContent = "Current Year:";
      previousHeader.textContent = "Previous Year:";
      extendedHeader.textContent = "All-Time Summary (Avg. Daily):";
    }
  }
}

window.cardioManager = new CardioManager();
