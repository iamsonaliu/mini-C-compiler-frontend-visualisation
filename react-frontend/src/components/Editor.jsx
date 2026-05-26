import React from 'react';

const EXAMPLES = {
  // --- Core / Basics ---
  hello: `// Hello World\nprintf("Hello, World!");\nreturn 0;`,
  arithmetic: `// Arithmetic expressions\nint a = 10;\nint b = 5;\nint sum = a + b;\nint diff = a - b;\nfloat ratio = 3.14;\nint product = a * b;`,
  
  // --- Control Flow ---
  if_else: `// If-Else Statement\nint score = 85;\nint grade = 0;\nif (score >= 90) {\n    grade = 1;\n} else {\n    grade = 0;\n}\nreturn grade;`,
  while_loop: `// While Loop\nint i = 0;\nint sum = 0;\nwhile (i < 10) {\n    sum = sum + i;\n    i = i + 1;\n}\nreturn sum;`,
  for_loop: `// For Loop & Compound Assignment\nint sum = 0;\nfor (int i = 1; i <= 10; i++) {\n    sum += i;\n}\nreturn sum;`,
  do_while: `// Do-While Loop\nint count = 0;\nint x = 10;\ndo {\n    x = x / 2;\n    count++;\n} while (x > 1);\nreturn count;`,
  switch_case: `// Switch Case Statement\nint x = 2;\nint result = 0;\nswitch (x) {\n    case 1:\n        result = 10;\n        break;\n    case 2:\n        result = 20;\n        break;\n    default:\n        result = 99;\n        break;\n}\nreturn result;`,
  loop_control: `// Break & Continue in Loops\nint sum = 0;\nfor (int i = 0; i < 10; i++) {\n    if (i % 2 == 0) {\n        continue;\n    }\n    if (i > 7) {\n        break;\n    }\n    sum += i;\n}\nreturn sum;`,

  // --- Advanced constructs ---
  functions: `// Function Definition & Calls\nint add(int a, int b) {\n    return a + b;\n}\n\nint main() {\n    int x = 10;\n    int y = 20;\n    int sum = add(x, y);\n    return sum;\n}`,
  arrays: `// Arrays & Subscripts\nint arr[5];\narr[0] = 100;\narr[1] = 200;\nint val = arr[0] + arr[1];\nreturn val;`,
  pointers: `// Pointers & Address-Of\nint x = 42;\nint *p = &x;\n*p = 100;\nreturn x;`,

  // --- Semantic Errors ---
  undeclared: `// Semantic Error: Undeclared variable\nint x = 10;\ny = 20;\nreturn x + y;`,
  duplicate: `// Semantic Error: Duplicate declaration\nint count = 0;\nint count = 5;\nreturn count;`,
  err_break: `// Semantic Error: break outside loop/switch\nint x = 10;\nbreak;\nreturn x;`,
  err_func_args: `// Semantic Error: Function call param mismatch\nint multiply(int a, int b) {\n    return a * b;\n}\n\nint main() {\n    int val = multiply(5);\n    return val;\n}`,
  err_return: `// Semantic Error: Return type mismatch\nint get_int() {\n    return; // returns void\n}`,
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
          
          <optgroup label="Core Basics">
            <option value="hello">Hello World</option>
            <option value="arithmetic">Arithmetic Expressions</option>
          </optgroup>
          
          <optgroup label="Control Flow">
            <option value="if_else">If / Else</option>
            <option value="while_loop">While Loop</option>
            <option value="for_loop">For Loop (Compound Ops)</option>
            <option value="do_while">Do-While Loop</option>
            <option value="switch_case">Switch Case Statement</option>
            <option value="loop_control">Break & Continue</option>
          </optgroup>
          
          <optgroup label="Advanced Constructs">
            <option value="functions">Functions & Calls</option>
            <option value="arrays">Arrays & Subscripts</option>
            <option value="pointers">Pointers & Address-Of</option>
          </optgroup>
          
          <optgroup label="Errors & Diagnostics">
            <option value="undeclared">⚠ Undeclared Variable</option>
            <option value="duplicate">⚠ Duplicate Declaration</option>
            <option value="err_break">⚠ Invalid break</option>
            <option value="err_func_args">⚠ Function param mismatch</option>
            <option value="err_return">⚠ Return type mismatch</option>
            <option value="syntax_err">⚠ Syntax Error</option>
          </optgroup>
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
