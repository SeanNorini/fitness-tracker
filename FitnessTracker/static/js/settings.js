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
    switch (e.target.getAttribute("id")) {
      case "user":
        settingsManager.initialize();
        break;
      case "workouts":
        scriptLoaded = pageManager.addScript("/static/js/workout.js");
        if (scriptLoaded) {
          scriptLoaded.onload = function () {
            workoutSettingsManager.initialize();
          };
        } else {
          workoutSettingsManager.initialize();
        }
        break;
      case "exercises":
        scriptLoaded = pageManager.addScript("/static/js/exercise_settings.js");
        if (scriptLoaded) {
          scriptLoaded.onload = function () {
            exerciseSettingsManager.initialize();
          };
        } else {
          exerciseSettingsManager.initialize();
        }
        break;
      case "routine":
        pageManager.loadModuleScript(
          "/static/js/routine_settings.js",
          "routineSettingsManager",
        );
        break;
    }
  }

  loadUserSettings() {
    pageManager.addBtnGroupToggleListeners(this.btnGroupHandler);
    this.accountSettingsListeners();
    this.userSettingsListeners();
  }

  addLbsToKgListeners() {
    const measurementRadios = document.querySelectorAll(
      'input[name="system_of_measurement"]',
    );
    measurementRadios.forEach((radio) => {
      radio.addEventListener("change", (e) => {
        const heightLabel = document.querySelector('label[for="height"]');
        const heightInput = document.querySelector('input[name="height"]');
        const weightLabel = document.querySelector('label[for="body_weight"]');
        const weightInput = document.querySelector('input[name="body_weight"]');

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

  updateUserSettings() {
    const formData = FormUtils.getFormData("user-settings-form");
    FetchUtils.apiFetch({
      url: `${this.baseURL}/user_settings/`,
      method: "PATCH",
      body: formData,
      successHandler: (response) => {
        pageManager.showTempPopupMessage("User Settings Updated", 2000);
      },
      errorHandler: FormUtils.formErrorHandler,
    });
  }

  userSettingsListeners() {
    this.addLbsToKgListeners();
    this.addUpdateUserSettingsListener();
  }

  addUpdateUserSettingsListener() {
    const updateUserSettings = document.querySelector("#update-user-settings");
    updateUserSettings.addEventListener("click", (e) => {
      this.updateUserSettings();
    });
  }

  addDeleteAccountListener() {
    const deleteAccount = document.querySelector("#delete-account");
    deleteAccount.addEventListener("click", (e) => {
      const confirmation = window.prompt(
        "WARNING! This will permanently delete your account and any " +
          "associated records. Type 'delete' to confirm.",
      );
      if (confirmation) {
        FetchUtils.apiFetch({
          url: `${pageManager.baseURL}/user/delete_account`,
          method: "DELETE",
          body: { confirmation: confirmation },
          successHandler: () => {
            window.location.href = `${pageManager.baseURL}/user/login`;
          },
          errorHandler: (response) => {
            pageManager.showTempPopupMessage(
              "Confirmation Must Be Entered Exactly. Account Not Deleted",
              2000,
            );
          },
        });
      }
    });
  }

  addOpenChangePasswordListener() {
    const changePassword = document.querySelector("#change-password");
    changePassword.addEventListener("click", (e) => {
      this.openChangePassword();
    });
  }

  openChangePassword() {
    pageManager
      .fetchData({
        url: `${pageManager.baseURL}/user/change_password_form`,
        method: "GET",
        responseType: "text",
      })
      .then((contentHTML) => {
        pageManager.updateContent(contentHTML, "settings");
        this.changePasswordEventListeners();
      });
  }

  addUpdateAccountSettingsListener() {
    const updateAccountSettings = document.querySelector("#update-account");
    updateAccountSettings.addEventListener("click", (e) => {
      this.updateAccountSettings();
    });
  }

  updateAccountSettings() {
    const formData = FormUtils.getFormData("account-settings-form");
    FormUtils.clearFormErrors();
    FetchUtils.apiFetch({
      url: `${pageManager.baseURL}/user/settings/account_settings/`,
      method: "PATCH",
      body: formData,
      successHandler: (response) => {
        pageManager.showTempPopupMessage("Account Updated.", 2000);
      },
      errorHandler: FormUtils.formErrorHandler,
    });
  }
  accountSettingsListeners() {
    this.addDeleteAccountListener();
    this.addOpenChangePasswordListener();
    this.addUpdateAccountSettingsListener();
  }

  changePassword() {
    const formData = FormUtils.getFormData("change-password-form");
    FormUtils.clearFormErrors();
    FetchUtils.apiFetch({
      url: `${pageManager.baseURL}/user/change_password/`,
      method: "POST",
      body: formData,
      successHandler: (response) => {
        pageManager.showTempPopupMessage("Password Updated.", 2000);
        settingsManager.initialize();
      },
      errorHandler: FormUtils.formErrorHandler,
    });
  }
  addChangePasswordListener() {
    const changePassword = document.querySelector("#change-password");
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
    const returnToSettingsLink = document.querySelector("#return-to-settings");
    returnToSettingsLink.addEventListener("click", (e) => {
      e.preventDefault();
      settingsManager.initialize();
    });
  }
}

window.settingsManager = new SettingsManager();
