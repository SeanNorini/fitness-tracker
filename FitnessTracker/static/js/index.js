class PageManager {
  constructor() {
    this.baseURL = window.location.origin;

    this.addModuleLinkListeners();
    this.loadStartingModule();
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
    } else {
      this.loadModule("workout");
    }
  }

  addModuleLinkListeners() {
    // Change setting module id for fetch link
    const settingModule = document.querySelector("#settings");
    settingModule.id = "user/settings";

    // Create listeners for module navigation
    const modules = document.querySelectorAll(".module");
    modules.forEach((module) => {
      module.addEventListener("click", (e) => {
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
    }
  }

  loadWorkoutModule() {
    document.title = "Fitness Tracker - Workout";
    window.history.pushState({}, "", "/workout/");
    const scriptLoaded = this.addScript("/static/workout/js/workout.js");
    if (scriptLoaded) {
      scriptLoaded.onload = () => {
        workoutManager.initialize();
      };
    } else {
      workoutManager.initialize();
    }
  }

  loadStatsModule() {
    window.history.pushState({}, "", "/stats/");
    this.addStylesheet("/static/workout/css/stats.css");
    this.addStylesheet("/static/css/button_group.css");
    const scriptLoaded = this.addScript("/static/workout/js/stats.js");
    if (scriptLoaded) {
      scriptLoaded.onload = () => {
        loadStats();
      };
    } else {
      loadStats();
    }
  }

  loadSettingsModule() {
    window.history.pushState({}, "", "/user/settings/");
    this.addStylesheet("/static/css/button_group.css");
    this.addStylesheet("/static/users/css/form.css");
    this.addStylesheet("/static/users/css/settings.css");
    const scriptLoaded = this.addScript("/static/users/js/settings.js");
    if (scriptLoaded) {
      scriptLoaded.onload = () => {
        loadSettings();
      };
    } else {
      loadSettings();
    }
  }

  loadLogModule() {
    window.history.pushState({}, "", "/log/");
    this.addStylesheet("/static/log/css/log.css");
    const scriptLoaded = this.addScript("/static/log/js/log.js");
    if (scriptLoaded) {
      scriptLoaded.onload = () => {
        loadLog();
      };
    } else {
      loadLog();
    }
  }

  loadCardioModule() {
    window.history.pushState({}, "", "/cardio/");
  }

  addScript(src) {
    if (!this.isScriptLoaded(src)) {
      let script = document.createElement("script");
      script.src = src;
      document.head.appendChild(script);
      return script;
    }
  }

  addStylesheet(href) {
    if (!this.isStylesheetLoaded(href)) {
      let link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = href;
      document.head.appendChild(link);
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

  isStylesheetLoaded(href) {
    let links = document.getElementsByTagName("link");
    for (let i = 0; i < links.length; i++) {
      if (links[i].getAttribute("href") === href) {
        return true;
      }
    }
    return false;
  }

  disablePageExcept(element) {
    // Disable pointer events on page except for given element
    document.body.classList.add("disabled");
    element.classList.add("enabled");
  }

  enablePage(element) {
    // Enable pointer events on page
    document.body.classList.remove("disabled");
    element.classList.remove("enabled");
  }

  addReEnablePageListener(enabledElement, closeBtn) {
    const reEnablePageHandler = (e) => {
      // If user clicks outside enabled element, close element and remove listener
      if (
        !enabledElement.contains(e.target) &&
        enabledElement.style.display === "block"
      ) {
        closeBtn.click();
        document.removeEventListener("click", reEnablePageHandler);
      }

      // If user clicks close button manually, trigger normal event and remove listener
      if (e.target === closeBtn) {
        document.removeEventListener("click", reEnablePageHandler);
      }
    };

    // Add listener with slight delay to prevent first click from triggering event
    setTimeout(() => {
      document.addEventListener("click", reEnablePageHandler);
    }, 0);
  }
}

const pageManager = new PageManager();
