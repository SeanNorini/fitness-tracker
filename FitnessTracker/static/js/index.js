const domain = document.querySelector("#domain").value;

const settingModule = document.querySelector("#settings");
settingModule.id = "user/settings";

const modules = document.querySelectorAll(".module");

let unitOfMeasurement = "";
modules.forEach((module) => {
  module.addEventListener("click", (e) => {
    fetch(`http://${domain}/${module.id}`, {
      method: "GET",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .then((response) => response.text())
      .then((contentHTML) => {
        const contentContainer = document.querySelector("#content");
        contentContainer.innerHTML = contentHTML;
        loadModule(module.id);
      });
  });
});

function loadModule(module) {
  let scriptLoaded = null;
  switch (module) {
    case "workout":
      document.title = "Fitness Tracker - Workout";
      window.history.pushState({}, "", "/workout/");
      scriptLoaded = addScript("/static/workout/js/workout.js");
      if (!scriptLoaded) {
        workoutManager.initialize();
      }
      break;
    case "stats":
      window.history.pushState({}, "", "/stats/");
      addStylesheet("/static/workout/css/stats.css");
      addStylesheet("/static/css/button_group.css");
      scriptLoaded = addScript("/static/workout/js/stats.js");
      if (scriptLoaded) {
        scriptLoaded.onload = function () {
          loadStats();
        };
      } else {
        loadStats();
      }
      break;
    case "user/settings":
      window.history.pushState({}, "", "/user/settings/");
      addStylesheet("/static/css/button_group.css");
      addStylesheet("/static/users/css/form.css");
      addStylesheet("/static/users/css/settings.css");
      addScript("/static/workout/js/workout.js");
      scriptLoaded = addScript("/static/users/js/settings.js");
      if (scriptLoaded) {
        scriptLoaded.onload = function () {
          loadSettings();
        };
      } else {
        loadSettings();
      }
      break;
    case "log":
      window.history.pushState({}, "", "/log/");
      addStylesheet("/static/log/css/log.css");
      scriptLoaded = addScript("/static/log/js/log.js");
      if (scriptLoaded) {
        scriptLoaded.onload = function () {
          loadLog();
        };
      } else {
        loadLog();
      }
      break;
    case "cardio":
      window.history.pushState({}, "", "/cardio/");
      break;
  }
}

function addScript(src) {
  if (!isScriptLoaded(src)) {
    let script = document.createElement("script");
    script.src = src;
    document.head.appendChild(script);
    return script;
  }
}

function addStylesheet(href) {
  if (!isStylesheetLoaded(href)) {
    let link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = href;
    document.head.appendChild(link);
  }
}

function isScriptLoaded(src) {
  let scripts = document.getElementsByTagName("script");
  for (let i = 0; i < scripts.length; i++) {
    if (scripts[i].getAttribute("src") == src) {
      return true;
    }
  }
  return false;
}

function isStylesheetLoaded(href) {
  let links = document.getElementsByTagName("link");
  for (let i = 0; i < links.length; i++) {
    if (links[i].getAttribute("href") == href) {
      return true;
    }
  }
  return false;
}

const startingURL = window.location.href;

if (startingURL.includes("stats")) {
  loadModule("stats");
} else if (startingURL.includes("settings")) {
  loadModule("user/settings");
} else if (startingURL.includes("log")) {
  loadModule("log");
} else {
  loadModule("workout");
}

function disablePageExcept(element) {
  // Disable pointer events on page except for given element
  document.body.classList.add("disabled");
  element.classList.add("enabled");
}

function enablePage(element) {
  // Enable pointer events on page
  document.body.classList.remove("disabled");
  element.classList.remove("enabled");
}

function addReEnablePageListener(enabledElement, closeBtn) {
  function reEnablePageHandler(e) {
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
  }

  // Add listener with slight delay to prevent first click from triggering event
  setTimeout(() => {
    document.addEventListener("click", reEnablePageHandler);
  }, 0);
}
