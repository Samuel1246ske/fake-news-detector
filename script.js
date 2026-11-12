const API_URL = "https://YOUR-BACKEND-URL.example.com"; // Replace after deploying the FastAPI backend.
const input = document.getElementById('newsText');
const count = document.getElementById('charCount');
const analyse = document.getElementById('analyseBtn');
const status = document.getElementById('status');
const result = document.getElementById('result');

document.getElementById('year').textContent = new Date().getFullYear();
input.addEventListener('input', () => count.textContent = `${input.value.length.toLocaleString()} / 12,000 characters`);
document.getElementById('clearBtn').addEventListener('click', () => { input.value = ''; count.textContent = '0 / 12,000 characters'; input.focus(); status.textContent = ''; result.hidden = true; });
document.getElementById('newCheck').addEventListener('click', () => { result.hidden = true; input.focus(); });

analyse.addEventListener('click', async () => {
  const text = input.value.trim();
  result.hidden = true;
  if (text.length < 40) { status.textContent = 'Please enter at least 40 characters so the model has enough context.'; return; }
  if (text.length > 12000) { status.textContent = 'Please keep the text below 12,000 characters.'; return; }
  if (API_URL.includes('YOUR-BACKEND-URL')) { status.textContent = 'The website interface is ready. Deploy the backend and replace API_URL in script.js to activate AI analysis.'; return; }
  analyse.disabled = true; analyse.innerHTML = 'Analysing…'; status.textContent = '';
  try {
    const response = await fetch(`${API_URL.replace(/\/$/, '')}/predict`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text}) });
    if (!response.ok) throw new Error(`Server returned ${response.status}`);
    const data = await response.json();
    showResult(data);
  } catch (error) { status.textContent = `Could not analyse this story. Please try again. (${error.message})`; }
  finally { analyse.disabled = false; analyse.innerHTML = 'Analyse story <span>→</span>'; }
});
function showResult(data) {
  const labels = { likely_real:'Likely credible pattern', likely_fake:'Potentially misleading pattern', uncertain:'Needs more verification' };
  const badges = { likely_real:'LOWER RISK SIGNAL', likely_fake:'HIGHER RISK SIGNAL', uncertain:'UNVERIFIED' };
  const label = labels[data.label] || labels.uncertain;
  document.getElementById('resultLabel').textContent = label;
  document.getElementById('resultBadge').textContent = badges[data.label] || badges.uncertain;
  document.getElementById('resultSummary').textContent = data.summary || 'The model could not make a confident assessment.';
  const confidence = Math.max(0, Math.min(100, Number(data.confidence) || 0));
  document.getElementById('confidence').textContent = `${confidence.toFixed(1)}%`;
  document.getElementById('scoreBar').style.width = `${confidence}%`;
  const checks = Array.isArray(data.checks) ? data.checks : ['Find the original publication or source.','Check the date and whether the story has been updated.','Compare the claim with at least two independent, reputable sources.'];
  document.getElementById('checksList').replaceChildren(...checks.map(item => { const li=document.createElement('li'); li.textContent=item; return li; }));
  result.hidden = false; result.scrollIntoView({behavior:'smooth',block:'start'});
}
