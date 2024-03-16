class SettingsManager {
  constructor() {
    this.baseURL = `${pageManager.baseURL}/user/settings`;
  }
  initialize() {
    pageManager
      .fetchData({ url: this.baseURL, method: "GET", responseType: "text" })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "content");
        this.loadUserSettings();
      });
  }
  btnGroupHandler(e) {
    let scriptLoaded = null;
    console.log(e.target.getAttribute("id"));
    switch (e.target.getAttribute("id")) {
      case "user":
        settingsManager.initialize();
        break;
      case "workouts":
        scriptLoaded = pageManager.addScript("/static/workout/js/workout.js");
        if (scriptLoaded) {
          scriptLoaded.onload = function () {
            workoutSettingsManager.initialize();
          };
        } else {
          workoutSettingsManager.initialize();
        }
        break;
      case "exercises":
        scriptLoaded = pageManager.addScript(
          "/static/users/js/exercise_settings.js",
        );
        if (scriptLoaded) {
          scriptLoaded.onload = function () {
            exerciseSettingsManager.initialize();
          };
        } else {
          exerciseSettingsManager.initialize();
        }
        break;
      case "routine":
        break;
    }
  }

  loadUserSettings() {
    pageManager.addButtonGroupToggleListeners(this.btnGroupHandler);
    this.accountSettingsListeners();
    this.bodyCompositionSettingsListeners();
  }

  addLbsToKgListeners() {
    const measurementRadios = document.querySelectorAll(
      'input[name="unit_of_measurement"]',
    );
    measurementRadios.forEach((radio) => {
      radio.addEventListener("change", (e) => {
        const heightLabel = document.querySelector('label[for="height"]');
        const heightInput = document.querySelector('input[name="height"]');
        const weightLabel = document.querySelector('label[for="weight"]');
        const weightInput = document.querySelector('input[name="weight"]');

        if (e.target.value === "Imperial") {
          heightLabel.textContent = heightLabel.textContent.replace(
            "(cm)",
            "(in.)",
          );
          heightInput.placeholder = "70";
          weightLabel.textContent = weightLabel.textContent.replace(
            "(kg)",
            "(lbs)",
          );
          weightInput.placeholder = "160";
        } else {
          heightLabel.textContent = heightLabel.textContent.replace(
            "(in.)",
            "(cm)",
          );
          heightInput.placeholder = "175";
          weightLabel.textContent = weightLabel.textContent.replace(
            "(lbs)",
            "(kg)",
          );
          weightInput.placeholder = "70";
        }
      });
    });
  }

  readBodyCompositionSettings() {
    const formData = new FormData();
    const formElements = document
      .querySelector("#body_composition_form")
      .querySelectorAll("input");
    formElements.forEach((element) => {
      formData.append(element.name, element.value);
    });

    const gender = document.querySelector("#gender_0");
    if (gender.checked) {
      formData.set("gender", "M");
    } else {
      formData.set("gender", "F");
    }

    const unitOfMeasurement = document.querySelector("#unit_of_measurement_0");
    if (unitOfMeasurement.checked) {
      formData.set("unit_of_measurement", "Imperial");
    } else {
      formData.set("unit_of_measurement", "Metric");
    }

    return formData;
  }

  updateBodyCompositionSettings() {
    const formData = this.readBodyCompositionSettings();
    pageManager
      .fetchData({
        url: `${this.baseURL}/update_body_composition_settings/`,
        method: "POST",
        body: formData,
        responseType: "text",
      })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "body_composition_settings");
        this.bodyCompositionSettingsListeners();
      });
  }
  bodyCompositionSettingsListeners() {
    this.addLbsToKgListeners();
    this.addUpdateBodyCompositionListener();
  }

  addUpdateBodyCompositionListener() {
    const updateBodyCompositionSettings = document.querySelector(
      "#update_body_composition",
    );
    updateBodyCompositionSettings.addEventListener("click", (e) => {
      const formData = this.readBodyCompositionSettings();
      this.updateBodyCompositionSettings(formData);
    });
  }

  addDeleteAccountListener() {
    const deleteAccount = document.querySelector("#delete_account");
    deleteAccount.addEventListener("click", (e) => {
      const confirm = this.getAccountDeleteConfirmation();
      if (confirm) {
        window.location.href = `${pageManager.baseURL}/user/delete_account`;
      }
    });
  }

  getAccountDeleteConfirmation() {
    let confirm;
    do {
      confirm = window.prompt(
        "WARNING! This will permanently delete your account and any " +
          "associated records. Type 'delete' to confirm.",
      );
      if (confirm !== null) {
        confirm = confirm.toLowerCase();
      }
    } while (confirm !== "delete" && confirm !== null);
    return confirm;
  }

  addOpenChangePasswordListener() {
    const changePassword = document.querySelector("#change_password");
    changePassword.addEventListener("click", (e) => {
      this.openChangePassword();
    });
  }

  openChangePassword() {
    pageManager
      .fetchData({
        url: `${pageManager.baseURL}/user/change_password`,
        method: "GET",
        responseType: "text",
      })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "settings");
        this.changePasswordEventListeners();
      });
  }

  readAccountSettings() {
    const formData = new FormData();
    const formElements = document
      .querySelector("#account_settings_form")
      .querySelectorAll("input");
    formElements.forEach((element) => {
      formData.append(element.name, element.value);
    });
    return formData;
  }
  addUpdateAccountSettingsListener() {
    const updateAccountSettings = document.querySelector("#update_settings");
    updateAccountSettings.addEventListener("click", (e) => {
      this.updateAccountSettings();
    });
  }

  updateAccountSettings() {
    const formData = this.readAccountSettings();
    pageManager
      .fetchData({
        url: `${pageManager.baseURL}/user/settings/update_account_settings/`,
        method: "POST",
        body: formData,
        responseType: "text",
      })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "account_settings");
        this.accountSettingsListeners();
      });
  }
  accountSettingsListeners() {
    this.addDeleteAccountListener();
    this.addOpenChangePasswordListener();
    this.addUpdateAccountSettingsListener();
  }

  readChangePasswordForm() {
    const formData = new FormData();
    const formElements = document
      .querySelector("#change_password_form")
      .querySelectorAll("input");
    formElements.forEach((element) => {
      formData.append(element.name, element.value);
    });

    const csrftoken = document.querySelector(
      "[name=csrfmiddlewaretoken]",
    ).value;
    formData.append("csrfmiddlewaretoken", csrftoken);

    return formData;
  }

  changePassword() {
    const formData = this.readChangePasswordForm();
    pageManager
      .fetchData({
        url: `${pageManager.baseURL}/user/change_password/`,
        method: "POST",
        body: formData,
        responseType: "text",
      })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "settings");
        const error = document.querySelector(".errorlist");
        if (error) {
          this.changePasswordEventListeners();
        } else {
          this.addReturnToSettingsListener();
        }
      });
  }
  addChangePasswordListener() {
    const changePassword = document.querySelector("#change_password");
    changePassword.addEventListener("click", (e) => {
      e.preventDefault();
      this.changePassword();
    });
  }
  changePasswordEventListeners() {
    this.addReturnToSettingsListener();
    this.addChangePasswordListener();
  }

  addReturnToSettingsListener() {
    const returnToSettingsLink = document.querySelector("#return_to_settings");
    returnToSettingsLink.addEventListener("click", (e) => {
      e.preventDefault();
      settingsManager.initialize();
    });
  }
}

window.settingsManager = new SettingsManager();
