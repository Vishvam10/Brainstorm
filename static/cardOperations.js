const container = document.querySelector(".details");
const addButton = document.getElementById("addButton");
const deleteButtons = document.querySelectorAll(".deleteButton");
const inputContainer = document.getElementById("inputContainer");

const addMoreQA = document.getElementById("addMoreQA");
const QACount = document.getElementById("QACount");

let questionCounter = 2;

const deleteCard = async (card_id) => {
  const url = `http://127.0.0.1:4000/api/card`;
  const response = await fetch(url, {
    method: "DELETE",
    mode: "cors",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
    body: JSON.stringify({ card_id: card_id }),
  });
  const res = await response.json();
  return res;
};

if (addButton) {
  const renderInputs = () => {
    const markup = `
    <div class="input-group input-group-sm mb-3 d-flex justify-content-center">
      <div class="row">
        <form class="edit" method="POST">
            <div class="col-8" style="margin: 1rem 2rem 1rem 0rem;">
                <input type="text" name="q_edited" class="form-control form-control-lg"">
            </div>
            <div class="col-4">
                <input type="text" name="a_edited" class="form-control form-control-lg"">
            </div>
            <div class="col-2">
                <label for="{{card.card_id}}" class="btn btn-primary btn-lg" style="margin: 0rem 0rem 0rem 4rem; height: 4rem; width: 6rem; display: flex; align-items: center; justify-content: center">Add</label>
                <input type="submit" name="submit" class="hide" id="{{card.card_id}}" value="{{card.card_id}}">
            </div>
        </form>
      </div>
    </div>`;
    container.insertAdjacentHTML("afterend", markup);
    addButton.style.display = "none";
  };

  addButton.addEventListener("click", () => {
    renderInputs();
  });
}

if (addMoreQA) {
  const renderQAs = (questionCounter) => {
    const markup = `
      <div class="row">
        <div class="col ms-4">
          <label for="q${questionCounter}" class="mb-3">Question ${questionCounter}</label>
          <input type="text" name="q${questionCounter}" class="form-control form-control-lg" id="q${questionCounter}">
        </div>
        <div class="col">
          <label for="a${questionCounter}" class="mb-3">Answer ${questionCounter}</label>
          <input type="text" name="a${questionCounter}" class="form-control form-control-lg" id="a${questionCounter}">
        </div>
      </div>
    `;
    inputContainer.insertAdjacentHTML("beforeend", markup);
    QACount.value = questionCounter;
  };

  addMoreQA.addEventListener("click", (e) => {
    e.preventDefault();
    questionCounter++;
    renderQAs(questionCounter);
  });
}

if (deleteButtons) {
  deleteButtons.forEach((ele) => {
    ele.addEventListener("click", function (e) {
      e.preventDefault();
      deleteCard(this.value);
    });
  });
}
