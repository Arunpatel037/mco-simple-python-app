const greetingHeading = document.getElementById("greeting");
const messageInput = document.getElementById("message-input");
const statusText = document.getElementById("status");
const greetingForm = document.getElementById("greeting-form");

// Show the message in the heading and the input box.
function showGreeting(greeting) {
  greetingHeading.textContent = greeting.message;
  messageInput.value = greeting.message;
  statusText.textContent = "";
}

function showError(error) {
  statusText.textContent = error.message;
}

// Call the backend API and return the greeting it sends back.
async function callApi(method, body) {
  const response = await fetch("/api/greeting", {
    method: method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    throw new Error("Could not " + (method === "GET" ? "load" : "save") + " the message (" + response.status + ")");
  }
  return response.json();
}

greetingForm.addEventListener("submit", (event) => {
  event.preventDefault();
  callApi("PUT", { message: messageInput.value })
    .then((greeting) => {
      showGreeting(greeting);
      statusText.textContent = "Saved";
    })
    .catch(showError);
});

// Load the current message when the page opens.
callApi("GET").then(showGreeting).catch(showError);
