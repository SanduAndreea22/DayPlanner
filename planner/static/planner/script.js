document.addEventListener("DOMContentLoaded", () => {

  /* ===========================
     🌿 DATA SOURCE (SAFE)
  =========================== */

  const moodEl = document.querySelector(".closed-box[data-mood]");
  const energyEl = document.querySelector(".closed-box[data-energy]");
  const isClosed = document.body.dataset.dayClosed === "true";

  if (!moodEl && !energyEl && !isClosed) return;


  /* ===========================
     💭 RECOMMENDATIONS POOL
  =========================== */

  const recommendations = {
    very_bad: [
      "Poate azi nu e despre a face, ci despre a rămâne.",
      "Respiră adânc. Doar asta este suficient acum.",
      "E ok să iei o pauză. Valoarea ta nu scade."
    ],
    bad: [
      "Alege un lucru mic și blând pentru tine.",
      "Poate corpul tău cere pauză.",
      "Nu trebuie să rezolvi tot azi."
    ],
    neutral: [
      "Dacă ai puțină energie, folosește-o fără presiune.",
      "Observă cum ești, fără să schimbi nimic.",
      "E ok să lași ziua să fie simplă."
    ],
    good: [
      "Poate e un moment bun pentru ceva creativ.",
      "Profită de ritmul tău, nu-l forța.",
      "Ceva mic azi poate conta mult."
    ],
    very_good: [
      "Ai energie – dar nu uita blândețea.",
      "Poți face, dar nu trebuie să faci tot.",
      "Bucură-te de starea asta."
    ],
    low_energy: [
      "Energia e limitată — alege cu grijă unde o pui.",
      "Uneori odihna este progres.",
      "Nu e lene. E autoreglare."
    ],
    closed_day: [
      "Ziua e închisă. Las-o să rămână așa.",
      "Ai făcut suficient azi.",
      "Poți merge mai departe, fără să te uiți înapoi."
    ]
  };


  /* ===========================
     🎲 PICK BLÂND
  =========================== */

  function pick(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
  }


  /* ===========================
     🧠 LOGIC
  =========================== */

  let message = null;

  if (isClosed) {
    message = pick(recommendations.closed_day);
  } else if (moodEl) {
    const mood = moodEl.dataset.mood;
    message = recommendations[mood]
      ? pick(recommendations[mood])
      : null;
  }

  if (!message && energyEl) {
    message = pick(recommendations.low_energy);
  }

  if (!message) return;


  /* ===========================
     🌸 RENDER
  =========================== */

  const card = document.querySelector(".day-card");
  if (!card) return;

  const box = document.createElement("div");
  box.className = "gentle-recommendation";
  box.innerHTML = `
    <span class="emoji">🌿</span>
    <span class="text">${message}</span>
  `;

  card.appendChild(box);


  /* ===========================
     ✨ ENTER ANIMATION
  =========================== */

  requestAnimationFrame(() => {
    box.style.opacity = 1;
    box.style.transform = "translateY(0)";
  });

});




