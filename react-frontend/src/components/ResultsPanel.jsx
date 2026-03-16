import React, { useState } from 'react';
import ParseTreeView from './ParseTreeView';

function escapeHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function TokensTable({ tokens }) {
  if (!tokens || !tokens.length) {
    return <div className="no-errors"><div className="no-errors-icon">∅</div><p>No tokens generated.</p></div>;
  }

  const tokenClass = (type) => {
    const KEYWORDS = new Set(['INT','FLOAT','CHAR','VOID','IF','ELSE','WHILE','RETURN','PRINTF']);
    const LITERALS = new Set(['NUMBER_INT','NUMBER_FLOAT','CHAR_LITERAL','STRING_LITERAL']);
    const OPERATORS = new Set(['PLUS','MINUS','TIMES','DIVIDE','MODULO','EQ','NEQ','LT','GT','LEQ','GEQ','ASSIGN','AND','OR','NOT']);
    const PUNCT = new Set(['LPAREN','RPAREN','LBRACE','RBRACE','SEMI','COMMA']);
    
    if (KEYWORDS.has(type)) return 'tt-keyword';
    if (type === 'ID') return 'tt-id';
    if (LITERALS.has(type)) return 'tt-literal';
    if (OPERATORS.has(type)) return 'tt-operator';
    if (PUNCT.has(type)) return 'tt-punct';
    return 'tt-error';
  };

  return (
    <div className="tokens-container">
      <div className="phase-label">Phase 1 — Lexical Analysis · {tokens.length} tokens</div>
      <table className="token-table">
        <thead>
          <tr><th>Line</th><th>Type</th><th>Value</th></tr>
        </thead>
        <tbody>
          {tokens.map((t, i) => (
            <tr key={i}>
              <td>{t.line}</td>
              <td><span className={`token-type ${tokenClass(t.type)}`}>{t.type}</span></td>
              <td>{escapeHtml(t.value)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ErrorsList({ errors }) {
  if (!errors || !errors.length) {
    return (
      <div className="no-errors">
        <div className="no-errors-icon">✓</div>
        <p>No errors detected.</p>
      </div>
    );
  }

  const tagLabel = { lex: 'Lexical', syn: 'Syntax', sem: 'Semantic', warn: 'Warning' };

  return (
    <div className="errors-container">
      {errors.map((e, i) => (
        <div key={i} className={`error-card ${e.phase}`}>
          <span className={`error-tag tag-${e.phase}`}>{tagLabel[e.phase]}</span>
          {escapeHtml(e.message)}
          {e.line && <div className="error-line">↳ Line {e.line}</div>}
        </div>
      ))}
    </div>
  );
}

function SymbolTable({ symbols }) {
  if (!symbols || !symbols.length) {
    return (
      <div className="no-errors">
        <div className="no-errors-icon">∅</div>
        <p>No symbols declared.</p>
      </div>
    );
  }

  return (
    <div className="symbols-container">
      <div className="phase-label">Phase 3 — Symbol Table · {symbols.length} symbol(s)</div>
      <table className="token-table">
        <thead>
          <tr><th>Name</th><th>Type</th><th>Scope</th><th>Line</th></tr>
        </thead>
        <tbody>
          {symbols.map((s, i) => (
            <tr key={i}>
              <td>{escapeHtml(s.name)}</td>
              <td><span className="token-type tt-keyword">{s.type}</span></td>
              <td><span style={{color:'var(--muted)', fontSize:'11px'}}>{s.scope}</span></td>
              <td>{s.line}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function ResultsPanel({ data, errorMsg }) {
  const [activeTab, setActiveTab] = useState('tokens');

  const tokens = data?.tokens || [];
  const lexErrors = (data?.lexical_errors || []).map(e => ({...e, phase:'lex'}));
  const synErrors = (data?.syntax_errors || []).map(e => ({...e, phase:'syn'}));
  const semErrors = (data?.semantic_errors || []).map(e => ({...e, phase:'sem'}));
  const semWarnings = (data?.semantic_warnings || []).map(e => ({...e, phase:'warn'}));
  
  const allErrors = [...lexErrors, ...synErrors, ...semErrors, ...semWarnings];
  const symbols = data?.symbol_table || [];
  const parseTree = data?.parse_tree || null;

  const errCount = allErrors.filter(e => e.phase !== 'warn').length;

  return (
    <div className="right-panel">
      {/* Banner */}
      <div 
        id="status-banner" 
        style={{ display: (data || errorMsg) ? 'flex' : 'none' }}
        className={errorMsg ? 'error' : (data?.status === 'success' ? 'success' : 'error')}
      >
        <span className="status-icon" id="status-icon">
          {errorMsg ? '✗' : (data?.status === 'success' ? '✓' : '✗')}
        </span>
        <span id="status-text">{errorMsg || data?.final_message}</span>
      </div>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'tokens' ? 'active' : ''}`} 
          onClick={() => setActiveTab('tokens')}
        >
          Tokens <span className={`tab-badge ${tokens.length > 0 ? 'ok' : ''}`}>{tokens.length || '—'}</span>
        </button>
        <button 
          className={`tab ${activeTab === 'errors' ? 'active' : ''}`} 
          onClick={() => setActiveTab('errors')}
        >
          Errors <span className={`tab-badge ${errCount > 0 ? 'error' : 'ok'}`}>{errCount || '—'}</span>
        </button>
        <button 
          className={`tab ${activeTab === 'tree' ? 'active' : ''}`} 
          onClick={() => setActiveTab('tree')}
        >
          Parse Tree
        </button>
        <button 
          className={`tab ${activeTab === 'symbols' ? 'active' : ''}`} 
          onClick={() => setActiveTab('symbols')}
        >
          Symbols <span className={`tab-badge ${symbols.length > 0 ? 'ok' : ''}`}>{symbols.length || '—'}</span>
        </button>
      </div>

      <div className={`tab-content ${activeTab === 'tokens' ? 'active' : ''}`}>
        {data ? <TokensTable tokens={tokens} /> : <Placeholder text="Token stream will appear here after validation." />}
      </div>

      <div className={`tab-content ${activeTab === 'errors' ? 'active' : ''}`}>
        {data ? <ErrorsList errors={allErrors} /> : <Placeholder text="Lexical, syntax, and semantic errors will appear here." />}
      </div>

      <div className={`tab-content ${activeTab === 'tree' ? 'active' : ''}`}>
        {data ? <ParseTreeView data={parseTree} /> : <Placeholder icon="🌲" text="Parse tree will render here after validation." />}
      </div>

      <div className={`tab-content ${activeTab === 'symbols' ? 'active' : ''}`}>
        {data ? <SymbolTable symbols={symbols} /> : <Placeholder text="Symbol table will appear here after validation." />}
      </div>
    </div>
  );
}

function Placeholder({ icon = '⬡', text }) {
  return (
    <div className="placeholder">
      <div className="placeholder-icon">{icon}</div>
      <p>{text}</p>
    </div>
  );
}
