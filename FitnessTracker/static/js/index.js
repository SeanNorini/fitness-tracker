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
            Fetch: "True",
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
        fetch: "True",
        "X-CSRFTOKEN": pageManager.csrftoken,
        ...args.headers,
      },
      body: args.body,
    }).then((response) => {
      if (response.ok) {
        return response[args.responseType]();
      } else {
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

  updateDropdownMenu(options) {
    const { option, action, selector, placeholderOption = "" } = options;
    const newOption = document.createElement("option");
    newOption.textContent = option;

    const dropdownMenu = document.querySelector(selector);
    if (action === "add") {
      dropdownMenu.appendChild(newOption);
      newOption.selected = true;
    } else {
      const menuOptions = dropdownMenu.querySelectorAll("option");
      menuOptions.forEach((menuOption) => {
        if (menuOption.textContent === option) {
          menuOption.remove();
          dropdownMenu.value = placeholderOption;
        }
      });
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
