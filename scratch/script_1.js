
            // === LÓGICA DEL LECTOR VIRTUAL ===
            let lectorChunks = [];
            let currentLectorIndex = 0;
            let currentUtterance = null;
            let isLectorPlaying = false;
            let lectorVoicesList = [];

            // Cargar voces disponibles (filtrando por español)
            function initLectorVoices() {
                lectorVoicesList = window.speechSynthesis.getVoices().filter(v => v.lang.startsWith('es'));
                const select = document.getElementById('lectorVoiceSelect');
                select.innerHTML = '';
                if(lectorVoicesList.length === 0) {
                    select.innerHTML = '<option value="">Predeterminada</option>';
                    return;
                }
                lectorVoicesList.forEach((voice, i) => {
                    const option = document.createElement('option');
                    option.value = i;
                    // Intentar identificar mujeres por nombre heurístico
                    const nameLow = voice.name.toLowerCase();
                    let icon = (nameLow.includes('female') || nameLow.includes('mujer') || nameLow.includes('paulina') || nameLow.includes('monica') || nameLow.includes('helena') || nameLow.includes('laura')) ? '👩 ' : '👨 ';
                    option.textContent = icon + voice.name.replace('Microsoft ', '').replace('Desktop', '').trim();
                    select.appendChild(option);
                });
            }

            if (speechSynthesis.onvoiceschanged !== undefined) {
                speechSynthesis.onvoiceschanged = initLectorVoices;
            }

            function updateLectorSettings() {
                const rate = parseFloat(document.getElementById('lectorSpeedRange').value);
                document.getElementById('lectorSpeedDisplay').textContent = rate + 'x';
                
                if (isLectorPlaying && currentUtterance) {
                    window.speechSynthesis.cancel();
                    playLectorChunk(currentLectorIndex);
                }
            }

            function startLectorVirtual(btnElem, title) {
                if(lectorVoicesList.length === 0) initLectorVoices();

                const accDiv = btnElem.closest('div[id^="acc_"]');
                const contentBody = accDiv.querySelector('.topic-content-body');
                if (!contentBody) return;

                // Extraer el texto preservando saltos de línea visuales como puntos y espacios
                let rawText = contentBody.innerText;
                if (!rawText) rawText = contentBody.textContent;
                
                // Limpiar espacios dobles pero mantener estructura básica
                const cleanText = rawText.replace(/\n+/g, '. ').replace(/\s+/g, ' ').trim();
                
                let rawChunks = cleanText.split('. ');
                lectorChunks = [];
                let tempChunk = "";
                
                for(let c of rawChunks) {
                    if(!c.trim()) continue;
                    if(tempChunk.length < 60) {
                        tempChunk += (tempChunk ? ". " : "") + c;
                    } else {
                        lectorChunks.push(tempChunk + ".");
                        tempChunk = c;
                    }
                }
                if(tempChunk) lectorChunks.push(tempChunk + (!tempChunk.endsWith('.') ? '.' : ''));

                if(lectorChunks.length === 0) {
                    alert("No hay texto legible en esta lección.");
                    return;
                }

                document.getElementById('lectorTitle').innerHTML = '🎧 ' + title;
                document.getElementById('lectorVirtualModal').style.display = 'flex';
                
                playLectorChunk(0);
            }

            function playLectorChunk(index) {
                if(index < 0 || index >= lectorChunks.length) {
                    isLectorPlaying = false;
                    document.getElementById('btnPausePlayLector').textContent = '▶️ Reiniciar';
                    return;
                }
                currentLectorIndex = index;
                
                const textContainer = document.getElementById('lectorTextContainer');
                textContainer.style.opacity = '0';
                setTimeout(() => {
                    textContainer.textContent = lectorChunks[index];
                    textContainer.style.opacity = '1';
                }, 150);

                document.getElementById('lectorProgress').textContent = (index + 1) + ' / ' + lectorChunks.length;
                
                window.speechSynthesis.cancel();
                
                currentUtterance = new SpeechSynthesisUtterance(lectorChunks[index]);
                currentUtterance.lang = 'es-ES';
                
                const rateElem = document.getElementById('lectorSpeedRange');
                const voiceElem = document.getElementById('lectorVoiceSelect');
                currentUtterance.rate = rateElem ? parseFloat(rateElem.value) : 0.95; 
                
                if (voiceElem && voiceElem.value !== "" && lectorVoicesList[voiceElem.value]) {
                    currentUtterance.voice = lectorVoicesList[voiceElem.value];
                }
                
                currentUtterance.onend = function(event) {
                    if(isLectorPlaying) {
                        setTimeout(() => playLectorChunk(currentLectorIndex + 1), 600);
                    }
                };
                
                isLectorPlaying = true;
                document.getElementById('btnPausePlayLector').textContent = '⏸️ Pausar';
                window.speechSynthesis.speak(currentUtterance);
            }

            function toggleLectorPause() {
                if(!currentUtterance) {
                    if(lectorChunks.length > 0) playLectorChunk(0);
                    return;
                }
                
                if(window.speechSynthesis.paused) {
                    window.speechSynthesis.resume();
                    isLectorPlaying = true;
                    document.getElementById('btnPausePlayLector').textContent = '⏸️ Pausar';
                } else if(window.speechSynthesis.speaking) {
                    window.speechSynthesis.pause();
                    isLectorPlaying = false;
                    document.getElementById('btnPausePlayLector').textContent = '▶️ Reanudar';
                } else {
                    playLectorChunk(currentLectorIndex);
                }
            }

            function lectorNext() {
                if(currentLectorIndex < lectorChunks.length - 1) {
                    playLectorChunk(currentLectorIndex + 1);
                }
            }

            function lectorPrev() {
                if(currentLectorIndex > 0) {
                    playLectorChunk(currentLectorIndex - 1);
                }
            }

            function closeLectorVirtual() {
                window.speechSynthesis.cancel();
                isLectorPlaying = false;
                document.getElementById('lectorVirtualModal').style.display = 'none';
            }
        