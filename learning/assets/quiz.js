/* LifeOS learning — shared lesson widgets.
   quiz(el, {q, opts:[...], answer:i, why})  — one multiple-choice question, instant feedback.
   timer(el, minutes)                          — a visible countdown; stopping when it ends is allowed.
   Options in a quiz should be the same length so the format never gives the answer away. */
"use strict";
function quiz(el, spec) {
  el.className = "quiz";
  el.innerHTML = '<div class="q">' + spec.q + '</div><div class="opts"></div><div class="fb"></div>';
  const opts = el.querySelector(".opts"), fb = el.querySelector(".fb");
  spec.opts.forEach((o, i) => {
    const b = document.createElement("button");
    b.textContent = o;
    b.onclick = () => {
      opts.querySelectorAll("button").forEach(x => x.classList.remove("right", "wrong"));
      if (i === spec.answer) { b.classList.add("right"); fb.className = "fb ok"; fb.textContent = "Yes. " + (spec.why || ""); }
      else { b.classList.add("wrong"); fb.className = "fb"; fb.textContent = "Not that one. Try again; the wrong ones teach as much."; }
    };
    opts.appendChild(b);
  });
}
function timer(el, minutes) {
  el.className = "timer";
  let left = minutes * 60, id = null;
  el.innerHTML = '<span class="clock">' + fmt(left) + '</span><button>start ' + minutes + ' min</button><span class="note">stopping when it ends is the deal</span>';
  const clock = el.querySelector(".clock"), btn = el.querySelector("button");
  function fmt(s) { return String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0"); }
  btn.onclick = () => {
    if (id) { clearInterval(id); id = null; btn.textContent = "resume"; return; }
    btn.textContent = "pause";
    id = setInterval(() => {
      left--; clock.textContent = fmt(Math.max(0, left));
      if (left <= 0) { clearInterval(id); id = null; clock.className = "clock done"; clock.textContent = "done"; btn.textContent = "that's time"; }
    }, 1000);
  };
}
