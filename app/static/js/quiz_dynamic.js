document.getElementById('quizForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const correctAnswers = JSON.parse(document.getElementById('quizData').dataset.answers);
    const quizId = document.getElementById('quizData').dataset.quizId;

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
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                answers: userAnswers,
                score: score,
                totalQuestions: totalQuestions
            })
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

        // Afficher les resultats
        const percentage = (score / totalQuestions) * 100;
        document.getElementById('score').textContent = `${score}/${totalQuestions} (${percentage.toFixed(0)}%)`;

        let message = '';
        if (percentage === 100) {
            message = 'Parfait ! Score maximum !';
        } else if (percentage >= 70) {
            message = 'Très bien ! Vous avez de bonnes connaissances.';
        } else if (percentage >= 50) {
            message = 'Pas mal ! Continuez à vous former.';
        } else {
            message = 'Il est recommandé de revoir les concepts abordés.';
        }

        document.getElementById('message').textContent = message;
        document.getElementById('results').classList.remove('hidden');
        document.getElementById('quizForm').style.display = 'none';
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Erreur:', error);
        alert('Une erreur est survenue lors de la validation du quiz: ' + error.message);
    }
});
