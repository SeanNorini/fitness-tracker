const measurementRadios = document.querySelectorAll(
  'input[name="unit_of_measurement"]',
);
measurementRadios.forEach((radio) => {
  radio.addEventListener("change", (e) => {
    const heightLabel = document.querySelector('label[for="height"]');
    const heightInput = document.querySelector('input[name="height"]');
    const weightLabel = document.querySelector('label[for="weight"]');
    const weightInput = document.querySelector('input[name="weight"]');

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
document.getElementById("registration-form").addEventListener("submit", (e) => {
  e.preventDefault();
  // Pull data from form
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
  // Add CSRF token
  const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  formData.append("csrfmiddlewaretoken", csrftoken);

  document.body.style.cursor = "wait";

  // Send form, redirect to index on success otherwise display error.
  fetch(".", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.text())
    .then((data) => {
      document.body.style.cursor = "default";
      const container = document.querySelector(".container");
      container.innerHTML = data;
    });
});
