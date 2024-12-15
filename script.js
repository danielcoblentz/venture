const search = document.querySelector(".search-wrapper");
const input = search.querySelector("input");

// expand search bar on hover
search.addEventListener("mouseenter", () => {
  if (!input.matches(":focus")) {
    search.classList.add("active");
  }
});

// close search bar when mouse leaves (if not focused or empty)
search.addEventListener("mouseleave", () => {
  if (!input.matches(":focus") && !input.value.trim()) {
    search.classList.remove("active");
  }
});

// keep expanded state when input is focused
input.addEventListener("focus", () => {
  search.classList.add("active");
});

// close when focus is lost, also input is empty
input.addEventListener("blur", () => {
  if (!input.value.trim()) {
    search.classList.remove("active");
  }
});
