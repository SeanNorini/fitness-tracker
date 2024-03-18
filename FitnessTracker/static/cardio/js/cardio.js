class CardioManager {
  constructor() {
    this.baseURL = `${pageManager.baseURL}/cardio/`;
  }

  initialize() {
    console.log("tests");
    pageManager
      .fetchData({
        url: `${this.baseURL}`,
        method: "GET",
        responseType: "text",
      })
      .then((contentHTML) => {
        console.log(this.baseURL);
        pageManager.updateContent(contentHTML, "content");
      });
  }
}

window.cardioManager = new CardioManager();
