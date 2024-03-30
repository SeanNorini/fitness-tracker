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
    pageManager
      .fetchData({
        url: `${this.baseURL}/get_nutrition_summary/week/`,
        method: "GET",
        responseType: "json",
      })
      .then((response) => {
        const pieChart = this.createGraphImg(response["pie_chart"]);
        const barChart = this.createGraphImg(response["bar_chart"]);
        const pieChartContainer = document.getElementById("pie_chart");
        const barChartContainer = document.getElementById("bar_chart");
        pieChartContainer.innerHTML = "";
        barChartContainer.innerHTML = "";
        pieChartContainer.appendChild(pieChart);
        barChartContainer.appendChild(barChart);

        const proteinContainer = document.querySelector(".avg_protein");
        proteinContainer.textContent = response["avg_protein"] + "g";
        const carbsContainer = document.querySelector(".avg_carbs");
        carbsContainer.textContent = response["avg_carbs"] + "g";
        const fatContainer = document.querySelector(".avg_fat");
        fatContainer.textContent = response["avg_fat"] + "g";
        const caloriesContainer = document.querySelector(".avg_calories");
        caloriesContainer.textContent = response["avg_calories"];
      });
  }

  saveLogListener() {
    const saveLogBtn = document.getElementById("save_log");
    saveLogBtn.addEventListener("click", (e) => {
      const containers = document.querySelector(".nutrition_info").children;
      const foods = { food_item: [] };
      for (let i = 7; i < containers.length - 7; i += 7) {
        const foodItem = {};
        foodItem["name"] = containers[i].textContent;
        foodItem["serving"] = containers[i + 1].textContent;
        foodItem["calories"] = containers[i + 2].textContent;
        foodItem["protein"] = containers[i + 3].textContent;
        foodItem["carbs"] = containers[i + 4].textContent;
        foodItem["fat"] = containers[i + 5].textContent;
        foods.food_item.push(foodItem);
      }
      const formData = new FormData();
      const date = document.getElementById("date").value;
      formData.append("foods", JSON.stringify(foods));
      formData.append("date", date);

      pageManager
        .fetchData({
          url: `${this.baseURL}/save_food_log/`,
          method: "POST",
          responseType: "json",
          body: formData,
        })
        .then((response) => {
          pageManager.showTempPopupMessage("Food Log Saved.", 2000);
          this.getNutritionSummary();
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
    const addItemBtn = document.getElementById("add_item");
    addItemBtn.addEventListener("click", (e) => {
      if (this.searchBar.itemDetails === null) {
        return;
      } else {
        const itemDetails = this.searchBar.itemDetails;
        let gridElements = [];
        for (let i = 0; i < 7; i++) {
          const element = document.createElement("div");
          element.classList.add("grid_item");
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
        gridElements[6].innerHTML = `<span class="material-symbols-outlined delete">delete</span>`;

        const totalElement = document.getElementById("total");

        gridElements.forEach((element) => {
          totalElement.before(element);
        });
      }
      this.calcFoodLogTotals();
    });
  }

  removeItemListener() {
    const foodLogContainer = document.querySelector(".nutrition_info");
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

    const totalCalories = document.getElementById("total_calories");
    const totalProtein = document.getElementById("total_protein");
    const totalCarbs = document.getElementById("total_carbs");
    const totalFat = document.getElementById("total_fat");

    totalCalories.textContent = calories;
    totalProtein.textContent = protein;
    totalCarbs.textContent = carbs;
    totalFat.textContent = fat;
  }

  createGraphImg(base64Graph) {
    // Create image element and set src to base64 data
    const img = document.createElement("img");
    img.src = "data:image/png;base64," + base64Graph;

    return img;
  }
}

window.nutritionManager = new NutritionManager();
