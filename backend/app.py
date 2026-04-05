from flask import Flask, request, jsonify, render_template
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import parse
from semantic import SemanticAnalyzer

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'react-frontend', 'dist'),
    static_url_path='/'
)

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/compile', methods=['POST', 'OPTIONS'])
def compile_code():
    if request.method == 'OPTIONS':
        return '', 204
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({'error': 'No code provided'}), 400

    code = data['code']

    # Phase 1+2: Lex + Parse
    tree, syn_errors, lex_errors = parse(code)

    from lexer import tokenize
    tokens_list, _ = tokenize(code)

    # Phase 3: Semantic
    analyzer = SemanticAnalyzer()
    sem_errors, sem_warnings, symbol_table = analyzer.analyze(tree)

    all_errors = lex_errors + syn_errors + sem_errors
    status = 'success' if not all_errors else 'error'

    if not all_errors:
        msg = ' Code is syntactically and semantically correct!'
        if sem_warnings:
            msg += f' ({len(sem_warnings)} warning(s))'
    else:
        parts = []
        if lex_errors: parts.append(f"{len(lex_errors)} lexical error(s)")
        if syn_errors: parts.append(f"{len(syn_errors)} syntax error(s)")
        if sem_errors: parts.append(f"{len(sem_errors)} semantic error(s)")
        msg = 'Compilation failed: ' + ', '.join(parts)

    return jsonify({
        'tokens':            tokens_list,
        'lexical_errors':    lex_errors,
        'syntax_errors':     syn_errors,
        'parse_tree':        tree.to_dict() if tree else None,
        'semantic_errors':   sem_errors,
        'semantic_warnings': sem_warnings,
        'symbol_table':      symbol_table,
        'status':            status,
        'total_errors':      len(all_errors),
        'total_warnings':    len(sem_warnings),
        'final_message':     msg,
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)