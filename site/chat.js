/* MK.Buildings — Talk to the team.
 * The REAL Python agents (site/py/mk_agents/*.py) run in the browser with Pyodide (free, open source).
 * Voice uses the browser's built-in speech recognition and speech synthesis (free).
 * No server, no API key, no paid service. */
(function () {
  "use strict";

  const DATA = window.MKB_DATA;
  const $ = id => document.getElementById(id);
  if (!DATA || !$("chat")) return;

  const TEAM = "team";
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const agentInfo = Object.fromEntries(DATA.agents.map(a => [a.name, a]));
  const divClass = d => "div-" + String(d || "leadership").toLowerCase().replace(/\s+/g, "-");
  const initials = name => {
    if (name === "CEO Orchestrator") return "CEO";
    if (name === "You") return "You";
    const words = name.replace(/\(.*?\)/g, "").replace(/&/g, " ").split(/[\s,]+/).filter(w => /^[A-Za-z]/.test(w));
    return (words[0][0] + (words[1] ? words[1][0] : "")).toUpperCase();
  };
  const slug = name => name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

  // People you can talk to (same ids as the Python ChatEngine)
  const people = [{ id: TEAM, name: "Whole team", division: "Team chat", role: "Ask anything. The CEO Orchestrator brings in the right experts." }]
    .concat(DATA.agents.map(a => ({ id: slug(a.name), name: a.name, division: a.division, role: a.role })));
  const histories = {};
  let current = TEAM;

  // ---------- Python engine (Pyodide) ----------
  let enginePromise = null;
  let engine = null;

  function setStatus(text, kind) {
    const el = $("engine-status");
    el.textContent = text || "";
    el.className = "engine-status" + (kind ? " " + kind : "");
  }

  function loadEngine() {
    if (enginePromise) return enginePromise;
    if (typeof window.loadPyodide !== "function") {
      setStatus("The Python engine could not be loaded in this browser.", "error");
      return Promise.reject(new Error("pyodide missing"));
    }
    setStatus("Waking up the team… loading the Python agents into your browser (about 14 MB, first time only).", "loading");
    enginePromise = (async () => {
      const pyodide = await window.loadPyodide({ indexURL: "vendor/pyodide/" });
      pyodide.FS.mkdirTree("/home/pyodide/mk_agents");
      for (const file of DATA.python_files) {
        const res = await fetch("py/mk_agents/" + file);
        if (!res.ok) throw new Error("Could not load " + file);
        pyodide.FS.writeFile("/home/pyodide/mk_agents/" + file, await res.text());
      }
      pyodide.runPython("import sys\nsys.path.insert(0, '/home/pyodide')\nfrom mk_agents.chat import ChatEngine\nengine = ChatEngine()");
      engine = pyodide.globals.get("engine");
      setStatus("The team is ready. Type or speak your question.", "ready");
      return engine;
    })().catch(err => {
      enginePromise = null;
      setStatus("Sorry, the team could not start: " + err.message + ". Please reload the page.", "error");
      throw err;
    });
    return enginePromise;
  }

  // Start loading when the chat section comes into view (or on first use)
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(entries => {
      if (entries.some(e => e.isIntersecting)) { loadEngine().catch(() => {}); io.disconnect(); }
    }, { rootMargin: "200px" });
    io.observe($("chat"));
  }

  async function askTeam(message, target) {
    const eng = await loadEngine();
    return JSON.parse(eng.ask_json(message, target));
  }

  // ---------- UI ----------
  function renderPeople() {
    $("people-list").innerHTML = people.map(p => `
      <li><button type="button" class="person ${divClass(p.division)}" data-id="${esc(p.id)}" aria-pressed="${p.id === current}">
        <span class="avatar" aria-hidden="true">${p.id === TEAM ? "ALL" : esc(initials(p.name))}</span>
        <span class="person-text"><strong>${esc(p.name)}</strong><small>${esc(p.division)}</small></span>
      </button></li>`).join("");
  }

  function renderHeader() {
    const p = people.find(x => x.id === current);
    $("chat-title").innerHTML = `<span class="avatar ${divClass(p.division)}" aria-hidden="true">${p.id === TEAM ? "ALL" : esc(initials(p.name))}</span>
      <div><strong>${esc(p.name)}</strong><small>${esc(p.role)}</small></div>`;
  }

  function renderSuggestions() {
    const list = current === TEAM ? DATA.chat_suggestions : ["Who are you?", "What are your instructions?", DATA.chat_suggestions[0]];
    $("suggestions").innerHTML = list.map(s => `<button type="button" class="suggestion">${esc(s)}</button>`).join("");
  }

  function addMessage(who, text, extraClass) {
    const mine = who === "You";
    const info = agentInfo[who];
    const li = document.createElement("li");
    li.className = "message " + (mine ? "from-me" : "from-agent " + divClass(info ? info.division : "leadership")) + (extraClass ? " " + extraClass : "");
    li.innerHTML = `<span class="avatar" aria-hidden="true">${esc(initials(who))}</span>
      <div class="bubble"><span class="who">${esc(who)}</span><span class="text"></span></div>`;
    li.querySelector(".text").textContent = text;
    $("messages").appendChild(li);
    $("messages").scrollTop = $("messages").scrollHeight;
    return li;
  }

  function showHistory() {
    $("messages").innerHTML = "";
    const history = histories[current] || [];
    if (!history.length) {
      const p = people.find(x => x.id === current);
      addMessage(current === TEAM ? "CEO Orchestrator" : p.name,
        current === TEAM ? "Hello Founder! Ask me anything, or describe a property and I'll bring in the experts."
                         : `Hi, I'm the ${p.name}. ${p.role} How can I help?`);
      return;
    }
    history.forEach(m => addMessage(m.who, m.text));
  }

  function remember(target, who, text) {
    (histories[target] = histories[target] || []).push({ who, text });
  }

  function selectPerson(id) {
    current = id;
    renderPeople(); renderHeader(); renderSuggestions(); showHistory();
  }

  $("people-list").addEventListener("click", e => {
    const btn = e.target.closest(".person");
    if (btn) selectPerson(btn.dataset.id);
  });
  $("suggestions").addEventListener("click", e => {
    const btn = e.target.closest(".suggestion");
    if (btn) send(btn.textContent);
  });
  $("chat-form").addEventListener("submit", e => { e.preventDefault(); send($("chat-text").value); });

  // Messages are answered one at a time, in order. Each answer stays in the chat it was asked in.
  let queue = Promise.resolve();
  function send(text) {
    text = (text || "").trim();
    if (!text) return queue;
    const target = current;
    $("chat-text").value = "";
    addMessage("You", text); remember(target, "You", text);
    const speaker = target === TEAM ? "CEO Orchestrator" : people.find(p => p.id === target).name;
    const thinking = addMessage(speaker, "Thinking…", "thinking");
    queue = queue.then(async () => {
      try {
        const replies = await askTeam(text, target);
        thinking.remove();
        for (const r of replies) {
          remember(target, r.agent, r.text);
          if (current === target) addMessage(r.agent, r.text);
          await new Promise(res => setTimeout(res, 120));
        }
        speak(replies);
      } catch (err) {
        thinking.remove();
        if (current === target) addMessage("CEO Orchestrator", "Sorry, the team is not available right now. Please reload the page and try again.", "error");
      }
    });
    return queue;
  }

  // ---------- Voice output (free, built into the browser) ----------
  const canSpeak = "speechSynthesis" in window;
  if (!canSpeak) $("speak-toggle").closest("label").hidden = true;

  function speak(replies) {
    if (!canSpeak || !$("speak-toggle").checked) return;
    window.speechSynthesis.cancel();
    replies.forEach((r, i) => {
      const clean = r.text.replace(/\nSource:.*$/s, "").replace(/\$/g, " dollars ").replace(/\n/g, ". ");
      const u = new SpeechSynthesisUtterance(`${r.agent}. ${clean}`);
      u.lang = "en-US";
      u.rate = 1.05;
      u.pitch = 0.85 + (i % 4) * 0.12; // slightly different voice for each speaker
      window.speechSynthesis.speak(u);
    });
  }
  $("speak-toggle").addEventListener("change", e => { if (!e.target.checked && canSpeak) window.speechSynthesis.cancel(); });

  // ---------- Voice input (free, built into Chrome, Edge and Safari) ----------
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const micBtn = $("btn-mic");
  if (!Recognition) {
    micBtn.disabled = true;
    micBtn.title = "Voice input works in Chrome, Edge and Safari";
    $("chat-hint").textContent += " Voice input works in Chrome, Edge and Safari.";
  } else {
    const rec = new Recognition();
    rec.lang = "en-US";
    rec.interimResults = true;
    rec.continuous = false;
    let listening = false;
    let finalText = "";

    rec.onresult = e => {
      let interim = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) finalText += e.results[i][0].transcript;
        else interim += e.results[i][0].transcript;
      }
      $("chat-text").value = (finalText + interim).trim();
    };
    rec.onend = () => {
      listening = false;
      micBtn.setAttribute("aria-pressed", "false");
      micBtn.querySelector("span").textContent = "Speak";
      if (finalText.trim()) send(finalText);
    };
    rec.onerror = e => {
      const msg = e.error === "not-allowed" ? "Microphone permission was denied. Allow the microphone in your browser settings."
        : e.error === "no-speech" ? "I didn't hear anything. Try again." : "Voice input error: " + e.error;
      setStatus(msg, "error");
    };
    micBtn.addEventListener("click", () => {
      if (listening) { rec.stop(); return; }
      finalText = "";
      try {
        rec.start();
        listening = true;
        micBtn.setAttribute("aria-pressed", "true");
        micBtn.querySelector("span").textContent = "Listening… tap to stop";
        loadEngine().catch(() => {});
      } catch (err) { setStatus("Voice input could not start: " + err.message, "error"); }
    });
  }

  // ---------- start ----------
  selectPerson(TEAM);
  // Allow other parts of the page to open a chat with a specific expert
  window.MKB_CHAT = { open(name) { selectPerson(slug(name) === "whole-team" ? TEAM : slug(name)); $("chat").scrollIntoView(); } };
})();
