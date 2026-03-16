// ── Examples ──────────────────────────────────────────────────────────────────
const EXAMPLES = {
  hello: `// Hello World
printf("Hello, World!");
return 0;`,

  arithmetic: `// Arithmetic expressions
int a = 10;
int b = 5;
int sum = a + b;
int diff = a - b;
float ratio = 3.14;
int product = a * b;`,

  if_else: `// If-Else Statement
int score = 85;
int grade = 0;
if (score >= 90) {
    grade = 1;
} else {
    grade = 0;
}
return grade;`,

  while_loop: `// While Loop
int i = 0;
int sum = 0;
while (i < 10) {
    sum = sum + i;
    i = i + 1;
}
return sum;`,

  undeclared: `// Semantic Error: Undeclared variable
int x = 10;
y = 20;
return x + y;`,

  duplicate: `// Semantic Error: Duplicate declaration
int count = 0;
int count = 5;
return count;`,

  syntax_err: `// Syntax Error: Missing semicolon
int x = 10
int y = 20;
return x + y;`,
};

// ── Load examples ─────────────────────────────────────────────────────────────
document.getElementById('example-select').addEventListener('change', e => {
  if (e.target.value && EXAMPLES[e.target.value]) {
    document.getElementById('code-input').value = EXAMPLES[e.target.value];
    e.target.value = '';
  }
});

// ── Tab switching ─────────────────────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    tab.classList.add('active');
    const id = 'tab-' + tab.dataset.tab;
    document.getElementById(id).classList.add('active');
    if (tab.dataset.tab === 'tree' && window._treeData) renderTree(window._treeData);
  });
});

// ── Token type classifier ─────────────────────────────────────────────────────
const KEYWORDS = new Set(['INT','FLOAT','CHAR','VOID','IF','ELSE','WHILE','RETURN','PRINTF']);
const LITERALS  = new Set(['NUMBER_INT','NUMBER_FLOAT','CHAR_LITERAL','STRING_LITERAL']);
const OPERATORS = new Set(['PLUS','MINUS','TIMES','DIVIDE','MODULO','EQ','NEQ','LT','GT','LEQ','GEQ','ASSIGN','AND','OR','NOT']);
const PUNCT     = new Set(['LPAREN','RPAREN','LBRACE','RBRACE','SEMI','COMMA']);

function tokenClass(type) {
  if (KEYWORDS.has(type))  return 'tt-keyword';
  if (type === 'ID')        return 'tt-id';
  if (LITERALS.has(type))   return 'tt-literal';
  if (OPERATORS.has(type))  return 'tt-operator';
  if (PUNCT.has(type))      return 'tt-punct';
  return 'tt-error';
}

// ── Render tokens ─────────────────────────────────────────────────────────────
function renderTokens(tokens) {
  const el = document.getElementById('tokens-content');
  if (!tokens || !tokens.length) {
    el.innerHTML = '<div class="no-errors"><div class="no-errors-icon">∅</div><p>No tokens generated.</p></div>';
    return;
  }

  const rows = tokens.map(t => `
    <tr>
      <td>${t.line}</td>
      <td><span class="token-type ${tokenClass(t.type)}">${t.type}</span></td>
      <td>${escapeHtml(String(t.value))}</td>
    </tr>`).join('');

  el.innerHTML = `
    <div class="phase-label">Phase 1 — Lexical Analysis · ${tokens.length} tokens</div>
    <table class="token-table">
      <thead>
        <tr><th>Line</th><th>Type</th><th>Value</th></tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>`;
}

// ── Render errors ─────────────────────────────────────────────────────────────
function renderErrors(lexErrors, synErrors, semErrors, semWarnings) {
  const el = document.getElementById('errors-content');
  const all = [
    ...lexErrors.map(e => ({...e, phase: 'lex'})),
    ...synErrors.map(e => ({...e, phase: 'syn'})),
    ...semErrors.map(e => ({...e, phase: 'sem'})),
    ...semWarnings.map(e => ({...e, phase: 'warn'})),
  ];

  if (!all.length) {
    el.innerHTML = `
      <div class="no-errors">
        <div class="no-errors-icon">✓</div>
        <p>No errors detected.</p>
      </div>`;
    return;
  }

  const tagLabel = { lex: 'Lexical', syn: 'Syntax', sem: 'Semantic', warn: 'Warning' };
  const cards = all.map(e => `
    <div class="error-card ${e.phase}">
      <span class="error-tag tag-${e.phase}">${tagLabel[e.phase]}</span>
      ${escapeHtml(e.message)}
      ${e.line ? `<div class="error-line">↳ Line ${e.line}</div>` : ''}
    </div>`).join('');

  el.innerHTML = cards;
}

// ── Render symbol table ───────────────────────────────────────────────────────
function renderSymbols(symbols) {
  const el = document.getElementById('symbols-content');
  if (!symbols || !symbols.length) {
    el.innerHTML = `
      <div class="no-errors">
        <div class="no-errors-icon">∅</div>
        <p>No symbols declared.</p>
      </div>`;
    return;
  }

  const rows = symbols.map(s => `
    <tr>
      <td>${escapeHtml(s.name)}</td>
      <td><span class="token-type tt-keyword">${s.type}</span></td>
      <td><span style="color:var(--muted);font-size:11px">${s.scope}</span></td>
      <td>${s.line}</td>
    </tr>`).join('');

  el.innerHTML = `
    <div class="phase-label">Phase 3 — Symbol Table · ${symbols.length} symbol(s)</div>
    <table class="token-table">
      <thead>
        <tr><th>Name</th><th>Type</th><th>Scope</th><th>Line</th></tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>`;
}

// ── D3 Parse Tree ─────────────────────────────────────────────────────────────
let zoom;

function renderTree(data) {
  const container = document.getElementById('tree-container');
  const svg = document.getElementById('tree-svg');
  svg.innerHTML = '';

  if (!data) {
    document.getElementById('tree-empty').style.display = 'flex';
    return;
  }
  document.getElementById('tree-empty').style.display = 'none';

  const W = container.clientWidth || 800;
  const H = container.clientHeight || 500;

  const root = d3.hierarchy(data);
  const nodeCount = root.descendants().length;
  const nodeWidth = Math.max(120, 1600 / nodeCount);
  const layout = d3.tree().nodeSize([nodeWidth, 80]);
  layout(root);

  // Center the tree
  const xs = root.descendants().map(d => d.x);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const treeW = maxX - minX + nodeWidth * 2;
  const treeH = root.height * 80 + 100;

  const svgEl = d3.select('#tree-svg')
    .attr('width', W)
    .attr('height', H);

  zoom = d3.zoom().scaleExtent([0.1, 4]).on('zoom', e => {
    g.attr('transform', e.transform);
  });
  svgEl.call(zoom);

  const g = svgEl.append('g');
  const initTx = W / 2 - (minX + maxX) / 2;
  const initTy = 40;
  g.attr('transform', `translate(${initTx},${initTy})`);
  window._treeG = g;
  window._treeInitTx = initTx;
  window._treeInitTy = initTy;
  window._treeSvgEl = svgEl;

  // Links
  g.selectAll('.link')
    .data(root.links())
    .join('path')
    .attr('class', 'link')
    .attr('d', d3.linkVertical().x(d => d.x).y(d => d.y));

  // Nodes
  const TERMINAL_TYPES = new Set(['Identifier','IntLiteral','FloatLiteral','CharLiteral',
                                   'StringLiteral','Type','Keyword','AssignOp','BinaryOp','UnaryOp']);

  const node = g.selectAll('.node')
    .data(root.descendants())
    .join('g')
    .attr('class', d => `node ${TERMINAL_TYPES.has(d.data.type) && !d.children ? 'terminal' : ''}`)
    .attr('transform', d => `translate(${d.x},${d.y})`);

  node.append('circle').attr('r', 18);

  // Label background
  node.each(function(d) {
    const label = d.data.name || d.data.type;
    const lines = wrapLabel(label, 14);
    const n = d3.select(this);

    const maxLen = Math.max(...lines.map(l => l.length));
    const bw = Math.max(40, maxLen * 6 + 8);
    const bh = lines.length * 13 + 4;

    n.append('rect')
      .attr('class', 'node-label-bg')
      .attr('x', -bw / 2)
      .attr('y', 22)
      .attr('width', bw)
      .attr('height', bh)
      .attr('rx', 3)
      .attr('fill', 'var(--surface)');

    lines.forEach((line, i) => {
      n.append('text')
        .attr('text-anchor', 'middle')
        .attr('x', 0)
        .attr('y', 32 + i * 13)
        .text(line);
    });
  });
}

function wrapLabel(label, maxLen) {
  if (label.length <= maxLen) return [label];
  const words = label.split(/\s+|(?<=[:=])/);
  const lines = [];
  let current = '';
  for (const w of words) {
    if ((current + w).length > maxLen) {
      if (current) lines.push(current.trim());
      current = w;
    } else {
      current += (current ? ' ' : '') + w;
    }
  }
  if (current) lines.push(current.trim());
  return lines.length ? lines : [label.slice(0, maxLen)];
}

// Tree controls
document.getElementById('tree-zoom-in').addEventListener('click', () => {
  if (window._treeSvgEl && zoom)
    window._treeSvgEl.transition().call(zoom.scaleBy, 1.4);
});
document.getElementById('tree-zoom-out').addEventListener('click', () => {
  if (window._treeSvgEl && zoom)
    window._treeSvgEl.transition().call(zoom.scaleBy, 0.7);
});
document.getElementById('tree-reset').addEventListener('click', () => {
  if (window._treeSvgEl && zoom) {
    window._treeSvgEl.transition()
      .call(zoom.transform, d3.zoomIdentity.translate(window._treeInitTx, window._treeInitTy));
  }
});

// ── Validate ──────────────────────────────────────────────────────────────────
document.getElementById('validate-btn').addEventListener('click', async () => {
  const code = document.getElementById('code-input').value.trim();
  if (!code) return;

  const btn = document.getElementById('validate-btn');
  btn.classList.add('loading');
  btn.innerHTML = '<div class="spinner"></div> Compiling…';

  try {
    const res = await fetch('/api/compile', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({code}),
    });
    const data = await res.json();
    displayResults(data);
  } catch (err) {
    showBanner('error', '✗ Network error — is the backend running?');
  } finally {
    btn.classList.remove('loading');
    btn.innerHTML = '<span class="btn-icon">▶</span> Validate';
  }
});

function displayResults(data) {
  // Status banner
  const banner = document.getElementById('status-banner');
  banner.style.display = 'flex';
  banner.className = data.status === 'success' ? 'success' : 'error';
  document.getElementById('status-icon').textContent = data.status === 'success' ? '✓' : '✗';
  document.getElementById('status-text').textContent = data.final_message;

  // Tab badges
  setTabBadge('tb-tokens',  (data.tokens || []).length, false);
  const errCount = (data.lexical_errors||[]).length + (data.syntax_errors||[]).length + (data.semantic_errors||[]).length;
  setTabBadge('tb-errors',  errCount, errCount > 0);
  setTabBadge('tb-symbols', (data.symbol_table||[]).length, false);

  // Panels
  renderTokens(data.tokens || []);
  renderErrors(
    data.lexical_errors  || [],
    data.syntax_errors   || [],
    data.semantic_errors || [],
    data.semantic_warnings || []
  );
  renderSymbols(data.symbol_table || []);

  // Tree
  window._treeData = data.parse_tree || null;
  if (document.getElementById('tab-tree').classList.contains('active')) {
    renderTree(window._treeData);
  }
}

function setTabBadge(id, count, isError) {
  const el = document.getElementById(id);
  el.textContent = count;
  el.className = 'tab-badge' + (isError ? ' error' : count > 0 ? ' ok' : '');
}

function showBanner(type, msg) {
  const banner = document.getElementById('status-banner');
  banner.style.display = 'flex';
  banner.className = type;
  document.getElementById('status-icon').textContent = type === 'success' ? '✓' : '✗';
  document.getElementById('status-text').textContent = msg;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── Keyboard shortcut: Ctrl+Enter to validate ─────────────────────────────────
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    document.getElementById('validate-btn').click();
  }
});

// ── Load default example ──────────────────────────────────────────────────────
document.getElementById('code-input').value = EXAMPLES.while_loop;