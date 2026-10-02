/**
 * TextPulse NLP - Client Application Controller
 * Handles interactive NLP analysis, Chart.js rendering, live counters,
 * sample presets, and reporting.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const inputText = document.getElementById('input-text');
    const analyzeBtn = document.getElementById('analyze-btn');
    const clearBtn = document.getElementById('clear-btn');
    const fileUpload = document.getElementById('file-upload');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorAlert = document.getElementById('error-alert');
    const errorMessage = document.getElementById('error-message');
    const resultsDashboard = document.getElementById('results-dashboard');
    const toast = document.getElementById('toast');

    // Live counter elements
    const liveWordCount = document.getElementById('live-word-count');
    const liveCharCount = document.getElementById('live-char-count');
    const liveReadingTime = document.getElementById('live-reading-time');

    // Sample Texts Library
    const sampleTexts = {
        positive: `The new cloud infrastructure update exceeded all our expectations! The deployment process was remarkably fast, silky smooth, and completely painless. Our engineering team observed an immediate 40% reduction in response latency, and the intuitive web dashboard makes monitoring microservices a sheer delight. We are thoroughly impressed and wholeheartedly recommend this solution to anyone building scalable modern applications. Excellent work by the entire developer platform team!`,
        
        critical: `I am deeply disappointed with the latest software release. Our production system suffered severe downtime for over three hours yesterday due to an unexpected memory leak. The documentation is confusing, outdated, and lacks essential configuration examples. Furthermore, reaching customer support was a frustrating ordeal with delayed responses and unhelpful answers. This has caused significant problems for our enterprise clients, and we urgently demand an immediate bug fix.`,
        
        tech: `Modern natural language processing has evolved rapidly with transformer architectures, dynamic self-attention mechanisms, and scalable vector databases. Cloud native environments like Render, Kubernetes, and serverless containers enable rapid continuous integration and automated deployment pipelines. Engineers must continuously balance algorithmic inference speed, memory allocation limits, and readability to deliver robust, high-performance web APIs for end users worldwide.`,
        
        academic: `This paper investigates computational semantic representations derived from unsupervised neural language modeling. By applying syntactic parsing and lexical frequency matrices, we observe statistically significant correlations between corpus complexity and reader comprehension levels. Experimental evaluations across multidimensional benchmarks indicate that hybrid neural-symbolic architectures maintain high predictive accuracy while mitigating sample variance.`
    };

    let posChartInstance = null;
    let currentAnalysisData = null;

    // Toast notification helper
    function showToast(msg) {
        toast.textContent = msg;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 2800);
    }

    // Live word and character counting
    function updateLiveCounters() {
        const text = inputText.value;
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        const chars = text.length;
        const estSec = Math.ceil((words / 200) * 60);

        liveWordCount.textContent = words.toLocaleString();
        liveCharCount.textContent = chars.toLocaleString();
        liveReadingTime.textContent = estSec >= 60 ? `${Math.ceil(estSec / 60)}m` : `${estSec}s`;
    }

    inputText.addEventListener('input', updateLiveCounters);

    // Sample buttons
    document.querySelectorAll('.pill-btn[data-sample]').forEach(btn => {
        btn.addEventListener('click', () => {
            const key = btn.getAttribute('data-sample');
            if (sampleTexts[key]) {
                inputText.value = sampleTexts[key];
                updateLiveCounters();
                triggerAnalysis();
            }
        });
    });

    // Clear button
    clearBtn.addEventListener('click', () => {
        inputText.value = '';
        updateLiveCounters();
        resultsDashboard.style.display = 'none';
        errorAlert.style.display = 'none';
        inputText.focus();
    });

    // File upload handler
    fileUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            inputText.value = event.target.result;
            updateLiveCounters();
            triggerAnalysis();
            showToast(`Loaded ${file.name}`);
        };
        reader.readAsText(file);
    });

    // Keyboard shortcut (Ctrl+Enter or Cmd+Enter)
    inputText.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            triggerAnalysis();
        }
    });

    analyzeBtn.addEventListener('click', triggerAnalysis);

    // Analysis Pipeline Trigger
    async function triggerAnalysis() {
        const text = inputText.value.trim();
        if (!text) {
            showError('Please enter or select some text before analyzing.');
            return;
        }

        hideError();
        setLoading(true);

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            const result = await response.json();
            if (!response.ok || !result.success) {
                throw new Error(result.error || 'Failed to analyze text.');
            }

            currentAnalysisData = result.data;
            renderResults(result.data);
            resultsDashboard.style.display = 'block';
            resultsDashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } catch (err) {
            showError(err.message || 'An unexpected error occurred while analyzing.');
        } finally {
            setLoading(false);
        }
    }

    function setLoading(isLoading) {
        if (isLoading) {
            loadingIndicator.style.display = 'flex';
            analyzeBtn.disabled = true;
            document.getElementById('analyze-spinner').style.display = 'inline-block';
        } else {
            loadingIndicator.style.display = 'none';
            analyzeBtn.disabled = false;
            document.getElementById('analyze-spinner').style.display = 'none';
        }
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        errorAlert.style.display = 'flex';
    }

    function hideError() {
        errorAlert.style.display = 'none';
    }

    // Render Dashboard Results
    function renderResults(data) {
        // Top Ribbon Stats
        document.getElementById('stat-words').textContent = data.stats.word_count.toLocaleString();
        document.getElementById('stat-chars').textContent = data.stats.char_count.toLocaleString();
        document.getElementById('stat-sentences').textContent = data.stats.sentence_count.toLocaleString();
        document.getElementById('stat-reading').textContent = data.readability.reading_time_text;
        document.getElementById('stat-speaking').textContent = data.readability.speaking_time_text;

        // Sentiment Card
        const sentiment = data.sentiment;
        const scoreEl = document.getElementById('sentiment-score');
        scoreEl.textContent = (sentiment.polarity >= 0 ? '+' : '') + sentiment.polarity.toFixed(2);
        scoreEl.style.color = sentiment.color;

        const badgeEl = document.getElementById('sentiment-badge');
        badgeEl.textContent = sentiment.label;
        badgeEl.style.backgroundColor = `${sentiment.color}25`;
        badgeEl.style.borderColor = `${sentiment.color}60`;
        badgeEl.style.color = sentiment.color;

        document.getElementById('sentiment-mood').textContent = sentiment.mood;
        document.getElementById('sentiment-subjectivity').textContent = `${Math.round(sentiment.subjectivity * 100)}%`;

        // Polarity Meter Slider (-1.0 to 1.0 mapped to 0% to 100%)
        const meterPercent = ((sentiment.polarity + 1.0) / 2.0) * 100;
        document.getElementById('meter-fill').style.left = `${Math.max(5, Math.min(95, meterPercent))}%`;

        // Sentence Sentiments Timeline
        const sentenceListEl = document.getElementById('sentence-list');
        sentenceListEl.innerHTML = '';
        if (data.sentence_sentiments && data.sentence_sentiments.length > 0) {
            data.sentence_sentiments.forEach((s) => {
                const item = document.createElement('div');
                item.className = 'sentence-item';
                item.style.borderLeftColor = s.color;

                const scoreBadge = document.createElement('span');
                scoreBadge.className = 's-score';
                scoreBadge.style.color = s.color;
                scoreBadge.textContent = (s.polarity >= 0 ? '+' : '') + s.polarity.toFixed(2);

                item.textContent = s.text;
                item.appendChild(scoreBadge);
                sentenceListEl.appendChild(item);
            });
        } else {
            sentenceListEl.innerHTML = '<div style="color:var(--text-muted);font-size:0.86rem;">No full sentences detected.</div>';
        }

        // Readability
        const readability = data.readability;
        document.getElementById('flesch-score').textContent = readability.flesch_reading_ease.toFixed(1);
        document.getElementById('readability-badge').textContent = readability.reading_ease_level;
        document.getElementById('flesch-fill').style.width = `${Math.min(100, Math.max(5, readability.flesch_reading_ease))}%`;

        document.getElementById('fk-grade').textContent = `Grade ${readability.flesch_kincaid_grade}`;
        document.getElementById('cli-score').textContent = readability.coleman_liau.toFixed(1);
        document.getElementById('ari-score').textContent = readability.ari.toFixed(1);
        document.getElementById('avg-sent-len').textContent = `${readability.avg_sentence_len} words`;
        document.getElementById('avg-syllables').textContent = `${readability.avg_syllables_per_word}`;

        // Keywords
        const keywordsListEl = document.getElementById('keywords-list');
        keywordsListEl.innerHTML = '';
        if (data.keywords && data.keywords.length > 0) {
            data.keywords.forEach((kw) => {
                const row = document.createElement('div');
                row.className = 'keyword-row';

                row.innerHTML = `
                    <span class="keyword-name">${escapeHtml(kw.word)}</span>
                    <div class="keyword-bar-container">
                        <div class="keyword-bar">
                            <div class="keyword-bar-fill" style="width: ${kw.percentage}%;"></div>
                        </div>
                        <span class="keyword-count">${kw.count} &bull; ${kw.percentage}%</span>
                    </div>
                `;
                keywordsListEl.appendChild(row);
            });
        } else {
            keywordsListEl.innerHTML = '<div style="color:var(--text-muted);font-size:0.86rem;">No recurring keywords extracted.</div>';
        }

        // POS Chart
        renderPosChart(data.pos);

        // Extractive Summary
        document.getElementById('summary-content').textContent = data.summary || 'Summary unavailable for short text.';

        // Entities & Patterns
        renderEntities(data.entities);
    }

    // Chart.js Part-of-Speech Rendering
    function renderPosChart(posData) {
        const ctx = document.getElementById('posChart').getContext('2d');
        if (posChartInstance) {
            posChartInstance.destroy();
        }

        const labels = Object.keys(posData);
        const values = Object.values(posData);

        posChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        '#6366f1', // Nouns (Indigo)
                        '#10b981', // Verbs (Emerald)
                        '#06b6d4', // Adjectives (Cyan)
                        '#f59e0b', // Adverbs (Amber)
                        '#64748b'  // Other (Slate)
                    ],
                    borderColor: '#111827',
                    borderWidth: 2,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#94a3b8',
                            font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
                            padding: 14
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleColor: '#fff',
                        bodyColor: '#cbd5e1',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderWidth: 1
                    }
                },
                cutout: '68%'
            }
        });
    }

    // Render Entities
    function renderEntities(entities) {
        const container = document.getElementById('entities-container');
        container.innerHTML = '';

        const allEntities = [
            ...(entities.urls || []).map(u => ({ icon: '🔗', label: u })),
            ...(entities.emails || []).map(e => ({ icon: '✉️', label: e })),
            ...(entities.phone_numbers || []).map(p => ({ icon: '📞', label: p })),
            ...(entities.hashtags || []).map(h => ({ icon: '#️⃣', label: h })),
            ...(entities.mentions || []).map(m => ({ icon: '@', label: m })),
            ...(entities.named_entities || []).map(n => ({ icon: '👤', label: n }))
        ];

        if (allEntities.length === 0) {
            container.innerHTML = '<div style="color:var(--text-muted);font-size:0.86rem;">No special entities or named expressions detected.</div>';
            return;
        }

        allEntities.forEach(ent => {
            const tag = document.createElement('span');
            tag.className = 'entity-tag';
            tag.innerHTML = `<span class="entity-tag-icon">${ent.icon}</span> <span>${escapeHtml(ent.label)}</span>`;
            container.appendChild(tag);
        });
    }

    // Tab Switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const targetContent = document.getElementById(tabId);
            if (targetContent) targetContent.classList.add('active');
        });
    });

    // Copy Summary Action
    document.getElementById('copy-summary-btn').addEventListener('click', () => {
        const summary = document.getElementById('summary-content').textContent;
        navigator.clipboard.writeText(summary);
        showToast('Summary copied to clipboard!');
    });

    // Export JSON
    document.getElementById('export-json-btn').addEventListener('click', () => {
        if (!currentAnalysisData) return;
        const blob = new Blob([JSON.stringify(currentAnalysisData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `nlp-analysis-${new Date().toISOString().slice(0, 10)}.json`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('JSON report downloaded!');
    });

    // Copy Markdown Report
    document.getElementById('copy-report-btn').addEventListener('click', () => {
        if (!currentAnalysisData) return;
        const d = currentAnalysisData;
        const report = `# NLP Text Analysis Report
Generated: ${new Date().toLocaleString()}

## Core Statistics
- Total Words: ${d.stats.word_count}
- Characters: ${d.stats.char_count}
- Sentences: ${d.stats.sentence_count}
- Reading Time: ${d.readability.reading_time_text}
- Speaking Time: ${d.readability.speaking_time_text}

## Sentiment & Tone
- Overall Sentiment: ${d.sentiment.label} (Polarity: ${d.sentiment.polarity})
- Mood: ${d.sentiment.mood}
- Subjectivity: ${Math.round(d.sentiment.subjectivity * 100)}%

## Readability & Complexity
- Flesch Reading Ease: ${d.readability.flesch_reading_ease} (${d.readability.reading_ease_level})
- Flesch-Kincaid Grade Level: Grade ${d.readability.flesch_kincaid_grade}
- Coleman-Liau Index: ${d.readability.coleman_liau}

## Extractive Summary
${d.summary}
`;
        navigator.clipboard.writeText(report);
        showToast('Markdown report copied to clipboard!');
    });

    function escapeHtml(str) {
        return str.replace(/[&<>"']/g, function(m) {
            return {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#39;'
            }[m];
        });
    }

    // Initial counter update
    updateLiveCounters();
});
