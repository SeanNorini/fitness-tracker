class NutritionManager {
  constructor() {
    this.baseURL = pageManager.baseURL + "/nutrition";
    this.searchBar = new SearchBar(null, 3, true);
  }

  initialize() {
    this.searchBar.initialize();
    this.addItemListener();
    this.removeItemListener();
    this.saveLogListener();
    this.setDate();
    this.getNutritionSummary();
  }

  getNutritionSummary() {
    FetchUtils.apiFetch({
      url: `${this.baseURL}/get_nutrition_summary/week/`,
      method: "GET",
      successHandler: this.getNutritionSummarySuccessHandler,
      errorHandler: {},
    });
  }

  getNutritionSummarySuccessHandler = (response) => {
    const pieChart = this.createGraphImg(response["pie_chart"]);
    const pieChartContainer = document.getElementById("pie-chart");
    pieChartContainer.innerHTML = "";
    pieChartContainer.appendChild(pieChart);

    pageManager.updateGraph(response["bar_chart"], "bar-chart");

    const proteinContainer = document.querySelector(".avg-protein");
    proteinContainer.textContent = response["avg_protein"]
      ? `${response["avg_protein"]}g`
      : "0g";
    const carbsContainer = document.querySelector(".avg-carbs");
    carbsContainer.textContent = response["avg_carbs"]
      ? `${response["avg_carbs"]}g`
      : "0g";
    const fatContainer = document.querySelector(".avg-fat");
    fatContainer.textContent = response["avg_fat"]
      ? `${response["avg_fat"]}g`
      : "0g";
    const caloriesContainer = document.querySelector(".avg-calories");
    caloriesContainer.textContent = response["avg_calories"]
      ? response["avg_calories"]
      : "0";
  };

  saveLogListener() {
    const saveLogBtn = document.getElementById("save-log");
    saveLogBtn.addEventListener("click", (e) => {
      const containers = document.querySelector(".nutrition-info").children;
      const formData = { food_items: [] };
      for (let i = 7; i < containers.length - 7; i += 7) {
        const foodItem = {};
        foodItem["name"] = containers[i].textContent;
        foodItem["serving"] = containers[i + 1].textContent;
        foodItem["calories"] = containers[i + 2].textContent;
        foodItem["protein"] = containers[i + 3].textContent;
        foodItem["carbs"] = containers[i + 4].textContent;
        foodItem["fat"] = containers[i + 5].textContent;
        formData.food_items.push(foodItem);
      }
      formData["date"] = document.getElementById("date").value;

      FetchUtils.apiFetch({
        url: `${pageManager.baseURL}/log/food_log/`,
        method: "POST",
        body: formData,
        successHandler: (response) => {
          pageManager.showTempPopupMessage("Food Log Saved.", 2000);
          this.getNutritionSummary();
          document.getElementById("food-log-pk").value = response.pk;
        },
      });
    });
  }

  setDate(date) {
    // Set calendar date on workout, default to current date.
    if (!date) {
      const currentDate = new Date();
      document.getElementById("date").valueAsDate = new Date(
        currentDate.getTime() - currentDate.getTimezoneOffset() * 60000,
      );
    } else {
      document.getElementById("date").valueAsDate = date;
    }
  }

  addItemListener() {
    const addItemBtn = document.getElementById("add-item");
    addItemBtn.addEventListener("click", (e) => {
      if (this.searchBar.itemDetails === null) {
        return;
      } else {
        const itemDetails = this.searchBar.itemDetails;
        let gridElements = [];
        for (let i = 0; i < 7; i++) {
          const element = document.createElement("div");
          element.classList.add("grid-item");
          gridElements.push(element);
        }
        gridElements[0].textContent = itemDetails["food_name"];
        gridElements[1].textContent = `${itemDetails["serving_qty"]} ${itemDetails["serving_unit"]}`;
        gridElements[2].textContent = itemDetails["nf_calories"];
        gridElements[2].classList.add("calories");
        gridElements[3].textContent = itemDetails["nf_protein"];
        gridElements[3].classList.add("protein");
        gridElements[4].textContent = itemDetails["nf_total_carbohydrate"];
        gridElements[4].classList.add("carbs");
        gridElements[5].textContent = itemDetails["nf_total_fat"];
        gridElements[5].classList.add("fat");
        gridElements[6].innerHTML = `<span class="material-symbols-outlined delete hover-red text-xl">delete</span>`;

        const totalElement = document.getElementById("total");

        gridElements.forEach((element) => {
          totalElement.before(element);
        });
      }
      this.calcFoodLogTotals();
    });
  }

  removeItemListener() {
    const foodLogContainer = document.querySelector(".nutrition-info");
    foodLogContainer.addEventListener("click", (e) => {
      if (e.target.classList.contains("delete")) {
        let elementToDelete = e.target.closest("div");

        for (let i = 0; i < 7; i++) {
          if (elementToDelete) {
            const previousElement = elementToDelete.previousElementSibling;

            elementToDelete.remove();

            elementToDelete = previousElement;
          }
        }
      }
      this.calcFoodLogTotals();
    });
  }

  calcFoodLogTotals() {
    let calories = 0;
    let protein = 0;
    let carbs = 0;
    let fat = 0;

    const calorieContainers = document.querySelectorAll(".calories");
    const proteinContainers = document.querySelectorAll(".protein");
    const carbsContainers = document.querySelectorAll(".carbs");
    const fatContainers = document.querySelectorAll(".fat");

    calorieContainers.forEach((container) => {
      calories += parseInt(container.textContent);
    });

    proteinContainers.forEach((container) => {
      protein += parseInt(container.textContent);
    });

    carbsContainers.forEach((container) => {
      carbs += parseInt(container.textContent);
    });

    fatContainers.forEach((container) => {
      fat += parseInt(container.textContent);
    });

    const totalCalories = document.getElementById("total-calories");
    const totalProtein = document.getElementById("total-protein");
    const totalCarbs = document.getElementById("total-carbs");
    const totalFat = document.getElementById("total-fat");

    totalCalories.textContent = calories;
    totalProtein.textContent = protein;
    totalCarbs.textContent = carbs;
    totalFat.textContent = fat;
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
}

window.nutritionManager = new NutritionManager();
