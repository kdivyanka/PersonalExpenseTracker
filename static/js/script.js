/* script.js - Small helpers: delete confirmation and Chart.js charts. */

document.addEventListener("DOMContentLoaded", function () {
  setupDeleteConfirmation();
  setupCharts();
});

// Ask "Are you sure?" before a transaction is deleted.
function setupDeleteConfirmation() {
  document.querySelectorAll(".js-delete-form").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      var title = form.dataset.title || "this transaction";
      if (!window.confirm('Delete "' + title + '"? This cannot be undone.')) {
        event.preventDefault();
      }
    });
  });
}

var CHART_COLORS = ["#6b8fd6", "#5aae8c", "#b3a6e6", "#8fb8e8", "#9ad1b8", "#d4a5c9", "#e3c27a", "#a8adc4"];

function setupCharts() {
  if (typeof Chart === "undefined") { return; }   // Chart.js did not load (no internet)

  var categoryCanvas = document.getElementById("category-chart");
  if (categoryCanvas) {
    new Chart(categoryCanvas, {
      type: "doughnut",
      data: {
        labels: JSON.parse(categoryCanvas.dataset.labels),
        datasets: [{ data: JSON.parse(categoryCanvas.dataset.values), backgroundColor: CHART_COLORS, borderWidth: 2, borderColor: "#ffffff" }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } }
    });
  }

  var barCanvas = document.getElementById("income-expense-chart");
  if (barCanvas) {
    new Chart(barCanvas, {
      type: "bar",
      data: {
        labels: JSON.parse(barCanvas.dataset.labels),
        datasets: [
          { label: "Income", data: JSON.parse(barCanvas.dataset.income), backgroundColor: "#5aae8c", borderRadius: 6 },
          { label: "Expenses", data: JSON.parse(barCanvas.dataset.expenses), backgroundColor: "#b3a6e6", borderRadius: 6 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: true } },
        plugins: { legend: { position: "bottom" } }
      }
    });
  }
}
