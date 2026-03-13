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
        <div class="mb-4">
            <label class="block mb-2 text-cyber-text text-sm">
                Lien ressource <span class="text-cyber-text-lighter text-xs">(optionnel — affiché après la question)</span>
            </label>
            <div class="flex gap-2 items-center">
                <input type="url"
                       name="question_link_url_${qIndex}"
                       class="input-cyber flex-1"
                       placeholder="https://..."
                       oninput="updateLinkPreview(${qIndex})">
                <input type="text"
                       name="question_link_label_${qIndex}"
                       class="input-cyber w-48"
                       placeholder="Texte du lien">
                <button type="button" onclick="clearLink(${qIndex})"
                        title="Supprimer le lien"
                        class="flex-shrink-0 px-2 py-1 text-red-400 hover:text-red-300 text-sm transition-colors">
                    ✕
                </button>
            </div>
            <span id="link_preview_${qIndex}"
                  class="hidden mt-1 block text-xs text-cyber-text-lighter break-all"></span>
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

function updateLinkPreview(qIndex) {
    const urlInput = document.querySelector(`input[name="question_link_url_${qIndex}"]`);
    const preview = document.getElementById('link_preview_' + qIndex);
    if (!urlInput || !preview) return;
    const val = urlInput.value.trim();
    if (val) {
        preview.textContent = val;
        preview.classList.remove('hidden');
    } else {
        preview.textContent = '';
        preview.classList.add('hidden');
    }
}

function clearLink(qIndex) {
    const urlInput = document.querySelector(`input[name="question_link_url_${qIndex}"]`);
    const labelInput = document.querySelector(`input[name="question_link_label_${qIndex}"]`);
    if (urlInput) urlInput.value = '';
    if (labelInput) labelInput.value = '';
    updateLinkPreview(qIndex);
}

function addResponse(qIndex) {
    const responsesDiv = document.getElementById('responses_' + qIndex);
    const rIndex = responsesDiv.children.length;

    const responseRow = document.createElement('div');
    responseRow.className = 'mb-3 p-3 border border-cyber-border rounded';

    responseRow.innerHTML = `
        <input type="hidden" name="response_exists_${qIndex}_${rIndex}" value="1">
        <div class="flex items-center gap-3 mb-2">
            <input type="radio"
                   name="correct_${qIndex}"
                   value="${rIndex}"
                   class="w-4 h-4 accent-green-400 cursor-pointer flex-shrink-0"
                   title="Marquer comme bonne réponse"
                   ${rIndex === 0 ? 'checked' : ''}>
            <input type="text"
                   name="response_text_${qIndex}_${rIndex}"
                   class="input-cyber flex-1"
                   placeholder="Texte (optionnel si image)">
            <button type="button" onclick="this.closest('.mb-3').remove()"
                    class="px-2 py-1 text-red-400 hover:text-red-300 text-sm transition-colors flex-shrink-0">
                ✕
            </button>
        </div>
        <div class="ml-7">
            <input type="file"
                   name="response_image_${qIndex}_${rIndex}"
                   accept="image/png,image/jpeg,image/gif,image/webp"
                   class="block w-full text-cyber-text text-sm file:mr-4 file:py-1 file:px-3 file:rounded file:border file:border-cyber-border file:bg-transparent file:text-cyber-text-lighter file:cursor-pointer hover:file:border-cyber-accent"
                   onchange="previewImage(this, 'resp_preview_${qIndex}_${rIndex}', 'resp_clear_${qIndex}_${rIndex}')">
            <button type="button"
                    id="resp_clear_${qIndex}_${rIndex}"
                    onclick="clearResponseImage(${qIndex}, ${rIndex})"
                    class="hidden mt-1 text-xs text-red-400 hover:text-red-300 transition-colors">
                ✕ Supprimer l'image
            </button>
            <img id="resp_preview_${qIndex}_${rIndex}" src="" alt="aperçu" class="hidden mt-2 max-h-32 rounded border border-cyber-border">
        </div>
    `;

    responsesDiv.appendChild(responseRow);
}

function clearResponseImage(qIndex, rIndex) {
    const fileInput = document.querySelector(`input[name="response_image_${qIndex}_${rIndex}"]`);
    if (fileInput) {
        fileInput.value = '';
        // Certains navigateurs ne permettent pas de vider un input file directement
        if (fileInput.value) {
            const clone = fileInput.cloneNode(true);
            fileInput.parentNode.replaceChild(clone, fileInput);
        }
    }
    const preview = document.getElementById(`resp_preview_${qIndex}_${rIndex}`);
    if (preview) {
        preview.src = '';
        preview.classList.add('hidden');
    }
    const clearBtn = document.getElementById(`resp_clear_${qIndex}_${rIndex}`);
    if (clearBtn) clearBtn.classList.add('hidden');
}

// Affiche un aperçu de l'image sélectionnée avant upload
function previewImage(input, previewId, clearBtnId) {
    const preview = document.getElementById(previewId);
    const clearBtn = clearBtnId ? document.getElementById(clearBtnId) : null;
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.classList.remove('hidden');
        };
        reader.readAsDataURL(input.files[0]);
        if (clearBtn) clearBtn.classList.remove('hidden');
    } else {
        preview.src = '';
        preview.classList.add('hidden');
        if (clearBtn) clearBtn.classList.add('hidden');
    }
}

// Ajouter une première question au chargement (sauf si le template d'édition gère le chargement)
document.addEventListener('DOMContentLoaded', function () {
    if (typeof existingQuestions === 'undefined') {
        addQuestion();
    }
});
