// ============================
// DOM ELEMENTS
// ============================
const genreInput = document.getElementById("genre");
const descriptionInput = document.getElementById("description");
const yearInput = document.getElementById("year");
const btnRecommend = document.getElementById("btn-recommend");
const recommendationsDiv = document.getElementById("recommendations");

const API_URL = "http://127.0.0.1:5000";

// ============================
// RENDER RECOMMENDATIONS
// ============================
function renderRecommendations(movies) {
  recommendationsDiv.innerHTML = "";

  if (!movies || movies.length === 0) {
    recommendationsDiv.innerHTML = "<p>No recommendations found. Try different inputs.</p>";
    return;
  }

  movies.forEach(movie => {
    const card = document.createElement("div");
    card.className = "recommendation-card";

    // Movie info
    const content = document.createElement("div");
    content.className = "content";

    const title = document.createElement("h4");
    title.textContent = movie.title;

    const genre = document.createElement("p");
    genre.innerHTML = `<b>Genres:</b> ${movie.genres || "N/A"}`;

    const desc = document.createElement("p");
    desc.textContent = movie.description || "No description available.";

    const year = document.createElement("p");
    year.innerHTML = `<b>Year:</b> ${movie.year || "Unknown"}`;

    const sim = document.createElement("p");
    sim.innerHTML = `<b>Similarity Score:</b> ${movie.similarity ?? ""}`;

    content.append(title, genre, desc, year, sim);
    card.appendChild(content);
    recommendationsDiv.appendChild(card);
  });
}

// ============================
// RECOMMEND MOVIES (API CALL)
// ============================
btnRecommend.addEventListener("click", async () => {
  const genre = genreInput.value.trim();
  const description = descriptionInput.value.trim();
  const year = yearInput.value.trim();

  if (!genre && !description && !year) {
    alert("Please enter at least one field (genre, description, or year).");
    return;
  }

  recommendationsDiv.innerHTML = "<p>Loading recommendations...</p>";

  try {
    const response = await fetch(`${API_URL}/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ genre, description, year })
    });

    const data = await response.json();

    if (response.ok) {
      renderRecommendations(data);
    } else {
      recommendationsDiv.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
    }
  } catch (err) {
    recommendationsDiv.innerHTML = `<p style="color:red;">Error connecting to server.</p>`;
    console.error(err);
  }
});