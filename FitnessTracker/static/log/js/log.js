function loadLog (){
    const navPrev = document.querySelector("#nav_prev");
    navPrev.addEventListener("click", e => {
        getCalendar("prev")
    });

    const navNext = document.querySelector("#nav_next");
    navNext.addEventListener("click", e => {
        getCalendar("next")
    });

    const logs = document.querySelectorAll(".log");
    logs.forEach(log => {
        log.addEventListener("click", e =>{
            getLog(log);
        });
    });
}

function getCalendar(calendarNav) {
    const monthAndYear = document.querySelector("#month_name");
    let month = parseInt(monthAndYear.dataset.month);
    let year = parseInt(monthAndYear.dataset.year);
    if (calendarNav === "prev"){
        month--;
        if (month === 0){
            month = 12;
            year--;
        }
    } else {
        month++;
        if (month === 12){
            month = 1;
            year++;
        }

    }

    fetch(`${year}/${month}/`, {method: "GET", headers: {"X-Requested-With": "XMLHttpRequest"}})
    .then(response => response.text())
    .then(calendarHTML => {
        const content = document.querySelector("#content");
        content.innerHTML = calendarHTML;
        loadLog();
    });

}

function getLog(log){
    const monthAndYear = document.querySelector("#month_name");
    const year = monthAndYear.dataset.year;
    const month = monthAndYear.dataset.month;
    const day = log.dataset.day;

    fetch(`${year}/${month}/${day}`, {method: "GET", headers: {"X-Requested-With": "XMLHttpRequest"}})
    .then(response => response.text())
    .then(dailyLogHTML => {
        showPopupDailyLog(dailyLogHTML);
    });
}

function showPopupDailyLog(dailyLogHTML) {
    // Create a new popup element
    const popup_content = document.getElementById('log_popup_content');
    popup_content.innerHTML = dailyLogHTML;
    const popup = document.getElementById('log_popup');
    popup.style.display = 'block';

    const closePopup = document.getElementById('close');
    closePopup.addEventListener("click", e => {
        popup.style.display = 'none';
    });
}