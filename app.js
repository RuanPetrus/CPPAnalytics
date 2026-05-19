async function init() {
  const res = await fetch('site_data.json');
  const { begin_date, deadline, rules, competitors } = await res.json();

  const BEGIN_DATE = new Date(begin_date);
  const DEADLINE   = new Date(deadline);
  const today      = new Date();

  function daysSince(date) {
    return Math.max(1, Math.ceil((today - date) / 86400000));
  }

  function totalScore(user) {
    return Object.values(user.scores_sources)
      .reduce((s, src) => s + (src.questions_score || 0) + (src.rating_score || 0), 0);
  }

  function totalQuestions(user) {
    return Object.values(user.scores_sources)
      .reduce((s, src) => s + (src.questions_score || 0), 0);
  }

  function medal(score) {
    if (score > 3000) return '🥇';
    if (score > 2000) return '🥈';
    if (score > 1000) return '🥉';
    return '';
  }

  function formatDate(date) {
    return date.toLocaleDateString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric'
    }).toUpperCase();
  }

  const days     = daysSince(BEGIN_DATE);
  const daysLeft = Math.max(0, Math.ceil((DEADLINE - today) / 86400000));

  document.getElementById('header-date').textContent = formatDate(today);

  document.getElementById('header-meta').innerHTML =
    `<span>STARTED &nbsp; ${formatDate(BEGIN_DATE)}</span>` +
    `<span>DEADLINE &nbsp; ${formatDate(DEADLINE)}</span>` +
    `<span>DAYS ELAPSED &nbsp; ${days}</span>` +
    `<span>DAYS LEFT &nbsp; ${daysLeft}</span>`;

  const ranked = [...competitors].sort((a, b) => totalScore(b) - totalScore(a));

  // Render rules
  const rulesList = document.getElementById('rules-list');
  if (rules && rules.length) {
    rules.forEach(rule => {
      const li = document.createElement('li');
      li.textContent = rule;
      rulesList.appendChild(li);
    });
  } else {
    document.getElementById('rules-section').style.display = 'none';
  }

  // Render table
  const tbody = document.getElementById('ranking-body');
  ranked.forEach((user, i) => {
    const score     = totalScore(user);
    const questions = totalQuestions(user);
    const meta      = parseInt(user.meta);
    const pct       = Math.min(100, Math.round((score / meta) * 100));
    const qpd       = (questions / days).toFixed(1);
    const m         = medal(score);

    const remaining = Math.max(0, meta - score);
    const slug = user.nome.toLowerCase().replace(/\s+/g, '-');

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="td-rank">${String(i + 1).padStart(2, '0')}</td>
      <td class="td-name">${m ? `<span class="medal">${m}</span>` : ''}<a href="#user-${slug}">${user.nome}</a></td>
      <td class="td-score">${score}</td>
      <td class="td-qpd">${qpd}</td>
      <td class="td-remaining ${remaining === 0 ? 'done' : ''}">${remaining === 0 ? '✓ done' : `${remaining} to go`}</td>
      <td class="td-progress">
        <div class="progress-wrap">
          <div class="progress-track">
            <div class="progress-fill" style="width:${pct}%"></div>
          </div>
          <span class="progress-pct">${pct}%</span>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // Render cards
  const grid = document.getElementById('cards-grid');
  ranked.forEach(user => {
    const score = totalScore(user);
    const m     = medal(score);

    const sourcesHTML = Object.entries(user.scores_sources).map(([src, stats]) => `
      <div>
        <div class="source-title">${src}</div>
        <div class="source-stats">
          <div class="stat">
            <span class="stat-label">Questions</span>
            <span class="stat-value">${stats.questions_score ?? '—'}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Rating</span>
            <span class="stat-value">${stats.rating_score ?? '—'}</span>
          </div>
        </div>
      </div>
    `).join('');

    const slug = user.nome.toLowerCase().replace(/\s+/g, '-');
    const card = document.createElement('div');
    card.className = 'card';
    card.id = `user-${slug}`;
    card.innerHTML = `
      <div class="card-header">
        <div class="card-name">${m ? `<span class="medal">${m}</span>` : ''}${user.nome}</div>
        <div class="card-total">${score} pts</div>
      </div>
      <div class="card-body">${sourcesHTML}</div>
    `;
    grid.appendChild(card);
  });
}

init();
