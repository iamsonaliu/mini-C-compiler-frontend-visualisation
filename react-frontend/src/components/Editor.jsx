import React from 'react';

const EXAMPLES = {
  hello: `// Hello World\nprintf("Hello, World!");\nreturn 0;`,
  arithmetic: `// Arithmetic expressions\nint a = 10;\nint b = 5;\nint sum = a + b;\nint diff = a - b;\nfloat ratio = 3.14;\nint product = a * b;`,
  if_else: `// If-Else Statement\nint score = 85;\nint grade = 0;\nif (score >= 90) {\n    grade = 1;\n} else {\n    grade = 0;\n}\nreturn grade;`,
  while_loop: `// While Loop\nint i = 0;\nint sum = 0;\nwhile (i < 10) {\n    sum = sum + i;\n    i = i + 1;\n}\nreturn sum;`,
  undeclared: `// Semantic Error: Undeclared variable\nint x = 10;\ny = 20;\nreturn x + y;`,
  duplicate: `// Semantic Error: Duplicate declaration\nint count = 0;\nint count = 5;\nreturn count;`,
  syntax_err: `// Syntax Error: Missing semicolon\nint x = 10\nint y = 20;\nreturn x + y;`
};

export default function Editor({ code, setCode, onValidate, isLoading }) {
  const handleExampleChange = (e) => {
    const val = e.target.value;
    if (val && EXAMPLES[val]) {
      setCode(EXAMPLES[val]);
      e.target.value = '';
    }
  };

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      onValidate();
    }
  };

  return (
    <div className="left-panel">
      <div className="panel-header">
        <span>Source Editor</span>
        <div className="dot-row">
          <div className="dot dot-red"></div>
          <div className="dot dot-yellow"></div>
          <div className="dot dot-green"></div>
        </div>
      </div>
      <div id="editor-container">
        <textarea
          id="code-input"
          spellCheck="false"
          placeholder="// Enter Mini-C code here..."
          value={code}
          onChange={(e) => setCode(e.target.value)}
          onKeyDown={handleKeyDown}
        />
      </div>
      <div className="editor-footer">
        <select 
          className="example-select" 
          defaultValue="" 
          onChange={handleExampleChange} 
          title="Load example"
        >
          <option value="" disabled>Load example…</option>
          <option value="hello">Hello World</option>
          <option value="arithmetic">Arithmetic</option>
          <option value="if_else">If / Else</option>
          <option value="while_loop">While Loop</option>
          <option value="undeclared">⚠ Undeclared Var</option>
          <option value="duplicate">⚠ Duplicate Decl</option>
          <option value="syntax_err">⚠ Syntax Error</option>
        </select>
        <button 
          id="validate-btn" 
          onClick={onValidate} 
          className={isLoading ? 'loading' : ''}
          disabled={isLoading}
        >
          {isLoading ? <div className="spinner"></div> : <span className="btn-icon">▶</span>}
          {isLoading ? ' Compiling…' : ' Validate'}
        </button>
      </div>
    </div>
  );
}
