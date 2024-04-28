class SearchBar {
  constructor(inputHandler, minLengthQuery = 3, tabs = false) {
    // this.inputHandler = inputHandler;
    this.minLengthQuery = minLengthQuery;
    this.tabs = tabs;
    this.activeTab = "all";
  }
  initialize() {
    this.searchBar = document.querySelector(".search-bar");
    this.searchInput = this.searchBar.querySelector("input");
    this.clearSearchBtn = this.searchBar.querySelector(".delete-search");
    this.searchResultList = document.querySelector("#items");
    const debouncedSearch = debounce(this.inputHandler, 300);
    this.searchInput.addEventListener("input", debouncedSearch);
    this.clearSearchBtn.addEventListener("click", (e) => {
      this.searchInput.value = "";
      this.searchResultList.innerHTML = "";
      const searchResultContainer = document.getElementById("item-details");
      searchResultContainer.classList.add("hidden");
    });

    const debouncedItemDetails = debounce(this.fetchItemDetails, 300);
    const itemList = document.getElementById("items");
    itemList.addEventListener("click", debouncedItemDetails);
    if (this.tabs) {
      this.addTabListener();
    }
  }

  addTabListener() {
    const tabContainer = document.querySelector("#tabs");
    tabContainer.addEventListener("click", (e) => {
      const tabs = tabContainer.querySelectorAll(".tab");
      tabs.forEach((tab) => {
        if (e.target === tab) {
          tab.classList.add("active");
          this.activeTab = tab.dataset.filter;
          this.updateSearchResultsList();
        } else {
          tab.classList.remove("active");
        }
      });
    });
  }

  inputHandler = (e) => {
    const query = this.searchInput.value;
    if (query.length >= this.minLengthQuery) {
      this.fetchSearchRequest(query);
      const searchResultContainer = document.getElementById("item-details");
      searchResultContainer.classList.remove("hidden");
    }
  };

  fetchSearchRequest(query) {
    pageManager
      .fetchData({
        url: `${pageManager.baseURL}/nutrition/get_search_results/${query}`,
        method: "GET",
        responseType: "json",
      })
      .then((response) => {
        this.searchResults = response;
        this.updateSearchResultsList();
      });
  }

  updateSearchResultsList() {
    this.searchResultList.innerHTML = "";

    if (this.activeTab === "all") {
      for (const key in this.searchResults) {
        this.filterSearchResults(key);
      }
    } else if (this.activeTab === "common") {
      this.filterSearchResults("common");
    } else if (this.activeTab === "branded") {
      this.filterSearchResults("branded");
    }
  }

  filterSearchResults(key) {
    if (!this.searchResults) {
      return;
    }

    this.searchResults[key].forEach((result) => {
      const resultContainer = document.createElement("div");
      resultContainer.classList.add(
        "row",
        "row-align-center",
        "px-1",
        "radius",
        "item",
      );

      const itemImg = document.createElement("img");
      itemImg.src = result["photo"]["thumb"];
      itemImg.style.maxHeight = "2rem";

      const contentContainer = document.createElement("div");
      contentContainer.classList.add("col");

      const resultItem = document.createElement("div");
      resultItem.textContent = result["food_name"]
        .split(" ")
        .map((word) => word[0].toUpperCase() + word.slice(1))
        .join(" ");
      contentContainer.appendChild(resultItem);

      if (key === "branded") {
        const brandContainer = document.createElement("div");
        brandContainer.classList.add(
          "row",
          "row-align-center",
          "row-justify-space-between",
          "full-width",
        );

        const resultBrand = document.createElement("div");
        resultBrand.classList.add("brand-name", "text-sm", "text-secondary");
        resultBrand.textContent = result["brand_name"];

        const resultCalories = document.createElement("div");
        resultCalories.classList.add("brand-calories", "text-green", "text-sm");
        resultCalories.textContent = result["nf_calories"] + " cal";

        brandContainer.appendChild(resultBrand);
        brandContainer.appendChild(resultCalories);
        contentContainer.appendChild(brandContainer);
        resultContainer.dataset.type = "branded";
        resultContainer.dataset.id = result["nix_item_id"];
      } else {
        resultContainer.dataset.type = "common";
        resultContainer.dataset.id = result["food_name"];
      }

      resultContainer.appendChild(itemImg);
      resultContainer.appendChild(contentContainer);

      this.searchResultList.appendChild(resultContainer);
    });
  }

  fetchItemDetails = (e) => {
    const item = e.target.closest(".item");
    if (!item) {
      return;
    }

    let url = "";
    if (item.dataset.type === "common") {
      url = `${pageManager.baseURL}/nutrition/get_item_details/common/${item.dataset.id}`;
    } else if (item.dataset.type === "branded") {
      url = `${pageManager.baseURL}/nutrition/get_item_details/branded/${item.dataset.id}`;
    }

    pageManager
      .fetchData({
        url: url,
        method: "GET",
        responseType: "json",
      })
      .then((response) => {
        this.itemDetails = response["foods"][0];
        this.populateFoodDetails(response["foods"][0]);
      });
  };

  populateFoodDetails(food) {
    const imgContainer = document.getElementById("detail-img");
    const imgElement = document.createElement("img");
    if (food["photo"]["highres"] === null) {
      imgContainer.innerHTML = "No Image";
    } else {
      imgElement.src = food["photo"]["highres"];
      imgElement.style.maxWidth = "10rem";
      imgElement.style.maxHeight = "10rem";
      imgContainer.innerHTML = "";
      imgContainer.appendChild(imgElement);
    }

    const nameContainer = document.getElementById("detail-name");
    nameContainer.textContent = food["food_name"]
      .split(" ")
      .map((word) => word[0].toUpperCase() + word.slice(1))
      .join(" ");

    const servingsContainer = document.getElementById("detail-servings");
    servingsContainer.textContent = `${food["serving_qty"]} ${food["serving_unit"]}`;

    const caloriesContainer = document.getElementById("detail-calories");
    caloriesContainer.textContent = food["nf_calories"];

    const proteinContainer = document.getElementById("detail-protein");
    proteinContainer.textContent = food["nf_protein"];

    const carbsContainer = document.getElementById("detail-carbs");
    carbsContainer.textContent = food["nf_total_carbohydrate"];

    const fatContainer = document.getElementById("detail-fat");
    fatContainer.textContent = food["nf_total_fat"];
  }
}
