class PageManager {
  constructor() {
    this.baseURL = window.location.origin;
    this.overlay = document.getElementById("overlay");
    this.popupStack = [];
    this.currentPopup = null;
    this.addModuleLinkListeners();
    this.loadStartingModule();
    this.csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
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
    } else if (startingURL.includes("workout")) {
      this.loadModule("workout");
    } else if (startingURL.includes("cardio")) {
      this.loadModule("cardio");
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
    }
  }

  loadWorkoutModule() {
    this.updateModuleWindow("Fitness Tracker - Workout", "/workout");
    this.loadModuleScript("/static/workout/js/workout.js", "workoutManager");
  }

  loadStatsModule() {
    this.updateModuleWindow("Fitness Tracker - Stats", "/stats");
    this.loadModuleScript("/static/workout/js/stats.js", "statsManager");
    this.loadModuleStylesheets([
      "/static/workout/css/stats.css",
      "/static/css/button_group.css",
    ]);
  }

  loadSettingsModule() {
    this.updateModuleWindow("Fitness Tracker - Settings", "/user/settings");
    this.loadModuleScript("/static/users/js/settings.js", "settingsManager");
    this.loadModuleStylesheets([
      "/static/css/button_group.css",
      "/static/users/css/form.css",
      "/static/users/css/settings.css",
    ]);
  }

  loadLogModule() {
    this.updateModuleWindow("Fitness Tracker - Log", "/log");
    this.loadModuleScript("/static/log/js/log.js", "logManager");
    this.loadModuleStylesheets(["/static/log/css/log.css"]);
  }

  loadCardioModule() {
    this.updateModuleWindow("Fitness Tracker - Cardio", "/cardio");
    this.loadModuleScript("/static/cardio/js/cardio.js", "cardioManager");
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

    const closePopupBtn = popupElement.querySelector(".close_popup_container");
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
    this.overlay.classList.add("dark_overlay");
  }

  enablePage() {
    // Enable pointer events on page
    document.body.classList.remove("disabled");
    this.overlay.classList.remove("dark_overlay");
  }

  buttonGroupToggle(btnElement) {
    const group = btnElement.getAttribute("data-group");
    const btnGroup = document.querySelectorAll(
      `.button_back[data-group="${group}"]`,
    );

    if (!btnElement.classList.contains("active")) {
      btnGroup.forEach((btn) => {
        if (btn !== btnElement) {
          btn.classList.remove("active");
        }
      });

      btnElement.classList.toggle("active");
    }
  }
  addButtonGroupToggleListeners(btnGroupHandler) {
    document.querySelectorAll(".button_back").forEach((groupBtn) => {
      groupBtn.addEventListener("click", (e) => {
        pageManager.buttonGroupToggle(groupBtn);
        btnGroupHandler(e);
      });
    });
  }

  fetchData(args) {
    return fetch(args.url, {
      method: args.method,
      headers: {
        Fetch: "True",
        "X-CSRFTOKEN": pageManager.csrftoken,
        ...args.headers,
      },
      body: args.body,
    }).then((response) => {
      return response[args.responseType]();
    });
  }

  updateContent(content, contentContainerID) {
    const contentContainer = document.getElementById(contentContainerID);
    contentContainer.innerHTML = content;
  }

  showTempPopupMessage(message, duration) {
    // Display popup message
    const popupElement = document.getElementById("temp_popup");
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

class DragAndDrop {
  initialize(marginOffset = null) {
    this.parentContainer = document.querySelector(".drag_and_drop_container");
    this.draggableSelector = ".drag_and_drop_element";
    this.handlebarClass = "drag_and_drop_handlebar";
    this.parentContainer.addEventListener("mousedown", this.dragStart);
    this.marginOffset = marginOffset;
  }

  dragStart = (e) => {
    // Get nearest draggable element
    this.dragStartElement = e.target.closest(this.draggableSelector);

    if (
      this.dragStartElement &&
      e.target.classList.contains(this.handlebarClass)
    ) {
      this.cloneStartElement();
      this.dragStartElement.firstElementChild.classList.add("dragging");

      // Get original element position
      this.offsetX =
        e.clientX - this.dragStartElement.getBoundingClientRect().left;
      this.offsetY =
        e.clientY - this.dragStartElement.getBoundingClientRect().top;

      // Get start position of element being dragged
      this.startX = e.clientX - this.offsetX + window.scrollX;
      this.startY = e.clientY - this.offsetY + window.scrollY;

      // Set dragged element to start position
      this.cloneElement.style.left = this.startX + "px";
      this.cloneElement.style.top = this.startY + "px";

      // Activate listeners for dragging
      this.addDragListeners();
    }
  };

  cloneStartElement() {
    this.cloneElement = this.dragStartElement.cloneNode(true);
    this.cloneElement.classList.add("draggable"); // Toggle class for CSS style on dragged element
    this.parentContainer.appendChild(this.cloneElement);
    if (this.marginOffset) {
      this.cloneElement.style.margin = this.marginOffset;
    }
  }

  addDragListeners() {
    document.addEventListener("mousemove", this.onMousemoveHandler);
    document.addEventListener("mouseup", this.dragEnd);

    const draggableElements = this.parentContainer.querySelectorAll(
      this.draggableSelector,
    );
    draggableElements.forEach((draggableElement) => {
      draggableElement.addEventListener("mouseenter", this.onMouseenterHandler);
      draggableElement.addEventListener("mouseleave", this.onMouseleaveHandler);
    });
  }

  onMousemoveHandler = (e) => {
    this.cloneElement.style.left =
      e.clientX - this.offsetX + window.scrollX + "px";
    this.cloneElement.style.top =
      e.clientY - this.offsetY + window.scrollY + "px";
  };

  onMouseenterHandler = (e) => {
    if (this.startY < e.clientY) {
      e.target.firstElementChild.style.transform = "translateY(-10px)";
    } else {
      e.target.firstElementChild.style.transform = "translateY(10px)";
    }
  };

  onMouseleaveHandler(e) {
    e.target.classList.remove("drag_over");
    e.target.firstElementChild.style.transform = "translateY(0)";
  }

  dragEnd = (e) => {
    // Get element being dragged onto
    this.dragAndDropTarget = this.getDragAndDropTarget(e);

    this.removeDragListeners();

    if (this.dragAndDropTarget) {
      // Move elements and clean up
      this.moveElements(e);
      this.cloneElement.style.margin = this.dragStartElement.style.margin;
      this.dragStartElement.remove();
      this.cloneElement.classList.remove("draggable");
    } else {
      // Invalid drag and drop, remove dragged element and make no changes
      this.dragStartElement.firstElementChild.classList.remove("dragging");
      this.cloneElement.remove();
    }
  };

  getDragAndDropTarget(e) {
    const dragEndElement = document.elementFromPoint(e.clientX, e.clientY);
    return dragEndElement.closest(this.draggableSelector);
  }

  removeDragListeners() {
    document.removeEventListener("mousemove", this.onMousemoveHandler);
    document.removeEventListener("mouseup", this.dragEnd);

    const draggableContainers = this.parentContainer.querySelectorAll(
      this.draggableSelector,
    );
    draggableContainers.forEach((draggable) => {
      draggable.removeEventListener("mouseenter", this.onMouseenterHandler);
      draggable.removeEventListener("mouseleave", this.onMouseleaveHandler);
    });
  }

  moveElements(e) {
    if (this.startY < e.clientY) {
      // Insert after if element was dragged down
      this.parentContainer.insertBefore(
        this.cloneElement,
        this.dragAndDropTarget.nextSibling,
      );
    } else {
      // Insert before if element was dragged up
      this.parentContainer.insertBefore(
        this.cloneElement,
        this.dragAndDropTarget,
      );
    }
    this.dragAndDropTarget.firstElementChild.style.transform = "translateY(0)";
  }
}

const pageManager = new PageManager();
