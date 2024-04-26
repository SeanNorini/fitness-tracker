class PageManager {
  constructor() {
    this.baseURL = window.location.origin;
    this.overlay = document.getElementById("overlay");
    this.popupStack = [];
    this.date = new Date();
    this.currentPopup = null;
    this.addModuleLinkListeners();
    this.loadStartingModule();
    this.csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    this.rootFontSize = parseFloat(
      window.getComputedStyle(document.documentElement).fontSize,
    );
  }

  loadStartingModule() {
    // Check starting url and load content for that module
    const startingURL = window.location.href;
    if (startingURL.includes("stats")) {
      this.loadModule("stats");
    } else if (startingURL.includes("settings")) {
      this.loadModule("user/settings");
    } else if (startingURL.includes("log")) {
      this.loadModule("log");
    } else if (
      startingURL.includes("workout") ||
      startingURL === `${this.baseURL}/`
    ) {
      this.loadModule("workout");
    } else if (startingURL.includes("cardio")) {
      this.loadModule("cardio");
    } else if (startingURL.includes("nutrition")) {
      this.loadModule("nutrition");
    }
  }

  addModuleLinkListeners() {
    // Change setting module id for fetch link
    const settingModule = document.querySelector("#settings");
    settingModule.id = "user/settings";

    // Create listeners for module navigation
    const modules = document.querySelectorAll(".module");
    modules.forEach((module) => {
      module.addEventListener("click", () => {
        fetch(`${this.baseURL}/${module.id}`, {
          method: "GET",
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        })
          .then((response) => response.text())
          .then((contentHTML) => {
            const contentContainer = document.querySelector("#content");
            contentContainer.innerHTML = contentHTML;
            this.loadModule(module.id);
          });
      });
    });
  }

  loadModule(module) {
    switch (module) {
      case "workout":
        this.loadWorkoutModule();
        break;
      case "stats":
        this.loadStatsModule();
        break;
      case "user/settings":
        this.loadSettingsModule();
        break;
      case "log":
        this.loadLogModule();
        break;
      case "cardio":
        this.loadCardioModule();
        break;
      case "nutrition":
        this.loadNutritionModule();
    }
  }

  loadNutritionModule() {
    this.updateModuleWindow("Fitness Tracker - Nutrition", "/nutrition");
    this.loadModuleScript("/static/js/nutrition.js", "nutritionManager");
    this.loadModuleStylesheets(["/static/css/nutrition.css"]);
  }

  loadWorkoutModule() {
    this.updateModuleWindow("Fitness Tracker - Workout", "/workout");
    this.loadModuleScript("/static/js/workout.js", "workoutManager");
  }

  loadStatsModule() {
    this.updateModuleWindow("Fitness Tracker - Stats", "/stats");
    this.loadModuleScript("/static/js/stats.js", "statsManager");
    this.loadModuleStylesheets(["/static/css/button_group.css"]);
  }

  loadSettingsModule() {
    this.updateModuleWindow("Fitness Tracker - Settings", "/user/settings");
    this.loadModuleScript("/static/js/settings.js", "settingsManager");
    this.loadModuleStylesheets(["/static/css/button_group.css"]);
  }

  loadLogModule() {
    this.updateModuleWindow("Fitness Tracker - Log", "/log");
    this.loadModuleScript("/static/js/log.js", "logManager");
    this.loadModuleStylesheets(["/static/css/log.css"]);
  }

  loadCardioModule() {
    this.updateModuleWindow("Fitness Tracker - Cardio", "/cardio");
    this.loadModuleScript("/static/js/cardio.js", "cardioManager");
    this.loadModuleStylesheets(["/static/css/button_group.css"]);
  }

  loadModuleScript(scriptURL, moduleManager) {
    // Load javascript if necessary, then run method to initialize page
    const scriptLoaded = this.addScript(scriptURL);
    if (scriptLoaded) {
      scriptLoaded.onload = () => {
        window[moduleManager].initialize();
      };
    } else {
      window[moduleManager].initialize();
    }
  }

  addScript(src) {
    if (!this.isScriptLoaded(src)) {
      let script = document.createElement("script");
      script.src = src;
      document.head.appendChild(script);
      return script;
    }
  }

  isScriptLoaded(src) {
    let scripts = document.getElementsByTagName("script");
    for (let i = 0; i < scripts.length; i++) {
      if (scripts[i].getAttribute("src") === src) {
        return true;
      }
    }
    return false;
  }

  updateModuleWindow(title, pageURL) {
    document.title = title;
    window.history.pushState({}, "", pageURL);
  }

  loadModuleStylesheets(hrefs) {
    hrefs.forEach((href) => {
      if (!this.isStylesheetLoaded(href)) {
        let link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = href;
        document.head.appendChild(link);
      }
    });
  }

  isStylesheetLoaded(href) {
    let links = document.getElementsByTagName("link");
    for (let i = 0; i < links.length; i++) {
      if (links[i].getAttribute("href") === href) {
        return true;
      }
    }
    return false;
  }

  openPopup(popupElementID, cleanupCallback = null) {
    const popupElement = document.getElementById(popupElementID);
    this.popupStack.push(popupElement);
    this.currentPopup = popupElement;

    this.enableTopPopup(popupElement);
    this.disablePage();
    this.addClosePopupHandler(popupElement, cleanupCallback);
  }

  enableTopPopup(popupElement) {
    popupElement.style.display = "flex";
    popupElement.style.flexDirection = "col";
    popupElement.classList.add("enabled");
    popupElement.style.zIndex = (this.popupStack.length + 1).toString();

    if (this.popupStack.length > 1) {
      const previousPopup = this.popupStack[this.popupStack.length - 2];
      previousPopup.classList.remove("enabled");
      this.overlay.style.zIndex = (this.popupStack.length + 1).toString();
    }
  }

  addClosePopupHandler(popupElement, cleanupCallback) {
    const closePopupHandler = (e) => {
      e.stopPropagation();
      popupElement.style.display = "none";
      this.popupStack.pop();
      this.overlay.style.zIndex = (this.popupStack.length + 1).toString();

      // Run extra cleanup if necessary
      if (cleanupCallback) {
        cleanupCallback();
      }

      if (!this.popupStack.length) {
        this.enablePage();
        this.currentPopup = null;
      } else {
        this.currentPopup = this.popupStack[this.popupStack.length - 1];
        this.currentPopup.classList.add("enabled");
      }
      document.removeEventListener("click", closePopupOutsideHandler);
    };

    const closePopupBtn = popupElement.querySelector(".close-popup-container");
    closePopupBtn.addEventListener("click", closePopupHandler, { once: true });

    const closePopupOutsideHandler = (e) => {
      // Close element if user clicks outside of it
      if (
        !popupElement.contains(e.target) &&
        popupElement === this.currentPopup
      ) {
        closePopupBtn.click();
        document.removeEventListener("click", closePopupOutsideHandler);
      }
    };

    // Add listener with slight delay to prevent first click from triggering event
    setTimeout(() => {
      document.addEventListener("click", closePopupOutsideHandler);
    }, 0);
  }

  disablePage() {
    // Disable pointer events on page and add dark overlay
    document.body.classList.add("disabled");
    this.overlay.classList.add("dark-overlay");
  }

  enablePage() {
    // Enable pointer events on page
    document.body.classList.remove("disabled");
    this.overlay.classList.remove("dark-overlay");
  }

  btnGroupToggle(btnElement) {
    const group = btnElement.getAttribute("data-group");
    const btnGroup = document.querySelectorAll(
      `.btn-back[data-group="${group}"]`,
    );

    if (!btnElement.classList.contains("active")) {
      btnGroup.forEach((btn) => {
        if (btn !== btnElement) {
          btn.classList.remove("active");
        }
      });

      btnElement.classList.add("active");
    }
  }
  addBtnGroupToggleListeners(btnGroupHandler) {
    document.querySelectorAll(".btn-back").forEach((groupBtn) => {
      groupBtn.addEventListener("click", (e) => {
        pageManager.btnGroupToggle(groupBtn);
        btnGroupHandler(e);
      });
    });
  }

  fetchData(args) {
    return fetch(args.url, {
      method: args.method,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFTOKEN": pageManager.csrftoken,
        ...args.headers,
      },
      body: args.body,
    }).then((response) => {
      if (response.ok) {
        return response[args.responseType]();
      } else {
        console.log(response.json());
        throw new Error("Network response was not ok");
      }
    });
  }

  updateContent(content, contentContainerID) {
    const contentContainer = document.getElementById(contentContainerID);
    contentContainer.innerHTML = content;
  }

  showTempPopupMessage(message, duration) {
    // Display popup message
    const popupElement = document.getElementById("popup-message");
    popupElement.textContent = message;
    popupElement.style.display = "flex";

    // Close message after duration
    setTimeout(function () {
      popupElement.style.display = "none";
    }, duration);
  }

  showTempPopupErrorMessages(messages, duration) {
    // Display popup message
    const popupElement = document.getElementById("popup-message");
    const container = document.createElement("div");
    Object.values(messages).forEach((message) => {
      const element = document.createElement("div");
      element.textContent = message;
      container.appendChild(element);
    });
    popupElement.innerHTML = "";
    popupElement.appendChild(container);
    popupElement.style.display = "flex";

    // Close message after duration
    setTimeout(function () {
      popupElement.style.display = "none";
    }, duration);
  }

  addCollapsibleListener(element, controllerSelector, collapsibleSelector) {
    const controllerElement = element.querySelector(controllerSelector);
    controllerElement.addEventListener("click", (e) => {
      const collapsibleElement = element.querySelector(collapsibleSelector);
      collapsibleElement.classList.toggle("hidden");
    });
  }

  createElementFromHTMLText(contentHTML) {
    const elementTemplate = document.createElement("template");
    elementTemplate.innerHTML = contentHTML.trim();
    return elementTemplate.content.firstChild;
  }

  updateGraph(graph, containerID) {
    const graphImg = this.createGraphImg(graph);
    const graphContainer = document.getElementById(containerID);

    graphContainer.innerHTML = "";
    graphContainer.appendChild(graphImg);
  }

  createGraphImg(base64Graph) {
    if (base64Graph) {
      const img = document.createElement("img");
      img.src = "data:image/png;base64," + base64Graph;
      return img;
    } else {
      const div = document.createElement("div");
      div.textContent = "No Chart To Display";
      return div;
    }
  }

  appendElement(element, container) {
    if (typeof container === "string") {
      container = document.getElementById(container);
    }
    container.appendChild(element);
    return container.lastElementChild;
  }

  cloneAndAppend(elementToClone, container) {
    if (typeof elementToClone === "string") {
      elementToClone = document.getElementById(elementToClone).content;
    }
    const clone = elementToClone.cloneNode(true);
    return this.appendElement(clone, container);
  }

  setValues(element, values) {
    for (const [key, value] of Object.entries(values)) {
      const input = element.querySelector(`.${key}`);
      if (input) {
        input.value = value;
      }
    }
  }
}

class Collapsible {
  constructor() {
    this.containerClass = ".collapse-container";
    this.controllerClass = ".collapse-controller";
    this.collapseClass = "collapse";
  }

  initialize() {
    const containers = document.querySelectorAll(this.containerClass);
    containers.forEach((container) => {
      this.addControllerListener(container);
    });
  }

  addControllerListener(container) {
    const controller = container.querySelector(this.controllerClass);
    controller.addEventListener("click", this.onClickHandler);
  }

  onClickHandler = (e) => {
    const collapseTargets = this.getCollapseTargets(
      e.currentTarget.parentNode.parentNode,
    );
    collapseTargets.forEach((target) => {
      target.classList.toggle("hide");
    });
  };

  getCollapseTargets(container) {
    return Array.from(container.children).filter((child) =>
      child.classList.contains(this.collapseClass),
    );
  }
}

const pageManager = new PageManager();

class FormUtils {
  /*
   * Static method to extract data from a form.
   *
   * Parameters:
   *   formID - The ID of the form element to process.
   *   args - An object that may contain:
   *     blankFields - A boolean indicating whether to include empty input values (default: false).
   *     postprocessFunc - A function to execute after processing each input (default: null).
   *     readOnly - A boolean indicating whether to include readonly input values (default: false).
   *
   * Returns:
   *   An object containing key-value pairs of form inputs, where keys are the names of the inputs.
   *
   * This method processes all input types, handling read-only fields based on settings,
   * and selectively including radio button inputs only if they are checked.
   */
  static getFormData(formID, args) {
    const settings = {
      blankFields: false,
      postprocessFunc: null,
      readOnly: false,
      ...args,
    };
    let formData = {};

    const formElements = document
      .getElementById(formID)
      .querySelectorAll("input");
    formElements.forEach((element) => {
      if (element.readOnly && !settings.readOnly) {
        return;
      }

      if (element.type === "radio" && element.checked) {
        formData[element.name] = element.value;
      } else if (element.value || settings.blankFields) {
        formData[element.name] = element.value;
      }
    });

    if (settings.postprocessFunc) {
      formData = settings.postprocessFunc(formData);
    }
    return formData;
  }

  static clearFormErrors() {
    // Clears all form errors on the page
    const errors = document.querySelectorAll(".errors");
    errors.forEach((error) => {
      error.innerHTML = "";
    });
  }

  static formErrorHandler(response) {
    // Iterate over errors from django response
    Object.entries(response).forEach(([key, value]) => {
      // Gather error fields
      const errorField = document.getElementById(key).querySelector(".errors");

      // Create error container
      const ul = document.createElement("ul");
      ul.classList.add("text-red", "text-sm");
      value.forEach((error) => {
        // Add errors to container
        const li = document.createElement("li");
        li.textContent = error;
        ul.appendChild(li);
      });
      // Add container to error field
      errorField.appendChild(ul);
    });
  }
}

class FetchUtils {
  static apiFetch(args) {
    fetch(args.url, {
      method: args.method,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFTOKEN": pageManager.csrftoken,
        "Content-Type": "application/json",
        ...args.headers,
      },
      body: JSON.stringify(args.body),
    })
      .then((response) => {
        if (response.ok) {
          if (
            response.status === 204 ||
            response.headers.get("Content-Length") === "0"
          ) {
            args.successHandler({});
          } else {
            response.json().then((response) => {
              args.successHandler(response);
            });
          }
        } else {
          response.json().then((response) => {
            args.errorHandler(response);
          });
        }
      })
      .catch((error) => {
        console.error("Server did not respond.", error);
      });
  }
}

class InputUtils {
  static roundedFloatHandler(element, min, max, increment) {
    /* Rounds to the nearest given increment min-max range, out of range values
    will return min if less than min or max if greater than max.*/
    let value = parseFloat(element.value);
    value = this.validateNumberInput(value, min, max);
    element.value = Math.round(value / increment) * increment;
  }

  static roundedIntegerHandler(element, min, max) {
    /* Rounds to nearest integer within min-max range, out of range values
    will return min if less than min or max if greater than max.*/
    let value = Math.round(parseFloat(element.value));
    element.value = this.validateNumberInput(value, min, max);
  }

  static validateNumberInput(value, min, max) {
    if (isNaN(value) || value < min) {
      value = min;
    }
    if (value > max) {
      value = max;
    }
    return value;
  }
}

function capitalize(str) {
  return str
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
}

function getCurrentDate() {
  const currentDate = new Date();
  return new Date(
    currentDate.getTime() - currentDate.getTimezoneOffset() * 60000,
  );
}

function validateDate(date) {
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;
  const currentDay = new Date().getDate();

  return (
    date.year < currentYear ||
    (date.year === currentYear && date.month < currentMonth) ||
    (date.year === currentYear &&
      date.month === currentMonth &&
      date.day <= currentDay)
  );
}

function splitDate(date) {
  const dateParts = date.split("-");
  const year = parseInt(dateParts[0], 10);
  const month = parseInt(dateParts[1], 10);
  const day = parseInt(dateParts[2], 10);
  return { year: year, month: month, day: day };
}
