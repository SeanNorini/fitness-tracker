class Spinner {
  constructor(options) {
    this.type = options.type ?? "range";
    this.id = options.id ?? 0;
    this.elements = Array.from(
      document.querySelectorAll("[data-id='" + this.id + "']"),
    );
    this.noWrap = options.noWrap ? options.noWrap : false;
    this.inputElementIndex = options.inputIndex ? options.inputIndex : 0;
    this.inputElement = this.elements[this.inputElementIndex];
    this.moveThreshold = options.moveThreshold ?? 2 * pageManager.rootFontSize;
    this.leadingZeroes = options.leadingZeroes
      ? options.leadingZeroes[0]
      : false;
    this.numberLength = options.leadingZeroes ? options.leadingZeroes[1] : 0;
    this.animate = options.animate ?? true;
    this.spinning = false;
    this.initialized = false;
    this.styles = this.getDefaultStyles(options.styles);
    this.initialize(options);
  }

  getDefaultStyles(styles) {
    if (styles) {
      return styles;
    }

    const defaultStyles = {
      all: { color: "#8f8f8f" },
      input: { color: "#f5f5f5" },
    };

    return defaultStyles;
  }

  initialize(options) {
    this.setValueRange(options.valueRange);

    if (this.type === "range") {
      this.setRangeStartValue(options.inputStartValue);
    } else if (this.type === "list") {
      this.setListStartIndex(options.inputStartValue - 1);
    } else if (this.type === "date") {
      this.startDate = new Date();
      this.startDate.setDate(this.startDate.getDate() - this.inputElementIndex);
    }
    this.update(0);

    this.setElementStyles();

    this.initialized = true;
  }

  getDate() {
    const inputDate = new Date(this.startDate);
    inputDate.setDate(inputDate.getDate() + this.inputElementIndex);

    const currentYear = new Date().getFullYear();
    return inputDate.toLocaleDateString("en-us", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: inputDate.getFullYear() <= currentYear ? "numeric" : undefined,
    });
  }

  getPythonDate() {
    const inputDate = new Date(this.startDate);
    inputDate.setDate(inputDate.getDate() + this.inputElementIndex);

    let year = inputDate.getFullYear();
    let month = String(inputDate.getMonth() + 1).padStart(2, "0"); // Add 1 to month because it's zero-based
    let day = String(inputDate.getDate()).padStart(2, "0");

    // Format the date as "YYYY-MM-DD"
    return year + "-" + month + "-" + day;
  }

  setValueRange(valueRange) {
    if (this.type === "list") {
      this.minValue = valueRange[0];
      this.maxValue = valueRange[valueRange.length - 1];
      this.valueRange = valueRange;
    } else if (this.type === "range") {
      this.minValue = valueRange[0];
      this.maxValue = valueRange[1];
      this.increment = valueRange?.[2] ?? 1;
    } else if (this.type === "date") {
      this.maxDate = new Date();
      this.maxValue = valueRange?.[1] ?? this.maxDate;
      this.minDate = new Date();
      this.minValue = this.minDate.setFullYear(this.minDate.getFullYear() - 5);
      this.minValue = valueRange?.[0] ?? this.minDate;
      this.increment = valueRange?.[2] ?? 1;
    }
  }

  setElementStyles() {
    this.elements.forEach((element, index) => {
      if (
        !("input" in this.styles) ||
        element !== this.elements[this.inputElementIndex]
      ) {
        this.addElementStyles(element, this.styles.all);
      } else {
        this.addElementStyles(element, this.styles.input);
      }
      if (index !== this.inputElementIndex) {
        element.readOnly = true;
      }
    });
  }

  addElementStyles(element, styles) {
    for (const styleType in styles) {
      element.style[styleType] = styles[styleType];
    }
  }

  setRangeStartValue(inputStartValue = this.minValue) {
    let startValue =
      inputStartValue -
      this.increment * this.inputElementIndex -
      this.increment;

    if (startValue < this.minValue) {
      let numberOfIncrements = (this.minValue - startValue) / this.increment;
      numberOfIncrements %= this.elements.length;
      startValue = this.maxValue - (numberOfIncrements - 1) * this.increment;
    }

    this.elements[0].value = startValue;
  }

  setListStartIndex(inputStartValue = this.minValue) {
    this.startIndex =
      this.valueRange.indexOf(inputStartValue) - this.inputElementIndex;
  }

  update(mouseDelta) {
    if (this.type === "range") {
      this.updateRangeSpinner(mouseDelta);
    } else if (this.type === "list") {
      this.updateListSpinner(mouseDelta);
    } else if (this.type === "date") {
      this.updateDateSpinner(mouseDelta);
    }
    this.triggerInputChange(this.inputElement);
  }

  updateDateSpinner(mouseDelta) {
    this.startDate.setDate(this.startDate.getDate() + mouseDelta);
    for (let i = 0; i < this.elements.length; i++) {
      let dateValue = new Date(this.startDate);
      dateValue.setDate(dateValue.getDate() + i);

      let outOfRange = null;
      if (this.noWrap) {
        if (dateValue < this.minValue || dateValue > this.maxValue) {
          outOfRange = true;
        }
      } else {
        if (dateValue < this.minValue) {
          dateValue = new Date(this.maxValue);
        }
        if (dateValue > this.maxValue) {
          dateValue = new Date(this.minValue);
        }
      }

      if (outOfRange) {
        this.elements[i].value = "";
      } else {
        this.elements[i].value = dateValue.toLocaleDateString("en-US", {
          weekday: "short",
          month: "short",
          day: "numeric",
        });
      }
    }
  }

  updateRangeSpinner(mouseDelta) {
    let startValue = parseFloat(this.elements[0].value);
    if (mouseDelta < 0) {
      startValue -= 2 * this.increment;
    }

    this.elements.forEach((element) => {
      let nextValue = this.getNextRangeValue(startValue);
      startValue = nextValue;

      if (this.noWrap) {
        this.noWrapRangeHandler(nextValue, element);
      }
      if (this.leadingZeroes) {
        nextValue = this.addLeadingZeroes(nextValue);
      }

      element.value = nextValue;
    });
  }

  addLeadingZeroes(value) {
    return value.toString().padStart(this.numberLength, "0");
  }

  noWrapRangeHandler(nextValue, element) {
    if (nextValue < this.minValue || nextValue > this.maxValue) {
      element.style.visibility = "hidden";
    } else {
      element.style.visibility = "visible";
    }
  }

  updateListSpinner(mouseDelta) {
    this.setListStartIndex(this.inputElement.value);
    for (let i = 0; i < this.elements.length; i++) {
      let nextIndex = this.startIndex + mouseDelta + i;

      if (this.noWrap) {
        this.noWrapListHandler(nextIndex, this.elements[i]);
      } else {
        if (nextIndex > this.valueRange.length - 1) {
          nextIndex -= this.valueRange.length;
        } else if (nextIndex < 0) {
          nextIndex += this.valueRange.length;
        }
        this.elements[i].value = this.valueRange[nextIndex];
      }
    }
  }

  noWrapListHandler(nextIndex, element) {
    if (nextIndex < 0 || nextIndex > this.valueRange.length - 1) {
      element.style.opacity = "0";
    } else {
      element.value = this.valueRange[nextIndex];
      element.style.removeProperty("opacity");
    }
  }

  getNextRangeValue(currValue) {
    let nextValue = currValue + this.increment;
    if (nextValue < this.minValue) {
      nextValue = this.maxValue;
    }
    if (nextValue > this.maxValue) {
      nextValue = this.minValue;
    }
    return nextValue;
  }

  animateMousemoveSpin(deltaY) {
    if (this.animate) {
      this.elements.forEach((element) => {
        element.style.transform = `translateY(${-deltaY}px)`;
      });
    }
  }

  stopAnimation() {
    if (this.animate) {
      this.elements.forEach((element) => {
        element.style.transform = `translateY(0)`;
      });
    }
  }

  atSpinEnd(mouseDelta) {
    let inputElementValue = this.inputElement.value;

    if (this.type === "range") {
      inputElementValue = parseFloat(inputElementValue);
    }
    if (this.type === "date") {
      return this.atSpinEndDateHandler(inputElementValue, mouseDelta);
    }

    return (
      (inputElementValue === this.minValue && mouseDelta < 0) ||
      (inputElementValue === this.maxValue && mouseDelta > 0)
    );
  }

  atSpinEndDateHandler(inputElementValue, mouseDelta) {
    inputElementValue = new Date(this.startDate);
    inputElementValue.setDate(
      inputElementValue.getDate() + this.inputElementIndex,
    );
    inputElementValue = inputElementValue.getTime();

    return (
      (inputElementValue === this.minValue.getTime() && mouseDelta < 0) ||
      (inputElementValue === this.maxValue.getTime() && mouseDelta > 0)
    );
  }

  triggerInputChange(element) {
    const event = new Event("input", {
      bubbles: true, // Ensure the event bubbles up the DOM tree
      cancelable: true, // Allow the event to be canceled if needed
    });
    element.dispatchEvent(event); // Dispatch the custom input event
  }
}
class InputSpinner {
  constructor(spinnerClass = "spinner") {
    this.spinnerClass = spinnerClass;
    this.spinners = {};
    this.currSpinner = null;
    this.prevY = null;
    this.deltaY = 0;
    this.mouseDelta = 0;
  }

  createSpinner(options) {
    this.spinners[options.id] = new Spinner(options);
    this.currSpinner = this.spinners[options.id];
  }

  new(options) {
    this.createSpinner(options);
    this.addMouseListeners("mousedown", this.mousedownHandler);
    this.addMouseListeners("wheel", this.mousewheelHandler);
    this.addMouseListeners("contextmenu", this.contextmenuHandler);
  }

  timePreset(startID = 0) {
    this.now = new Date();
    this.now.setMinutes(this.now.getMinutes() - 30);
    this.hours = this.now.getHours();
    this.minutes = this.now.getMinutes();
    const timeSpinners = [
      {
        id: startID,
        valueRange: [1, 12],
        inputIndex: 1,
        inputStartValue: this.hours % 12 || 12,
      },
      {
        id: startID + 1,
        valueRange: [0, 59],
        inputIndex: 1,
        leadingZeroes: [true, 2],
        inputStartValue: this.minutes,
      },
      {
        id: startID + 2,
        type: "list",
        valueRange: ["AM", "PM"],
        noWrap: true,
        inputIndex: 1,
        inputStartValue: this.hours > 12 ? "PM" : "AM",
      },
    ];

    timeSpinners.forEach((spinner) => {
      this.new(spinner);
    });
  }

  durationPreset(startID = 0) {
    const durationSpinners = [
      {
        id: startID,
        valueRange: [0, 24],
        inputStartValue: 0,
        inputIndex: 1,
        leadingZeroes: [true, 2],
      },
      {
        id: startID + 1,
        valueRange: [0, 59],
        inputStartValue: 30,
        inputIndex: 1,
        leadingZeroes: [true, 2],
      },
      {
        id: startID + 2,
        valueRange: [0, 59],
        inputStartValue: 0,
        inputIndex: 1,
        leadingZeroes: [true, 2],
      },
    ];
    durationSpinners.forEach((spinner) => {
      this.new(spinner);
    });
  }

  addMouseListeners(listenerType, handler) {
    this.currSpinner.elements.forEach((element) => {
      element.addEventListener(listenerType, handler);
    });
  }

  mousewheelHandler = (e) => {
    e.preventDefault();
    const currentTarget = document.elementFromPoint(e.clientX, e.clientY);
    if (currentTarget.classList.contains(this.spinnerClass)) {
      this.currSpinner = this.spinners[currentTarget.dataset.id];
      this.updateMouseDelta(e);

      if (this.shouldSpin()) {
        this.currSpinner.update(this.mouseDelta);
      }
      this.mouseDelta = 0;
    }
  };

  mousedownHandler = (e) => {
    this.currSpinner = this.spinners[e.target.dataset.id];
    if (this.currSpinner.spinning === true) {
      return;
    }
    this.currSpinner.spinning = true;

    this.prevY = e.clientY;
    document.body.classList.add("grabbing");

    document.addEventListener("mousemove", this.mousemoveHandler);
    document.addEventListener(
      "mouseup",
      (e) => {
        this.cleanUp();
      },
      { once: true },
    );
  };

  contextmenuHandler = (e) => {
    e.preventDefault();
  };

  mousemoveHandler = (e) => {
    this.updateMouseDelta(e);
    this.currSpinner.animateMousemoveSpin(this.deltaY);
    if (this.shouldSpin()) {
      this.currSpinner.update(this.mouseDelta);
    }
  };

  shouldSpin() {
    // Check if mouse movement met spin threshold
    if (this.mouseDelta === 0) {
      return false;
    }

    // Check if no wrap spinner is already at one end
    if (this.currSpinner.noWrap) {
      return !this.currSpinner.atSpinEnd(this.mouseDelta);
    }

    return true;
  }

  updateMouseDelta = (e) => {
    if (e.type === "wheel") {
      // Check for mousewheel up/down
      this.mouseDelta = e.deltaY > 0 ? -1 : 1;
    } else {
      this.deltaY += this.prevY - e.clientY;

      // Check mouse movement against move threshold
      this.mouseDelta =
        this.deltaY > 0
          ? Math.floor(this.deltaY / this.currSpinner.moveThreshold)
          : Math.ceil(this.deltaY / this.currSpinner.moveThreshold);

      this.deltaY %= this.currSpinner.moveThreshold; // Keep remaining change until mouseup
      this.prevY = e.clientY;
    }
  };

  cleanUp() {
    document.removeEventListener("mousemove", this.mousemoveHandler);
    document.body.classList.remove("grabbing");
    this.currSpinner.stopAnimation();
    this.currSpinner.spinning = false;

    this.updateSpinnerAtEnd();
  }

  updateSpinnerAtEnd() {
    if (this.deltaY / this.currSpinner.moveThreshold >= 0.4) {
      this.mouseDelta = 1;
    } else if (this.deltaY / this.currSpinner.moveThreshold <= -0.4) {
      this.mouseDelta = -1;
    }
    if (this.mouseDelta !== 0 && !this.currSpinner.atSpinEnd(this.mouseDelta)) {
      this.currSpinner.update(this.mouseDelta);
    }
    this.deltaY = 0;
    this.mouseDelta = 0;
  }
}
