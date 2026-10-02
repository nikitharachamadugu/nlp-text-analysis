import os
from flask import Flask, render_template, request, jsonify
from nlp_engine import analyze_text

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nlp-text-analyzer-secret-key-2026')

@app.route('/')
def home():
    """Renders the main dashboard."""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint for Render monitoring."""
    return jsonify({"status": "healthy", "service": "nlp-text-analysis"}), 200


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint to analyze text."""
    try:
        data = request.get_json(silent=True) or request.form
        text = data.get('text', '')

        if not text or not text.strip():
            return jsonify({
                "error": "Please provide some text to analyze."
            }), 400

        # Safety length limit (e.g. 50,000 characters) to prevent memory issues on Render free tier
        if len(text) > 60000:
            text = text[:60000]

        results = analyze_text(text)
        return jsonify({
            "success": True,
            "data": results
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Analysis error: {str(e)}"
        }), 500


if __name__ == '__main__':
    # Render binds the port using the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1')
    app.run(host='0.0.0.0', port=port, debug=debug)
