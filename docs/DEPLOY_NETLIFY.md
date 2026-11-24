# Deploying the MK.Buildings website to Netlify (free)

The website is in the `site/` folder. It is a **static site** (HTML, CSS and JavaScript), so it works on Netlify's free plan with no build step, no server and no paid services.

The agent results shown on the site were produced by the real Python agents (`mk_agents/`) and saved in `site/data/site-data.js` by `scripts/export_site_data.py`.

The **Talk to the team** chat runs those same Python agents directly in the visitor's browser with **Pyodide** (free, open source, bundled in `site/vendor/pyodide/`, about 14 MB). The microphone uses the browser's free speech recognition. Netlify serves the site over HTTPS, which browsers require before they allow the microphone.

---

## Option A — Connect your GitHub repository (recommended)

The site updates automatically every time you push to `main`.

1. Go to **https://app.netlify.com** and sign up or log in for free. **Sign up with GitHub** is easiest.
2. Click **Add new project → Import an existing project**. Older Netlify screens call this **Add new site**.
3. Choose **GitHub** and authorize Netlify if asked.
4. Select the repository **`martinezkelleymr/Experts-Agents`**.
5. Check the settings. Netlify reads them from `netlify.toml`, so they should already be filled in:
   - **Branch to deploy:** `main`
   - **Build command:** *(leave empty)*
   - **Publish directory:** `site`
6. Click **Deploy**. After about 30 seconds Netlify shows your public URL, for example `https://something-random-123.netlify.app`.
7. Optional: change the name in **Project configuration → Change project name**, for example to `mk-buildings-ai-experts`. Your URL becomes `https://mk-buildings-ai-experts.netlify.app` if that name is free.

**This URL is your final deliverable.** Open it in a private or incognito window to confirm it works for everyone.

## Option B — Drag and drop (no GitHub connection)

1. Download the repository from GitHub (**Code → Download ZIP**) and unzip it.
2. Go to **https://app.netlify.com/drop**.
3. Drag the **`site`** folder (not the whole project) onto the page.
4. Netlify gives you a public URL. Log in to keep the site permanently; sites dropped without an account are temporary.

To update an Option B site later, drag the `site` folder again onto the project's **Deploys** page.

---

## Test the website on your own computer first

```bash
cd site
python3 -m http.server 8000
```

Then open http://localhost:8000. Use the local server (not a double-click on `index.html`) so the chat can load the Python agents. The microphone works on `localhost` and on Netlify (HTTPS).

## After changing the agents or sample data

```bash
python3 scripts/export_site_data.py   # re-run the Python agents and refresh the website data
python3 -m pytest -v                  # make sure everything still passes
git add -A && git commit -m "Update agents" && git push origin main
```

With Option A, Netlify redeploys automatically after the push.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Netlify shows "Page not found" | Make sure **Publish directory** is `site` (Site configuration → Build & deploy). |
| The page loads but the experts or demo are empty | `site/data/site-data.js` is missing. Run `python3 scripts/export_site_data.py`, then commit and push. |
| Netlify asks for a build command | Leave it empty. Nothing needs to be built. |
| The test `test_site_data_is_up_to_date_with_the_agents` fails | Run `python3 scripts/export_site_data.py` to refresh the data. |
| Chat says "the team could not start" | Reload the page. Check that `site/vendor/pyodide/` and `site/py/` were deployed. |
| The 🎤 button is greyed out | That browser has no free speech recognition. Use Chrome, Edge or Safari, or type instead. |
| The microphone doesn't listen | Allow microphone access when the browser asks (padlock icon in the address bar). |

## Cost

Netlify's free plan covers this project: a small static site with no functions, forms or paid add-ons. No credit card is needed for the steps above.
