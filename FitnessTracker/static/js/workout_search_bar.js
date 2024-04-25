class SearchBar_ {
  constructor(searchHandler, tabs = false) {
    this.searchHandler = searchHandler;
    this.tabs = tabs;
    this.activeTab = "all";
  }
  initialize(searchBarSelector) {
    this.searchBar = document.getElementById(searchBarSelector);
    this.searchInput = this.searchBar.querySelector("input");
    this.clearInputBtn = this.searchBar.querySelector(".clear");
    this.clearInputBtn.classList.add("vis-hidden");
    this.searchList = this.searchBar.querySelector(".search-list");
    const debouncedSearch = this.debounce(this.inputHandler, 300);
    this.searchInput.addEventListener("input", debouncedSearch);
    this.searchInput.addEventListener("focus", this.openSearchList);
    this.clearInputBtn.addEventListener("click", this.clearInput);

    if (this.tabs) {
      this.addTabListener();
    }
  }

  clearInput = (e) => {
    this.searchInput.value = "";
    this.closeSearchList(e);
    this.updateSearchList("", 0);
  };

  openSearchList = (e) => {
    this.searchList.classList.remove("hidden");
    this.clearInputBtn.classList.remove("vis-hidden");
    document.addEventListener("click", this.searchListHandler);
  };

  searchListHandler = (e) => {
    if (
      !this.searchList.contains(e.target) &&
      !this.searchBar.contains(e.target)
    ) {
      this.closeSearchList();
      return;
    }
    this.searchHandler(e);
  };

  closeSearchList = (e) => {
    this.searchList.classList.add("hidden");
    this.clearInputBtn.classList.add("vis-hidden");
    this.searchInput.removeEventListener("click", this.searchListHandler);
  };

  addTabListener() {
    const tabContainer = this.searchBar.querySelector(".tabs");
    tabContainer.addEventListener("click", (e) => {
      const tabs = tabContainer.querySelectorAll(".tab");
      tabs.forEach((tab) => {
        if (e.target === tab) {
          tab.classList.add("active");
          this.activeTab = tab.dataset.filter;
          this.updateSearchList();
        } else {
          tab.classList.remove("active");
        }
      });
    });
  }

  inputHandler = (e) => {
    const query = this.searchInput.value;
    const length = query.length;
    if (this.tabs) {
      this.updateSearchList(query, length, this.activeTab);
    } else {
      this.updateSearchList(query, length);
    }
  };

  updateSearchList(query, length) {
    const items = this.searchList.querySelectorAll("div");
    items.forEach((item) => {
      const name = item.textContent.trim();
      if (name.substring(0, length).toLowerCase() !== query.toLowerCase()) {
        item.classList.add("hidden");
      } else {
        item.classList.remove("hidden");
      }
    });
  }

  deleteItem(itemName) {
    const element = this.itemExists(itemName);
    if (element) {
      element.remove();
    }
  }

  addItem(itemName, itemClass, args = null) {
    if (!this.itemExists(itemName)) {
      const element = document.createElement("div");
      element.textContent = capitalize(itemName);
      element.classList.add(
        "row",
        "row-align-center",
        "hover",
        "border",
        "p-0_2",
        itemClass,
      );
      this.searchList.appendChild(element);
      if (args) {
        for (const key of Object.keys(args)) {
          element.dataset[key] = args[key];
        }
      }
      return true;
    }
    return false;
  }

  itemExists(itemName) {
    const items = this.searchList.querySelectorAll("div");
    for (const itemElement of items) {
      if (
        itemElement.textContent.trim().toLowerCase() === itemName.toLowerCase()
      ) {
        return itemElement;
      }
    }
    return null;
  }

  debounce(func, delay) {
    let timer;
    return function () {
      const context = this;
      const args = arguments;
      clearTimeout(timer);
      timer = setTimeout(() => {
        func.apply(context, args);
      }, delay);
    };
  }
}
