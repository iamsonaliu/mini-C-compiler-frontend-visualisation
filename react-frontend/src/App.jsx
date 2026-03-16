import React, { useState } from 'react';
import Editor from './components/Editor';
import ResultsPanel from './components/ResultsPanel';

function App() {
  const [code, setCode] = useState(() => {
    return `// While Loop\nint i = 0;\nint sum = 0;\nwhile (i < 10) {\n    sum = sum + i;\n    i = i + 1;\n}\nreturn sum;`;
  });
  
  const [compilationData, setCompilationData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

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
      
      <div className="main">
        <Editor 
          code={code} 
          setCode={setCode} 
          onValidate={handleValidate} 
          isLoading={isLoading} 
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
