function selectRole(role) {
  document.getElementById("ctaRole").value = role;
  document.getElementById("start").scrollIntoView({ behavior: "smooth" });
  document.getElementById("ctaEmail").focus();
}

document.getElementById("ctaForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("ctaEmail").value;
  const role = document.getElementById("ctaRole").value;
  const msg = document.getElementById("ctaMsg");

  msg.textContent = "Registrando...";
  try {
    const res = await fetch("/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, role }),
    });
    const data = await res.json();
    msg.textContent = `✅ ${data.message} — te contactaremos a ${email}`;
    e.target.reset();
  } catch {
    msg.textContent = "❌ Error al registrar. Inténtalo de nuevo.";
  }
});

// Scroll reveal
const observer = new IntersectionObserver(
  (entries) => entries.forEach((e) => e.isIntersecting && e.target.classList.add("visible")),
  { threshold: 0.12 }
);
document.querySelectorAll(".role-card, .step, .stat-card").forEach((el) => {
  el.style.opacity = "0";
  el.style.transform = "translateY(24px)";
  el.style.transition = "opacity .5s ease, transform .5s ease";
  observer.observe(el);
});
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".visible").forEach((el) => {
    el.style.opacity = "1";
    el.style.transform = "translateY(0)";
  });
});

// Patch observer to apply styles
const originalObserve = observer.observe.bind(observer);
const style = document.createElement("style");
style.textContent = ".visible { opacity: 1 !important; transform: translateY(0) !important; }";
document.head.appendChild(style);
