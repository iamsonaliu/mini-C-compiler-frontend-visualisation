import React, { useState, useEffect, useCallback } from 'react';
import Editor from './components/Editor';
import ResultsPanel from './components/ResultsPanel';

function App() {
  const [code, setCode] = useState(() => {
    return `// Rich Mini-C Demo (Functions, Loops, Pointers, Arrays)\nint add(int a, int b) {\n    return a + b;\n}\n\nint main() {\n    int arr[3];\n    arr[0] = 10;\n    arr[1] = 20;\n\n    int sum = 0;\n    for (int i = 0; i < 2; i++) {\n        sum = add(sum, arr[i]);\n    }\n\n    int *p = &sum;\n    *p += 5;\n\n    printf("Total sum: %d", sum);\n    return sum;\n}`;
  });
  
  const [compilationData, setCompilationData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Split-resizer state
  const [editorWidth, setEditorWidth] = useState(450);
  const [isResizing, setIsResizing] = useState(false);

  const startResizing = useCallback((e) => {
    e.preventDefault();
    setIsResizing(true);
    document.body.classList.add('is-resizing');
  }, []);

  const stopResizing = useCallback(() => {
    setIsResizing(false);
    document.body.classList.remove('is-resizing');
  }, []);

  const resize = useCallback((e) => {
    if (isResizing) {
      const minWidth = 280;
      const maxWidth = window.innerWidth * 0.8;
      const newWidth = Math.max(minWidth, Math.min(e.clientX, maxWidth));
      setEditorWidth(newWidth);
    }
  }, [isResizing]);

  useEffect(() => {
    if (isResizing) {
      window.addEventListener('mousemove', resize);
      window.addEventListener('mouseup', stopResizing);
    }
    return () => {
      window.removeEventListener('mousemove', resize);
      window.removeEventListener('mouseup', stopResizing);
    };
  }, [isResizing, resize, stopResizing]);

  const handleValidate = async () => {
    if (!code.trim()) return;
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch('http://localhost:5000/api/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });
      if (!res.ok) throw new Error('Network error');
      const data = await res.json();
      setCompilationData(data);
    } catch (err) {
      console.error(err);
      setErrorMsg('✗ Network error — is the backend running?');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <div className="logo">
          <div className="logo-icon">C</div>
          <div className="logo-text">Mini-<span>C</span> Compiler</div>
        </div>
        <div className="badge">FRONT-END VISUALIZER</div>
        <div className="header-sep"></div>
        <div className="badge">v2.0 (React)</div>
      </header>
      
      <div className="main" style={{ gridTemplateColumns: `${editorWidth}px 6px 1fr` }}>
        <Editor 
          code={code} 
          setCode={setCode} 
          onValidate={handleValidate} 
          isLoading={isLoading} 
        />
        <div 
          className={`resizer-bar ${isResizing ? 'resizing' : ''}`} 
          onMouseDown={startResizing} 
        />
        <ResultsPanel 
          data={compilationData} 
          errorMsg={errorMsg}
        />
      </div>
    </div>
  );
}

export default App;
