let currentLog = null;
function loadLog (){
    const navPrev = document.querySelector("#nav_prev");
    navPrev.addEventListener("click", e => {
        getCalendar("prev")
    });

    const navNext = document.querySelector("#nav_next");
    navNext.addEventListener("click", e => {
        getCalendar("next")
    });

    const logs = document.querySelectorAll(".day");
    logs.forEach(log => {
        log.addEventListener("click", e =>{
            getLog(log);
        });
    });
}

function closeDailyLog(e){
    const dailyLogPopup = document.getElementById('daily_log_popup');
    const addLogPopup = document.getElementById('add_log_popup');
    if (!dailyLogPopup.contains(e.target) && !addLogPopup.contains(e.target)){
        document.getElementById('close').click();
        document.removeEventListener('click', closeDailyLog);
        const addLogPopup = document.querySelector('#add_log_popup');
        addLogPopup.style.display = 'none';
    }
}

function showPopupDailyLog(dailyLogHTML) {
    // Create a new popup element
    const popup_content = document.getElementById('log_popup_content');
    popup_content.innerHTML = dailyLogHTML;
    const popup = document.getElementById('daily_log_popup');
    popup.style.display = 'block';

    const closePopup = document.getElementById('close');
    closePopup.addEventListener('click', e => {
        popup.style.display = 'none';
    });
}

function addSaveWorkoutListener(){
    const saveWorkoutButton = document.querySelector('#save_workout_session');
    saveWorkoutButton.addEventListener('click', e => {
        const workoutIcon = currentLog.querySelector('.workout_icon');
        if (!workoutIcon){
            currentLog.innerHTML += '<div><span class="material-symbols-outlined workout_icon">' +
                'exercise</span></div>';
        }
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
    currentLog = log;
    const monthAndYear = document.querySelector("#month_name");
    const year = monthAndYear.dataset.year;
    const month = monthAndYear.dataset.month;
    const day = log.dataset.day;

    fetch(`${year}/${month}/${day}`, {method: "GET", headers: {"X-Requested-With": "XMLHttpRequest"}})
    .then(response => response.text())
    .then(dailyLogHTML => {
        showPopupDailyLog(dailyLogHTML);
        addDailyLogPopupListeners();
        document.addEventListener('click', closeDailyLog);
    });
}

function addDailyLogPopupListeners(){
    const addWeightLogButton = document.querySelector('.add_weight_log');
    addWeightLogButton.addEventListener('click', e => {
        fetch('save_weight_log/', {method: "GET"})
        .then(response => response.text())
        .then(addWeightLogHTML => {
            showPopupAddWeightLog(addWeightLogHTML);
        });
    });

    const addWorkoutLogButton = document.querySelector('.add_workout_log');
    addWorkoutLogButton.addEventListener('click', e => {
        fetch(`http://${domain}/workout`, {method:"GET", headers: {
        "X-Requested-With": "XMLHttpRequest",
        }})
        .then(response => response.text())
        .then(addWorkoutLogHTML => {
            showPopupAddWorkoutLog(addWorkoutLogHTML);
            scriptLoaded = addScript("/static/workout/js/workout.js");
            if (scriptLoaded){
                scriptLoaded.onload = function(){
                    loadWorkout();
                    setDate();
                    addSaveWorkoutListener();
                };
            }
            else{
                loadWorkout();
                setDate();
                addSaveWorkoutListener();
            }
        });
    });
}

function setDate(){
    const monthAndYear = document.querySelector("#month_name");
    const month = parseInt(monthAndYear.dataset.month) - 1;
    const year = parseInt(monthAndYear.dataset.year);
    const day = parseInt(currentLog.dataset.day);
    document.getElementById("date").valueAsDate = new Date(year, month, day);
}

function addSaveWeightLogListener() {
    const saveWeightLogButton = document.getElementById('save_weight_log');
    saveWeightLogButton.addEventListener('click', e => {
        saveWeightLog();
    });
}


function saveWeightLog() {
    const bodyweight = document.getElementById('bodyweight').value;
    const bodyfat = document.getElementById('bodyfat').value;
    const date = document.getElementById('log_popup_date').textContent;
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const formData = new FormData();
    formData.append('bodyweight', bodyweight);
    formData.append('bodyfat', bodyfat);
    formData.append('date', date);
    formData.append('csrfmiddlewaretoken', csrftoken);

    fetch('save_weight_log/', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            document.getElementById('add_log_close').click();
            getLog(currentLog);

            const weightIcon = currentLog.querySelector('.weight_icon');
            if (!weightIcon){
                currentLog.innerHTML += '<div><span class="material-symbols-outlined weight_icon">' +
                    'monitor_weight</span></div>';
            }
        } else {
            throw new Error('Failed to save weight log');
        }
    });
}

function showPopupAddWeightLog(addWeightLogHTML) {
    const popup = document.getElementById('add_log_popup');
    popup.innerHTML = addWeightLogHTML;
    popup.style.display = 'block';

    const dailyLogDate = document.getElementById('log_popup_date').textContent;
    const weightLogHeaderText = document.getElementById('weight_log_header_text');
    weightLogHeaderText.innerHTML = `Weight Log - ` + dailyLogDate;


    const closePopup = document.getElementById('add_log_close');
    closePopup.addEventListener('click', e => {
        popup.style.display = 'none';
    });
    addSaveWeightLogListener();
}

function showPopupAddWorkoutLog(addWorkoutLogHTML) {
    const popup = document.getElementById('add_log_popup');
    popup.innerHTML = addWorkoutLogHTML;
    popup.style.display = 'block';
}
