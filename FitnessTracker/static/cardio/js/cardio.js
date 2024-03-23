class CardioManager {
  constructor() {
    this.baseURL = `${pageManager.baseURL}/cardio`;
    this.collapsible = new Collapsible();
    this.inputSpinner = new InputSpinner();
  }

  initialize() {
    pageManager
      .fetchData({
        url: `${this.baseURL}`,
        method: "GET",
        responseType: "text",
      })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "content");
        this.collapsible.initialize();
        this.initializeInputSpinners();
        this.initializeCardioEntryHeaders();
        this.addSaveCardioListener();
      });
  }

  initializeCardioEntryHeaders() {
    this.setupDateHeader();
    this.setupDurationHeader();
    this.setupDistanceHeader();
  }

  setupDateHeader() {
    const dateFields = {};
    dateFields["header"] = document.getElementById("date");
    dateFields["input"] = document.getElementById("selected_date");
    dateFields["hours"] = document.getElementById("date_hours");
    dateFields["minutes"] = document.getElementById("date_minutes");
    dateFields["period"] = document.getElementById("date_am_pm");

    this.updateDateHeader(dateFields);
    for (const field in dateFields) {
      if (field !== "header") {
        dateFields[field].addEventListener("input", (e) => {
          this.updateDateHeader(dateFields);
        });
      }
    }
  }

  readCardioSessionForm() {
    const formData = new FormData();

    const formInputs = document.querySelectorAll("input");
    formInputs.forEach((input) => {
      if (!input.readOnly && input.name !== "selected_date") {
        formData.append(input.name, input.value);
      }
    });
    formData.append("date", this.inputSpinner.spinners[8].getPythonDate());

    return formData;
  }

  saveCardioSession() {
    const formData = this.readCardioSessionForm();

    pageManager
      .fetchData({
        url: `${this.baseURL}/save_cardio_session/`,
        method: "POST",
        body: formData,
        responseType: "json",
      })
      .then((response) => {
        if (response.success) {
          pageManager.showTempPopupMessage("Cardio Session Saved.", 2000);
        } else {
          pageManager.showTempPopupMessage(
            "Error Saving Cardio Session. Please Try Again.",
            2000,
          );
        }
      })
      .catch(() => {
        pageManager.showTempPopupMessage(
          "Error Saving Cardio Session. Please Try Again.",
          2000,
        );
      });
  }

  addSaveCardioListener() {
    const saveCardioSessionBtn = document.getElementById("save_cardio_session");
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
    const hoursInput = document.getElementById("dur_hours");
    durationHours.textContent = hoursInput.value;
    hoursInput.addEventListener("input", (e) => {
      durationHours.textContent = hoursInput.value;
    });

    const durationMinutes = document.querySelector(".minutes");
    const minutesInput = document.getElementById("dur_minutes");
    durationMinutes.textContent = minutesInput.value;
    minutesInput.addEventListener("input", (e) => {
      durationMinutes.textContent = minutesInput.value;
    });

    const durationSeconds = document.querySelector(".seconds");
    const secondsInput = document.getElementById("dur_seconds");
    durationSeconds.textContent = secondsInput.value;
    secondsInput.addEventListener("input", (e) => {
      durationSeconds.textContent = secondsInput.value;
    });
  }
  setupDistanceHeader() {
    const distanceInteger = document.getElementById("dist_int");
    const distanceDecimal = document.getElementById("dist_dec");
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
  }
}

window.cardioManager = new CardioManager();
