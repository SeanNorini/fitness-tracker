class StatsManager {
  constructor() {
    this.baseURL = pageManager.baseURL + "/stats";
  }

  getGraphSettings() {
    const selections = document.querySelectorAll(".active");

    const dateRange = selections[0].value;

    let stat = selections[1].value;
    if (stat === "weightlifting") {
      stat = document.getElementById("select-exercise").value;
    }

    return { dateRange: dateRange, stat: stat };
  }

  updateGraph() {
    const graphSettings = this.getGraphSettings();

    FetchUtils.apiFetch({
      url: `${this.baseURL}/${graphSettings["stat"]}/${graphSettings["dateRange"]}`,
      method: "GET",
      successHandler: (response) => {
        pageManager.updateGraph(response["graph"], "graph");
      },
      errorHandler: {},
    });
  }

  btnGroupHandler = () => {
    const weightliftingButton = document.querySelector("#weightlifting");
    if (weightliftingButton.classList.contains("active")) {
      this.selectExerciseDropdown.classList.remove("hidden");
    } else {
      this.selectExerciseDropdown.classList.add("hidden");
    }
    this.updateGraph();
  };
  initialize() {
    this.updateGraph();
    this.selectExerciseDropdown = document.getElementById("select-exercise");
    this.selectExerciseDropdown.addEventListener("change", (e) => {
      this.updateGraph();
    });
    pageManager.addBtnGroupToggleListeners(this.btnGroupHandler);
  }
}

window.statsManager = new StatsManager();
