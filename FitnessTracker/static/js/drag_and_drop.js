class DragAndDrop {
  initialize(marginOffset = null) {
    this.parentContainer = document.querySelector(".drag-and-drop-container");
    this.draggableSelector = ".drag-and-drop-element";
    this.handlebarClass = "drag-and-drop-handlebar";
    this.parentContainer.addEventListener("mousedown", this.dragStart);
    this.marginOffset = marginOffset;
    this.cloneElement = null;
  }

  dragStart = (e) => {
    // Cancel if cloned element already exists
    if (this.cloneElement) {
      return;
    }
    document.body.style.userSelect = "none";

    // Get nearest draggable element
    this.dragStartElement = e.target.closest(this.draggableSelector);

    if (
      this.dragStartElement &&
      e.target.classList.contains(this.handlebarClass)
    ) {
      this.cloneStartElement();
      this.dragStartElement.firstElementChild.classList.add("dragging");

      // Get original element position
      this.offsetX =
        e.clientX - this.dragStartElement.getBoundingClientRect().left;
      this.offsetY =
        e.clientY - this.dragStartElement.getBoundingClientRect().top;

      // Get start position of element being dragged
      this.startX = e.clientX - this.offsetX + window.scrollX;
      this.startY = e.clientY - this.offsetY + window.scrollY;

      this.prevX = e.clientX;
      this.prevY = e.clientY;

      // Set dragged element to start position
      this.cloneElement.style.left = this.startX + "px";
      this.cloneElement.style.top = this.startY + "px";

      // Activate listeners for dragging
      this.addDragListeners();
    }
  };

  cloneStartElement() {
    // Clone element being dragged for visual aid
    this.cloneElement = this.dragStartElement.cloneNode(true);
    this.cloneElement.classList.add("draggable"); // Toggle class for CSS style on dragged element
    this.parentContainer.appendChild(this.cloneElement);
    if (this.marginOffset) {
      this.cloneElement.style.margin = this.marginOffset;
    }
  }

  addDragListeners() {
    document.addEventListener("mousemove", this.onMousemoveHandler);
    document.addEventListener("mouseup", this.dragEnd);

    const draggableContainers = this.parentContainer.querySelectorAll(
      this.draggableSelector,
    );
    draggableContainers.forEach((draggableContainer) => {
      draggableContainer.addEventListener("mouseenter", this.moveElements);
    });
  }

  onMousemoveHandler = (e) => {
    // Update position of visual aid
    this.cloneElement.style.left =
      e.clientX - this.offsetX + window.scrollX + "px";
    this.cloneElement.style.top =
      e.clientY - this.offsetY + window.scrollY + "px";
  };

  dragEnd = (e) => {
    // Cleanup after drag and drop
    this.removeDragListeners();
    this.dragStartElement.firstElementChild.classList.remove("dragging");
    this.cloneElement.remove();
    this.cloneElement = null;
    document.body.style.userSelect = "auto";
  };

  removeDragListeners() {
    // Cleanup all listeners except mousedown on parent container
    document.removeEventListener("mousemove", this.onMousemoveHandler);
    document.removeEventListener("mouseup", this.dragEnd);
    const draggableContainers = this.parentContainer.querySelectorAll(
      this.draggableSelector,
    );
    draggableContainers.forEach((draggableContainer) => {
      draggableContainer.removeEventListener("mouseenter", this.moveElements);
    });
  }

  moveElements = (e) => {
    // Compare prev and current Y to get movement direction
    if (this.prevY < e.clientY) {
      // Insert after if element was dragged down
      this.parentContainer.insertBefore(
        this.dragStartElement,
        e.currentTarget.nextSibling,
      );
    } else {
      // Insert before if element was dragged up
      this.parentContainer.insertBefore(this.dragStartElement, e.currentTarget);
    }

    // Update previous X and Y coords
    this.prevX = e.clientX;
    this.prevY = e.clientY;
  };
}
