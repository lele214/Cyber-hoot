/* JS POUR LES QUIZ */

// Réponses correctes
const correctAnswers = {
    q1: 'b',  // Méthode qui manipule les personnes
    q2: 'b',  // Technique pour tromper via faux e-mails
    q3: 'c',  // Supprimer et contacter banque
    q4: 'a',  // Phishing par téléphone
    q5: 'b',  // Menacer de bloquer un compte
    q6: 'a',  // Phishing par SMS
    q7: 'b',  // Fautes, adresse suspecte, urgence
    q8: 'c',  // Formation et sensibilisation
    q9: 'b',  // Refuser et vérifier
    q10: 'b'  // Plusieurs preuves d'identité
};

document.getElementById('quizForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    let score = 0;
    const totalQuestions = Object.keys(correctAnswers).length;

    // Collecter les réponses de l'utilisateur
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

    // Envoyer les réponses au backend (nécessite d'être connecté)
    try {
        const response = await fetch('/quiz/1/submit', {
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
            // Si l'utilisateur n'est pas connecté (401)
            if (response.status === 401) {
                alert(data.error + '\n\nVous allez être redirigé vers la page de connexion.');
                window.location.href = data.redirect;
                return;
            }
            throw new Error(data.error || 'Erreur lors de la soumission du quiz');
        }

        // Si succès, afficher les résultats
        const percentage = (score / totalQuestions) * 100;
        document.getElementById('score').textContent = `${score}/${totalQuestions} (${percentage.toFixed(0)}%)`;

        let message = '';
        if (percentage === 100) {
            message = 'Parfait ! Vous maîtrisez parfaitement les bases de la protection contre l\'ingénierie sociale.';
        } else if (percentage >= 70) {
            message = 'Très bien ! Vous avez de bonnes connaissances sur le sujet.';
        } else if (percentage >= 50) {
            message = 'Pas mal ! Continuez à vous former pour améliorer vos compétences.';
        } else {
            message = 'Il est recommandé de revoir les concepts de base de l\'ingénierie sociale.';
        }

        document.getElementById('message').textContent = message;
        document.getElementById('results').classList.remove('hidden');
        document.getElementById('quizForm').style.display = 'none';

        // Scroll vers les résultats
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Erreur:', error);
        alert('Une erreur est survenue lors de la validation du quiz: ' + error.message);
    }
});