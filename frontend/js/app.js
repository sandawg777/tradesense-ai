const SESSION_ID = 'trader_' + Math.random().toString(36).substr(2, 9);
const API_URL = 'http://127.0.0.1:8000/analyze';
let queryCount = 0;

document.getElementById('session-display').textContent = SESSION_ID;

function setInput(text) {
  document.getElementById('input').value = text;
  document.getElementById('input').focus();
}

function askQuick(query) {
  document.getElementById('input').value = query;
  sendMessage();
}

function formatResponse(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
    .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
    .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>');
}

function extractTicker(text) {
  const match = text.match(/\b([A-Z]{2,5})\b/);
  return match ? match[1] : null;
}

function updateSignals(response, ticker) {
  const text = response.toLowerCase();
  const signals = [];

  if (text.includes('bullish') || text.includes('golden cross')) {
    signals.push({ label: 'Trend', value: 'BULLISH', cls: 'signal-bullish' });
  }
  if (text.includes('bearish') || text.includes('death cross')) {
    signals.push({ label: 'Trend', value: 'BEARISH', cls: 'signal-bearish' });
  }
  if (text.includes('overbought')) {
    signals.push({ label: 'RSI', value: 'OVERBOUGHT', cls: 'signal-bearish' });
  }
  if (text.includes('oversold')) {
    signals.push({ label: 'RSI', value: 'OVERSOLD', cls: 'signal-bullish' });
  }
  if (text.includes('breakout') || (text.includes('buy') && !text.includes("don't buy"))) {
    signals.push({ label: 'Action', value: 'BUY SIGNAL', cls: 'signal-bullish' });
  }
  if (text.includes('neutral') && signals.length === 0) {
    signals.push({ label: 'Trend', value: 'NEUTRAL', cls: 'signal-neutral' });
  }

  if (ticker) {
    document.getElementById('last-ticker').textContent = ticker;
    document.getElementById('last-price').textContent = 'Analysis complete';
  }

  const panel = document.getElementById('signals-panel');
  if (signals.length > 0) {
    panel.innerHTML = '<div class="signal-stack">' + signals.map(s =>
      `<div class="signal-item"><span class="signal-label">${s.label}</span><span class="signal-value ${s.cls}">${s.value}</span></div>`
    ).join('') + '</div>';
  } else {
    panel.innerHTML = '<div class="empty-state">No clear signals detected</div>';
  }
}

function updateGovLog(flagged, warning) {
  const log = document.getElementById('gov-log');
  const time = new Date().toLocaleTimeString();
  const line = flagged
    ? `<span class="warn">[WARN]</span> PII detected ${time}<br>`
    : `<span class="ok">[OK]</span> Clean request ${time}<br>`;
  log.innerHTML += line;
  log.scrollTop = log.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById('input');
  const btn = document.getElementById('btn');
  const chat = document.getElementById('chat');
  const query = input.value.trim();
  if (!query) return;

  const userDiv = document.createElement('div');
  userDiv.className = 'message user';
  userDiv.innerHTML = `
    <div class="avatar user-av">YOU</div>
    <div>
      <div class="bubble user">${query}</div>
      <div class="timestamp" style="text-align:right">${new Date().toLocaleTimeString()}</div>
    </div>
  `;
  chat.appendChild(userDiv);

  input.value = '';
  btn.disabled = true;
  btn.textContent = 'Analyzing...';

  const loadDiv = document.createElement('div');
  loadDiv.className = 'message';
  loadDiv.innerHTML = `
    <div class="avatar ai">AI</div>
    <div><div class="bubble ai loading">Running multi-agent analysis with live market data...</div></div>
  `;
  chat.appendChild(loadDiv);
  chat.scrollTop = chat.scrollHeight;

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: SESSION_ID })
    });

    const data = await response.json();
    queryCount++;
    document.getElementById('query-count').textContent = queryCount;

    const ticker = extractTicker(query.toUpperCase());
    updateSignals(data.answer, ticker);
    updateGovLog(data.flagged, data.warning);

    loadDiv.innerHTML = `
      <div class="avatar ai">AI</div>
      <div>
        ${data.warning ? `<div class="warning-banner">[WARN] ${data.warning}</div>` : ''}
        <div class="bubble ai">${formatResponse(data.answer)}</div>
        <div class="timestamp">${new Date().toLocaleTimeString()} · ${SESSION_ID}</div>
      </div>
    `;
  } catch (error) {
    loadDiv.innerHTML = `
      <div class="avatar ai">AI</div>
      <div><div class="bubble ai" style="color:var(--destructive)">Connection error. Is the API running at ${API_URL}?</div></div>
    `;
  }

  btn.disabled = false;
  btn.textContent = 'Analyze';
  chat.scrollTop = chat.scrollHeight;
}
