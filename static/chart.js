const ctx = document.getElementById("myChart");
const deckSelection = document.getElementById("deckSelection");
const deckOptions = document.getElementById("deckOptions");
const deckIDs = document.querySelectorAll(".deck-card");

const base_url = "https://brainstorm-flashcard-app.herokuapp.com";

//_ CHARTS

var results = {
  total_q: 0,
  easy_q: 0,
  medium_q: 0,
  hard_q: 0,
  score: 0,
};

var decksPresent = [];
var r = [];
var selectedDeck = -1;

const getReview = async (deck_id) => {
  const url = `${base_url}/api/review/${deck_id}`;
  const response = await fetch(url, {
    method: "GET",
    mode: "cors",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
  const res = await response.json();
  results.easy_q = res.easy_q;
  results.medium_q = res.medium_q;
  results.hard_q = res.hard_q;
  results.total_q = res.total_q;
  return res;
};

const myChart = new Chart(ctx, {
  type: "bar",
  data: {
    labels: [
      "Total Questions",
      "Easy Questions",
      "Medium Questions",
      "Hard Questions",
    ],
    datasets: [
      {
        label: "# of Questions",
        data: [
          results.total_q,
          results.easy_q,
          results.medium_q,
          results.hard_q,
        ],
        backgroundColor: [
          "rgba(255, 99, 132, 0.2)",
          "rgba(54, 162, 235, 0.2)",
          "rgba(255, 206, 86, 0.2)",
          "rgba(75, 192, 192, 0.2)",
          "rgba(153, 102, 255, 0.2)",
          "rgba(255, 159, 64, 0.2)",
        ],
        borderColor: [
          "rgba(255, 99, 132, 1)",
          "rgba(54, 162, 235, 1)",
          "rgba(255, 206, 86, 1)",
          "rgba(75, 192, 192, 1)",
          "rgba(153, 102, 255, 1)",
          "rgba(255, 159, 64, 1)",
        ],
        borderWidth: 1,
        barPercentage: 0.25,
      },
    ],
  },
  options: {
    scales: {
      y: {
        beginAtZero: true,
      },
    },
    plugins: {
      title: {
        display: true,
        text: "Distribution of # of Questions",
      },
    },
  },
});

const updateChart = (chart) => {
  const chartData = chart.data.datasets[0].data;
  chartData[0] = results.total_q;
  chartData[1] = results.easy_q;
  chartData[2] = results.medium_q;
  chartData[3] = results.hard_q;
  chart.update();
};

deckSelection.addEventListener("change", async function (e) {
  e.preventDefault();
  selectedDeck = deckSelection.value;
  if (selectedDeck !== -1) {
    const review = await getReview(selectedDeck);
    console.log(results);
    updateChart(myChart);
  }
});
