document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-row-link]").forEach((row) => {
    row.addEventListener("click", (event) => {
      if (!event.target.closest("a")) window.location.href = row.dataset.rowLink;
    });
  });

  const filterButton = document.querySelector("[data-filter-toggle]");
  const searchBox = document.querySelector(".search-box");
  if (filterButton && searchBox) {
    filterButton.addEventListener("click", () => searchBox.classList.toggle("filter-focused"));
  }
});
