/* JS POUR LA CRÉATION DE QUIZ */

let questionCount = 0;

function addQuestion() {
    const container = document.getElementById('questionsContainer');
    const qIndex = questionCount;

    const questionBlock = document.createElement('div');
    questionBlock.className = 'mb-6 p-4 border border-cyber-border rounded-lg';
    questionBlock.id = 'question_block_' + qIndex;

    questionBlock.innerHTML = `
        <div class="flex justify-between items-center mb-3">
            <h3 class="text-cyber-text-lighter font-semibold">Question ${qIndex + 1}</h3>
            <button type="button" onclick="removeQuestion(${qIndex})"
                    class="px-3 py-1 text-red-400 border border-red-400 rounded text-sm hover:bg-red-400 hover:text-white transition-all duration-200">
                Supprimer
            </button>
        </div>
        <div class="mb-4">
            <input type="text"
                   name="question_text_${qIndex}"
                   class="input-cyber"
                   placeholder="Entrez votre question"
                   required>
        </div>
        <div class="mb-2">
            <label class="block mb-2 text-cyber-text text-sm">
                Réponses <span class="text-cyber-text-lighter text-xs">(cochez la bonne réponse)</span>
            </label>
            <div id="responses_${qIndex}">
            </div>
            <button type="button" onclick="addResponse(${qIndex})"
                    class="mt-2 px-3 py-1 bg-transparent border border-cyber-border text-cyber-text rounded text-sm hover:border-cyber-accent hover:text-cyber-text-lighter transition-all duration-200">
                + Ajouter une réponse
            </button>
        </div>
    `;

    container.appendChild(questionBlock);
    questionCount++;

    // Ajouter 2 réponses par défaut
    addResponse(qIndex);
    addResponse(qIndex);
}

function removeQuestion(qIndex) {
    const block = document.getElementById('question_block_' + qIndex);
    if (block) {
        block.remove();
    }
}

function addResponse(qIndex) {
    const responsesDiv = document.getElementById('responses_' + qIndex);
    const rIndex = responsesDiv.children.length;

    const responseRow = document.createElement('div');
    responseRow.className = 'flex items-center gap-3 mb-2';

    responseRow.innerHTML = `
        <input type="radio"
               name="correct_${qIndex}"
               value="${rIndex}"
               class="w-4 h-4 accent-green-400 cursor-pointer"
               title="Marquer comme bonne réponse"
               ${rIndex === 0 ? 'checked' : ''}>
        <input type="text"
               name="response_text_${qIndex}_${rIndex}"
               class="input-cyber flex-1"
               placeholder="Réponse ${rIndex + 1}"
               required>
        <button type="button" onclick="this.parentElement.remove()"
                class="px-2 py-1 text-red-400 hover:text-red-300 text-sm transition-colors">
            ✕
        </button>
    `;

    responsesDiv.appendChild(responseRow);
}

// Ajouter une première question au chargement (sauf si le template d'édition gère le chargement)
document.addEventListener('DOMContentLoaded', function () {
    if (typeof existingQuestions === 'undefined') {
        addQuestion();
    }
});
