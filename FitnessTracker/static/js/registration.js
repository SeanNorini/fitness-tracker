const measurementRadios = document.querySelectorAll(
  'input[name="system_of_measurement"]',
);

measurementRadios.forEach((radio) => {
  radio.addEventListener("change", (e) => {
    const heightLabel = document.querySelector('label[for="height"]');
    const heightInput = document.querySelector('input[name="height"]');
    const weightLabel = document.querySelector('label[for="body_weight"]');
    const weightInput = document.querySelector('input[name="body_weight"]');

    if (e.target.value === "Imperial") {
      heightLabel.textContent = heightLabel.textContent.replace(
        "(cm)",
        "(in.)",
      );
      heightInput.placeholder = "70";
      weightLabel.textContent = weightLabel.textContent.replace(
        "(kg)",
        "(lbs)",
      );
      weightInput.placeholder = "160";
    } else {
      heightLabel.textContent = heightLabel.textContent.replace(
        "(in.)",
        "(cm)",
      );
      heightInput.placeholder = "175";
      weightLabel.textContent = weightLabel.textContent.replace(
        "(lbs)",
        "(kg)",
      );
      weightInput.placeholder = "70";
    }
  });
});

function addSaveRegistrationListener() {
  document
    .getElementById("registration-form")
    .addEventListener("submit", (e) => {
      e.preventDefault();

      const formData = readRegistrationForm();
      registerUser(formData);
    });
}

function readRegistrationForm() {
  const formElements = document
    .querySelector("#registration-form")
    .querySelectorAll("input");
  const formData = new FormData();
  formElements.forEach((element) => {
    formData.append(element.name, element.value);
  });

  const gender = document.querySelector("#gender_0");
  if (gender.checked) {
    formData.set("gender", "M");
  } else {
    formData.set("gender", "F");
  }

  const systemOfMeasurement = document.querySelector(
    "#system_of_measurement_0",
  );
  if (systemOfMeasurement.checked) {
    formData.set("Imperial", "Imperial");
  } else {
    formData.set("Metric", "Metric");
  }

  // Add CSRF token
  const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  formData.append("csrfmiddlewaretoken", csrftoken);

  return formData;
}

function registerUser(formData) {
  document.body.style.cursor = "wait";
  fetch(".", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.text())
    .then((data) => {
      document.body.style.cursor = "default";
      const container = document.querySelector(".container");
      container.innerHTML = data;

      const errors = document.querySelector(".errorlist");
      if (errors) {
        addSaveRegistrationListener();
      }
    });
}

addSaveRegistrationListener();
