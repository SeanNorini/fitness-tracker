class StatsManager {
  constructor() {
    this.baseURL = pageManager.baseURL + "/stats/";
  }

  getGraph() {
    const formData = this.getGraphSettings();

    return pageManager
      .fetchData({
        url: this.baseURL,
        method: "POST",
        body: formData,
        responseType: "arrayBuffer",
      })
      .then((graphBuffer) => {
        return graphBuffer;
      });
  }

  getGraphSettings() {
    const formData = new FormData();
    const selections = document.querySelectorAll(".active");

    const dateRange = selections[0].value;
    formData.append("date_range", dateRange);

    const stat = selections[1].value;
    formData.append("stat", stat);

    if (stat === "weightlifting") {
      const exercise = document.getElementById("select-exercise").value;
      formData.append("exercise", exercise);
    }

    const csrftoken = document.querySelector(
      "[name=csrfmiddlewaretoken]",
    ).value;
    formData.append("csrfmiddlewaretoken", csrftoken);

    return formData;
  }

  convertBufferToImg(buffer) {
    // Convert array buffer to Uint8Array
    const byteArray = new Uint8Array(buffer);

    // Convert bytes data to base64
    const base64String = btoa(String.fromCharCode(...byteArray));

    // Create image element and set src to base64 data
    const img = document.createElement("img");
    img.src = "data:image/png;base64," + base64String;

    return img;
  }

  updateGraph() {
    this.getGraph().then((graphBuffer) => {
      const graphImg = this.convertBufferToImg(graphBuffer);
      const graphContainer = document.getElementById("graph");

      graphContainer.innerHTML = "";
      graphContainer.appendChild(graphImg);
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
