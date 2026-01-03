const payloadEl = document.getElementById("analytics-data");
const analyticsData = payloadEl ? JSON.parse(payloadEl.textContent) : {};

const perCategoryRaw = Array.isArray(analyticsData.per_category)
  ? analyticsData.per_category
  : [];
const transactionsRaw = Array.isArray(analyticsData.transactions)
  ? analyticsData.transactions
  : [];
const budgetsRaw = Array.isArray(analyticsData.budgets)
  ? analyticsData.budgets
  : [];

const perCategory = perCategoryRaw.map((item) => ({
  category: item.category || "Uncategorised",
  total: Number(item.total || 0),
}));

const transactions = transactionsRaw.map((tx) => ({
  ...tx,
  amount: Number(tx.amount || 0),
  category: tx.category || "Uncategorised",
  type: tx.type || "expense",
  date: tx.date || "",
}));

const budgetItems = budgetsRaw
  .map((item) => ({
    name: item?.name || item?.category || "Uncategorised",
    budget: Number(item?.budget_amount ?? item?.budget ?? 0),
  }))
  .filter((item) => Number.isFinite(item.budget) && item.budget > 0);

const budgetMap = new Map();
budgetItems.forEach((item) => {
  budgetMap.set(item.name, item.budget);
});

const spendMap = new Map();
perCategory.forEach((item) => {
  spendMap.set(item.category, item.total);
});

const totals = analyticsData.totals || {};
const summary = analyticsData.summary || {};
const incomeVsExpense = analyticsData.income_vs_expense || {};

const currencyFormatter = new Intl.NumberFormat("en-GB", {
  style: "currency",
  currency: "GBP",
  maximumFractionDigits: 2,
});

function formatMoney(value) {
  return currencyFormatter.format(Number(value || 0));
}

const savingsValue = Number(
  totals.savings ?? summary.net_balance ?? 0
);
const totalIncome = Number(
  totals.total_income ?? summary.total_income ?? incomeVsExpense.income ?? 0
);
const totalExpense = Number(
  totals.total_expense ?? summary.total_expense ?? incomeVsExpense.expense ?? 0
);

const savingsEl = document.getElementById("savingsValue");
const incomeEl = document.getElementById("incomeValue");
const expenseEl = document.getElementById("expenseValue");

if (savingsEl) {
  savingsEl.textContent = formatMoney(savingsValue);
  if (savingsValue < 0) {
    savingsEl.classList.add("negative");
  }
}
if (incomeEl) {
  incomeEl.textContent = formatMoney(totalIncome);
}
if (expenseEl) {
  expenseEl.textContent = formatMoney(totalExpense);
}

const palette = [
  "#1f3a5f",
  "#f4a261",
  "#2a9d8f",
  "#e76f51",
  "#b56576",
  "#6d597a",
  "#3a86ff",
  "#90be6d",
  "#ffb703",
  "#219ebc",
];

if (window.Chart) {
  Chart.defaults.font.family =
    '"Space Grotesk", "Trebuchet MS", sans-serif';
  Chart.defaults.color = "#2b2a28";
}

const barLabels = perCategory.map((item) => item.category);
const barValues = perCategory.map((item) => item.total);
const barColors = barLabels.map((_, index) => palette[index % palette.length]);

const barEmpty = document.getElementById("barEmpty");
const expensePieEmpty = document.getElementById("expensePieEmpty");
const lineEmpty = document.getElementById("lineEmpty");
const incomeExpenseEmpty = document.getElementById("incomeExpenseEmpty");
const budgetList = document.getElementById("budgetList");
const budgetEmpty = document.getElementById("budgetEmpty");

function toggleEmptyState(element, isVisible) {
  if (!element) return;
  if (isVisible) {
    element.classList.add("is-visible");
  } else {
    element.classList.remove("is-visible");
  }
}

function renderBudgetList() {
  if (!budgetList) return;

  budgetList.textContent = "";

  const rows = Array.from(budgetMap.entries()).map(([name, budget]) => {
    const spent = spendMap.get(name) || 0;
    const remaining = budget - spent;
    const utilization = budget > 0 ? spent / budget : 0;
    return {
      name,
      budget,
      spent,
      remaining,
      utilization,
    };
  });

  rows.sort((a, b) => b.utilization - a.utilization);
  toggleEmptyState(budgetEmpty, rows.length === 0);

  rows.forEach((row) => {
    const isOver = row.remaining < -0.01;
    const isOnBudget = Math.abs(row.remaining) <= 0.01;

    const rowEl = document.createElement("div");
    rowEl.className = `budget-row${isOver ? " is-over" : ""}`;

    const metaEl = document.createElement("div");
    metaEl.className = "budget-meta";

    const nameEl = document.createElement("span");
    nameEl.className = "budget-name";
    nameEl.textContent = row.name;

    const numbersEl = document.createElement("span");
    numbersEl.className = "budget-numbers";
    numbersEl.textContent = `${formatMoney(row.spent)} / ${formatMoney(row.budget)}`;

    metaEl.append(nameEl, numbersEl);

    const barEl = document.createElement("div");
    barEl.className = "budget-bar";

    const fillEl = document.createElement("span");
    fillEl.className = "budget-fill";
    const percent = Math.min(100, Math.max(0, row.utilization * 100));
    fillEl.style.width = `${percent}%`;

    barEl.appendChild(fillEl);

    const statusEl = document.createElement("div");
    statusEl.className = "budget-status";
    if (isOnBudget) {
      statusEl.textContent = "On budget";
    } else if (isOver) {
      statusEl.textContent = `Over by ${formatMoney(Math.abs(row.remaining))}`;
    } else {
      statusEl.textContent = `${formatMoney(row.remaining)} remaining`;
    }

    rowEl.append(metaEl, barEl, statusEl);
    budgetList.appendChild(rowEl);
  });
}

const barCtx = document.getElementById("barChart");
let barChart;
let selectedCategory = null;

if (barCtx) {
  toggleEmptyState(barEmpty, barValues.length === 0);
  barChart = new Chart(barCtx, {
    type: "bar",
    data: {
      labels: barLabels,
      datasets: [
        {
          data: barValues,
          backgroundColor: barColors,
          borderRadius: 10,
          borderSkipped: false,
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (context) =>
              `${context.label}: ${formatMoney(context.parsed.y)}`,
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
        },
        y: {
          ticks: {
            callback: (value) => formatMoney(value),
          },
        },
      },
      onClick: (_event, elements) => {
        if (!elements.length) return;
        const index = elements[0].index;
        selectedCategory = barLabels[index];
        updateCategoryLabel();
        updateLineChart();
      },
    },
  });
}

const monthSelect = document.getElementById("monthSelect");

function getMonthKey(dateString) {
  if (!dateString || dateString.length < 7) return null;
  return dateString.slice(0, 7);
}

function formatMonthLabel(monthKey) {
  const parts = monthKey.split("-");
  if (parts.length !== 2) return monthKey;
  const year = Number(parts[0]);
  const monthIndex = Number(parts[1]) - 1;
  const date = new Date(year, monthIndex, 1);
  if (Number.isNaN(date.getTime())) {
    return monthKey;
  }
  return date.toLocaleString("en-US", { month: "long", year: "numeric" });
}

const monthSet = new Set();
transactions.forEach((tx) => {
  const monthKey = getMonthKey(tx.date);
  if (monthKey) monthSet.add(monthKey);
});

const monthList = Array.from(monthSet).sort();
const fallbackMonth = new Date().toISOString().slice(0, 7);
let selectedMonth = monthList.length ? monthList[monthList.length - 1] : fallbackMonth;

if (monthSelect) {
  const monthsToShow = monthList.length ? monthList : [fallbackMonth];
  monthsToShow.forEach((monthKey) => {
    const option = document.createElement("option");
    option.value = monthKey;
    option.textContent = formatMonthLabel(monthKey);
    monthSelect.appendChild(option);
  });
  monthSelect.value = selectedMonth;
  monthSelect.addEventListener("change", (event) => {
    selectedMonth = event.target.value;
    updateLineChart();
  });
}

const categoryLabel = document.getElementById("selectedCategory");
const clearCategory = document.getElementById("clearCategory");

function updateCategoryLabel() {
  if (!categoryLabel) return;
  categoryLabel.textContent = selectedCategory || "All categories";
}

if (clearCategory) {
  clearCategory.addEventListener("click", () => {
    selectedCategory = null;
    updateCategoryLabel();
    updateLineChart();
  });
}

function buildLineSeries(monthKey, category) {
  const totalsByDay = {};
  transactions.forEach((tx) => {
    if (tx.type !== "expense") return;
    if (!tx.date || !tx.date.startsWith(monthKey)) return;
    if (category && tx.category !== category) return;
    const dayKey = tx.date.slice(0, 10);
    totalsByDay[dayKey] = (totalsByDay[dayKey] || 0) + tx.amount;
  });

  const dayKeys = Object.keys(totalsByDay).sort();
  const labels = dayKeys.map((dayKey) => {
    const date = new Date(dayKey);
    if (Number.isNaN(date.getTime())) return dayKey;
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  });
  const values = dayKeys.map((dayKey) => totalsByDay[dayKey]);

  return { labels, values };
}

const lineCtx = document.getElementById("lineChart");
let lineChart;

function updateLineChart() {
  if (!lineCtx) return;

  const series = buildLineSeries(selectedMonth, selectedCategory);
  const hasData = series.values.length > 0;
  toggleEmptyState(lineEmpty, !hasData);

  const label = selectedCategory
    ? `${selectedCategory} spend`
    : "Total spend";

  if (lineChart) {
    lineChart.data.labels = series.labels;
    lineChart.data.datasets[0].data = series.values;
    lineChart.data.datasets[0].label = label;
    lineChart.update();
    return;
  }

  const gradient = lineCtx
    .getContext("2d")
    .createLinearGradient(0, 0, 0, 280);
  gradient.addColorStop(0, "rgba(31, 58, 95, 0.35)");
  gradient.addColorStop(1, "rgba(31, 58, 95, 0.02)");

  lineChart = new Chart(lineCtx, {
    type: "line",
    data: {
      labels: series.labels,
      datasets: [
        {
          label,
          data: series.values,
          borderColor: "#1f3a5f",
          backgroundColor: gradient,
          tension: 0.35,
          fill: true,
          pointRadius: 3,
          pointBackgroundColor: "#1f3a5f",
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (context) => formatMoney(context.parsed.y),
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
        },
        y: {
          ticks: {
            callback: (value) => formatMoney(value),
          },
        },
      },
    },
  });
}

updateCategoryLabel();
updateLineChart();
renderBudgetList();

const expensePieCtx = document.getElementById("expensePie");
if (expensePieCtx) {
  toggleEmptyState(expensePieEmpty, barValues.length === 0);
  new Chart(expensePieCtx, {
    type: "pie",
    data: {
      labels: barLabels,
      datasets: [
        {
          data: barValues,
          backgroundColor: barColors,
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
        },
        tooltip: {
          callbacks: {
            label: (context) =>
              `${context.label}: ${formatMoney(context.parsed)}`,
          },
        },
      },
    },
  });
}

const incomeExpenseCtx = document.getElementById("incomeExpensePie");
if (incomeExpenseCtx) {
  const incomeExpenseValues = [totalIncome, totalExpense];
  const hasIncomeExpense = incomeExpenseValues.some((value) => value > 0);
  toggleEmptyState(incomeExpenseEmpty, !hasIncomeExpense);
  new Chart(incomeExpenseCtx, {
    type: "doughnut",
    data: {
      labels: ["Income", "Expense"],
      datasets: [
        {
          data: incomeExpenseValues,
          backgroundColor: ["#2a9d8f", "#e76f51"],
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
        },
        tooltip: {
          callbacks: {
            label: (context) =>
              `${context.label}: ${formatMoney(context.parsed)}`,
          },
        },
      },
      cutout: "55%",
    },
  });
}
