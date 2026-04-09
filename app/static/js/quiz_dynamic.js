document.getElementById('quizForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const quizDataEl = document.getElementById('quizData');
    const correctAnswers = JSON.parse(quizDataEl.dataset.answers);
    const quizId = quizDataEl.dataset.quizId;
    const questions = JSON.parse(quizDataEl.dataset.questions);

    let score = 0;
    const totalQuestions = Object.keys(correctAnswers).length;

    // Collecter les reponses de l'utilisateur
    const userAnswers = {};
    for (let question in correctAnswers) {
        const selectedAnswer = document.querySelector(`input[name="${question}"]:checked`);
        if (selectedAnswer) {
            userAnswers[question] = selectedAnswer.value;
            if (selectedAnswer.value === correctAnswers[question]) {
                score++;
            }
        }
    }

    // Envoyer les reponses au backend
    try {
        const response = await fetch(`/quiz/${quizId}/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers: userAnswers, score: score, totalQuestions: totalQuestions })
        });

        const data = await response.json();

        if (!response.ok) {
            if (response.status === 401) {
                alert(data.error + '\n\nVous allez être redirigé vers la page de connexion.');
                window.location.href = data.redirect;
                return;
            }
            throw new Error(data.error || 'Erreur lors de la soumission du quiz');
        }

        // Score global
        const percentage = (score / totalQuestions) * 100;
        document.getElementById('score').textContent = `${score}/${totalQuestions} (${percentage.toFixed(0)}%)`;

        let message = '';
        if (percentage === 100) message = 'Parfait ! Score maximum !';
        else if (percentage >= 70) message = 'Très bien ! Vous avez de bonnes connaissances.';
        else if (percentage >= 50) message = 'Pas mal ! Continuez à vous former.';
        else message = 'Il est recommandé de revoir les concepts abordés.';
        document.getElementById('message').textContent = message;

        // Détail par question
        const detailContainer = document.getElementById('results-detail');
        detailContainer.innerHTML = '';

        questions.forEach((q, i) => {
            const key = `q${i}`;
            const userAnswer = userAnswers[key] !== undefined ? parseInt(userAnswers[key]) : null;
            const correctIndex = parseInt(correctAnswers[key]);
            const isCorrect = userAnswer === correctIndex;
            const unanswered = userAnswer === null;

            const borderColor = unanswered ? 'border-yellow-500' : (isCorrect ? 'border-green-500' : 'border-red-500');
            const bgColor = unanswered ? 'bg-yellow-900/20' : (isCorrect ? 'bg-green-900/20' : 'bg-red-900/20');
            const icon = unanswered ? '⚠️' : (isCorrect ? '✅' : '❌');
            const statusText = unanswered ? 'Sans réponse' : (isCorrect ? 'Correct' : 'Incorrect');
            const statusColor = unanswered ? 'text-yellow-400' : (isCorrect ? 'text-green-400' : 'text-red-400');

            const userResponseText = (userAnswer !== null && q.responses[userAnswer])
                ? q.responses[userAnswer].text : '—';
            const correctResponseText = q.responses[correctIndex] ? q.responses[correctIndex].text : '—';

            const correctAnswerHtml = (!isCorrect || unanswered)
                ? `<div class="mb-2">
                    <p class="text-sm"><span class="text-cyber-text-muted">Bonne réponse : </span><span class="text-green-400">${correctResponseText}</span></p>
                   </div>`
                : '';

            const explanationBody = q.explanation
                ? `<div class="mt-2 pt-2 border-t border-cyber-border">
                    <p class="text-cyber-text-muted text-xs uppercase tracking-widest mb-1">Explication</p>
                    <p class="text-cyber-text text-sm leading-relaxed">${q.explanation}</p>
                   </div>`
                : '';

            const hasSolution = (!isCorrect || unanswered || q.explanation);
            const solutionHtml = hasSolution
                ? `<div id="exp-${i}" class="hidden mt-3">${correctAnswerHtml}${explanationBody}</div>`
                : '';

            const wrongAnswerHtml = (!isCorrect && !unanswered)
                ? `<p class="text-sm mt-1"><span class="text-cyber-text-muted">Votre réponse : </span><span class="text-red-400">${userResponseText}</span></p>`
                : '';

            detailContainer.innerHTML += `
                <div class="border ${borderColor} ${bgColor} rounded-lg p-5">
                    <div class="flex-1">
                        <p class="text-cyber-text-lighter font-semibold mb-1">
                            ${icon} Question ${i + 1} — <span class="${statusColor}">${statusText}</span>
                        </p>
                        <p class="text-cyber-text text-sm mb-2">${q.text}</p>
                        ${wrongAnswerHtml}
                    </div>
                    ${solutionHtml}
                </div>
            `;
        });

        document.getElementById('quizForm').style.display = 'none';
        document.getElementById('results').classList.remove('hidden');
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Erreur:', error);
        alert('Une erreur est survenue lors de la validation du quiz: ' + error.message);
    }
});

function toggleAllSolutions() {
    const btn = document.getElementById('btn-all-solutions');
    const boxes = document.querySelectorAll('[id^="exp-"]');
    const allHidden = [...boxes].every(b => b.classList.contains('hidden'));
    boxes.forEach(b => b.classList.toggle('hidden', !allHidden));
    btn.textContent = allHidden ? 'Masquer ▲' : 'Voir toutes les solutions ▼';
}

// Attacher les listeners des boutons résultats — aucun onclick inline (conformité CSP)
document.getElementById('btn-all-solutions').addEventListener('click', toggleAllSolutions);
document.getElementById('btn-restart').addEventListener('click', function () {
    window.location.reload();
});
