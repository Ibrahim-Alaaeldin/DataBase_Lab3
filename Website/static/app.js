// Browser-side checks (the server repeats the same rules).
const val = (f, n) => (f.elements[n] ? f.elements[n].value : "");
const RULES = {
  register(f) {
    const e = [], p = val(f, "password"), c = val(f, "confirm_password");
    if (!val(f, "name").trim()) e.push("Name is required");
    if (!val(f, "email").trim()) e.push("Email is required");
    if (!p) e.push("Password is required");
    if (!c) e.push("Confirm password is required");
    if (p && c && p !== c) e.push("Passwords do not match");
    return e;
  },
  login(f) {
    const e = [];
    if (!val(f, "email").trim()) e.push("Email is required");
    if (!val(f, "password")) e.push("Password is required");
    return e;
  },
  todo(f) {
    const t = val(f, "title").trim();
    if (!t) return ["Title is required"];
    if (t.length > 200) return ["Title is too long (200 characters at most)"];
    return [];
  },
};

document.querySelectorAll("form[data-rules]").forEach((f) => {
  f.addEventListener("submit", (ev) => {
    const errs = RULES[f.dataset.rules](f);
    const box = f.querySelector(".errors");
    box.innerHTML = "";
    errs.forEach((m) => { const li = document.createElement("li"); li.textContent = m; box.appendChild(li); });
    box.hidden = errs.length === 0;
    if (errs.length) ev.preventDefault();
  });
});

document.querySelectorAll("form[data-confirm]").forEach((f) => {
  f.addEventListener("submit", (ev) => { if (!confirm(f.dataset.confirm)) ev.preventDefault(); });
});
