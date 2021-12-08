const cardContainer = document.querySelector(".cardContainer");
const nextButton = document.getElementById("nextBtn");
const submitAll = document.getElementById("submitAll");
const showAnswer = document.getElementById("showAnswer");
const backButton = document.getElementById("back");

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const deck_id = urlParams.get("deck_id");

const base_url = "https://brainstorm-flashcard-app.herokuapp.com";

var counter = 0;
var ansButtonClicked = false;
var number_of_questions = 0;
var randomQuestions = [];
var minimum = 1;

var results = {
  total_q: 0,
  easy_q: 0,
  medium_q: 0,
  hard_q: 0,
  score: 0,
  last_reviewed: "Today",
};

const getCards = async (deck_id) => {
  const url = `${base_url}/api/card/${deck_id}`;
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
  return res;
};

const checkReview = async (deck_id) => {
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
  return res;
};

const postReview = async (deck_id) => {
  results["last_reviewed"] = new Date().toLocaleString();
  const url = `${base_url}/api/review/${deck_id}`;
  const response = await fetch(url, {
    method: "POST",
    mode: "cors",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
    body: JSON.stringify(results),
  });
};

const updateReview = async (deck_id) => {
  results["last_reviewed"] = new Date().toLocaleString();
  const url = `${base_url}/api/review/${deck_id}`;
  const response = await fetch(url, {
    method: "PUT",
    mode: "cors",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
    body: JSON.stringify(results),
  });
  const res = await response.json();
};

const renderQuestionCard = async (id) => {
  var insertedContent = document.querySelector(".qacard");
  if (insertedContent) {
    insertedContent.parentNode.removeChild(insertedContent);
  }
  const cards = await getCards(deck_id);
  const number_of_cards = cards.length;
  if (counter < number_of_cards) {
    if (counter == number_of_cards - 1) {
      nextButton.childNodes[0].textContent = "Submit";
    }
    const currentCard = cards[id];
    const markup = `
    <div class="qacard">
        <div class="q_details">
          <h2 class="fs-5 mb-2">Question No : ${counter + 1}</h4>
          <h4 class="fw-bold mb-5">${currentCard.question}</h4>
        </div>
        <div style-"font-size: 1.2rem; color: grey">How difficult is the question ?</div>
        <div class="submit_ctrl">
          <div class="row">
            <div class="col">
              <input type="radio" id="easy_q" name="difficulty" class="form-check-input" value="3">
            </div>
            <div class="col">
              <label for="easy" class="form-check-label" name="dif">Easy</label>
            </div>
          </div>
          <div class="row">
            <div class="col">
              <input type="radio" id="medium_q" name="difficulty" class="form-check-input" value="2">
            </div>
            <div class="col">
              <label for="medium" class="form-check-label" name="dif">Medium</label>
            </div>
          </div>
          <div class="row">
            <div class="col">
              <input type="radio" id="hard_q" name="difficulty" class="form-check-input" value="1">
            </div>
            <div class="col">
              <label for="hard" class="form-check-label" name="dif">Hard</label>
            </div>
          </div>
        <div class="d-flex justify-content-center align-items-center mt-5 mb-3 fw-bold fs-3" id="ans"></div>
    </div>
    `;
    cardContainer.insertAdjacentHTML("afterbegin", markup);
  } else {
    showAnswer.parentNode.removeChild(showAnswer);
    const markup = `
      <div style="position: absolute; top: 30%; left: 44%;">
        <h3 class="fs-4 fw-bold" style="margin: 0rem 0rem 0rem 5.1rem" >FINISHED ⭐</h3>
        <h5 class="fs-5" style="position: absolute; width: 22rem; margin: 2rem 0rem 2rem 0rem; top: 50%">Please submit the answers before going back to the dashboard</h5>
      </div>`;

    cardContainer.insertAdjacentHTML("afterbegin", markup);
    nextButton.parentNode.removeChild(nextButton);
    submitAll.style.display = "block";
    backButton.style.display = "block";
  }
};

const resetResults = () => {
  results["total_q"] = 0;
  results["easy_q"] = 0;
  results["medium_q"] = 0;
  results["hard_q"] = 0;
  results["score"] = 0;
  results["last_reviewed"] = "Today";
};

const updateResults = (q_type) => {
  results[q_type]++;
  results["total_q"]++;

  if (q_type === "easy_q") {
    results["score"] += 2;
  } else if (q_type === "medium_q") {
    results["score"] += 1;
  } else if (q_type === "hard_q") {
    results["score"] += 0;
  } else {
    console.log("INVALID OPTION 🔥");
  }
};

const getTotalQuestions = async (deck_id) => {
  const cards = await getCards(deck_id);
  return cards.length;
};

//- Random Question Generator

number_of_questions = await getTotalQuestions(deck_id);
var nums = [];

for (let i = 0; i < number_of_questions; i++) {
  nums.push(i);
}

let i = number_of_questions;
let j = 0;

while (i--) {
  j = Math.floor(Math.random() * (i + 1));
  randomQuestions.push(nums[j]);
  nums.splice(j, 1);
}

// console.log(randomQuestions);

showAnswer.addEventListener("click", async () => {
  const ans = document.getElementById("ans");
  // To show the answer only once
  if (ans.childNodes.length == 0) {
    const cards = await getCards(deck_id);
    const currentCardAnswer = cards[counter].answer;
    ans.insertAdjacentHTML("afterbegin", currentCardAnswer);
  }
});

nextButton.addEventListener("click", () => {
  const checkedOption = document.querySelector(
    'input[name="difficulty"]:checked'
  );
  const q_type = checkedOption.id;
  updateResults(q_type);
  counter++;
  renderQuestionCard(randomQuestions[counter]);
});

submitAll.addEventListener("click", async () => {
  const res = results;
  const check = await checkReview(deck_id);
  if (check) {
    updateReview(deck_id, results);
  } else {
    postReview(deck_id, results);
  }
  submitAll.parentNode.removeChild(submitAll);
});

resetResults();
renderQuestionCard(0);
