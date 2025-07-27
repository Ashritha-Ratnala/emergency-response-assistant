// Global variables
let isRecording = false;
let recognition = null;
let currentLocation = null;
let transcriptText = '';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeSpeechRecognition();
    updateStatus('ready', '🟢 Ready', 'Click the microphone to report an emergency');
});

// Initialize Speech Recognition
function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        recognition.maxAlternatives = 1;

        recognition.onstart = function() {
            updateStatus('recording', '🔴 Recording', 'Listening for emergency report... Speak clearly');
        };

        recognition.onresult = function(event) {
            let interim_transcript = '';
            let final_transcript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    final_transcript += transcript;
                } else {
                    interim_transcript += transcript;
                }
            }

            transcriptText = final_transcript || interim_transcript;
            updateTranscript(transcriptText, !event.results[event.results.length - 1].isFinal);
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            updateStatus('error', '❌ Error', `Speech recognition failed: ${event.error}`);
            stopRecording();
        };

        recognition.onend = function() {
            if (isRecording) {
                updateStatus('ready', '🟢 Ready', 'Recording stopped. Click Process Emergency if ready.');
            }
            isRecording = false;
            updateMicButton();
        };
    } else {
        updateStatus('error', '❌ Not Supported', 'Speech recognition not supported in this browser');
        document.getElementById('micButton').disabled = true;
    }
}

// Toggle recording
function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

// Start recording
function startRecording() {
    if (recognition && !isRecording) {
        isRecording = true;
        recognition.start();
        updateMicButton();
    }
}

// Stop recording
function stopRecording() {
    if (recognition && isRecording) {
        isRecording = false;
        recognition.stop();
        updateMicButton();
    }
}

// Update microphone button
function updateMicButton() {
    const micButton = document.getElementById('micButton');
    const micIcon = document.getElementById('micIcon');
    const micText = document.getElementById('micText');

    if (isRecording) {
        micButton.classList.add('recording');
        micIcon.textContent = '⏹️';
        micText.textContent = 'Stop Recording';
    } else {
        micButton.classList.remove('recording');
        micIcon.textContent = '🎤';
        micText.textContent = 'Start Recording';
    }
}

// Update transcript display
function updateTranscript(text, isInterim = false) {
    const transcriptBox = document.getElementById('transcript');
    
    if (text.trim()) {
        transcriptBox.innerHTML = `<p>${text}</p>`;
        transcriptBox.classList.add('has-content');
        
        // Enable process button if we have content
        document.getElementById('processButton').disabled = false;
        
        if (!isInterim) {
            // Auto-classify when final transcript is received
            autoClassifyEmergency(text);
        }
    } else {
        transcriptBox.innerHTML = '<p class="placeholder-text">Your voice transcript will appear here...</p>';
        transcriptBox.classList.remove('has-content');
        document.getElementById('processButton').disabled = true;
    }
}

// Auto-classify emergency (client-side preview)
function autoClassifyEmergency(text) {
    const emergencyKeywords = {
        'medical': ['heart attack', 'stroke', 'bleeding', 'unconscious', 'chest pain', 'breathing', 'overdose', 'seizure', 'allergic', 'broken', 'pain'],
        'fire': ['fire', 'smoke', 'burning', 'flames', 'explosion', 'gas leak'],
        'crime': ['robbery', 'theft', 'assault', 'shooting', 'stabbing', 'break in', 'violence'],
        'accident': ['accident', 'crash', 'collision', 'hit and run', 'vehicle'],
        'natural_disaster': ['earthquake', 'flood', 'tornado', 'hurricane', 'storm'],
        'general': ['help', 'emergency', 'urgent', 'danger', 'trapped', 'stuck', 'lost']
    };

    const lowerText = text.toLowerCase();
    let detectedType = 'unknown';
    let matchedKeywords = [];
    let maxMatches = 0;

    // Find the category with most matches
    for (const [type, keywords] of Object.entries(emergencyKeywords)) {
        const matches = keywords.filter(keyword => lowerText.includes(keyword));
        if (matches.length > maxMatches) {
            maxMatches = matches.length;
            detectedType = type;
            matchedKeywords = matches;
        }
    }

    // Estimate urgency based on keywords
    const urgencyKeywords = ['critical', 'severe', 'immediately', 'dying', 'fatal', 'emergency'];
    const urgencyScore = urgencyKeywords.filter(keyword => lowerText.includes(keyword)).length;
    const estimatedUrgency = Math.min(5 + urgencyScore + maxMatches, 10);

    // Show classification preview
    showClassificationPreview(detectedType, estimatedUrgency, matchedKeywords);
}

// Show classification preview
function showClassificationPreview(type, urgency, keywords) {
    const panel = document.getElementById('classificationPanel');
    const typeElement = document.getElementById('emergencyType');
    const urgencyElement = document.getElementById('emergencyUrgency');
    const keywordsElement = document.getElementById('emergencyKeywords');

    typeElement.textContent = type.replace('_', ' ').toUpperCase();
    urgencyElement.innerHTML = `<span class="urgency-${urgency}">${urgency}/10</span>`;
    keywordsElement.textContent = keywords.length > 0 ? keywords.join(', ') : 'None detected';

    panel.style.display = 'block';
}

// Get user location
function getLocation() {
    const locationButton = document.getElementById('locationButton');
    const locationInfo = document.getElementById('locationInfo');

    if (navigator.geolocation) {
        locationButton.disabled = true;
        locationButton.innerHTML = '<div class="loading"></div> Getting Location...';

        navigator.geolocation.getCurrentPosition(
            function(position) {
                currentLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                };

                locationInfo.innerHTML = `
                    <p><strong>📍 Current Location Detected</strong></p>
                    <p>Latitude: ${currentLocation.latitude.toFixed(6)}</p>
                    <p>Longitude: ${currentLocation.longitude.toFixed(6)}</p>
                    <p>Accuracy: ±${Math.round(currentLocation.accuracy)} meters</p>
                    <p><a href="https://maps.google.com/?q=${currentLocation.latitude},${currentLocation.longitude}" target="_blank">View on Google Maps</a></p>
                `;

                // Update location in classification
                document.getElementById('emergencyLocation').textContent = 
                    `GPS: ${currentLocation.latitude.toFixed(6)}, ${currentLocation.longitude.toFixed(6)}`;

                locationButton.disabled = false;
                locationButton.innerHTML = '📍 Update Location';
            },
            function(error) {
                let errorMessage;
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage = "Location access denied by user.";
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage = "Location information unavailable.";
                        break;
                    case error.TIMEOUT:
                        errorMessage = "Location request timed out.";
                        break;
                    default:
                        errorMessage = "An unknown error occurred.";
                        break;
                }

                locationInfo.innerHTML = `<p style="color: #dc3545;">❌ ${errorMessage}</p>`;
                locationButton.disabled = false;
                locationButton.innerHTML = '📍 Try Again';
            }
        );
    } else {
        locationInfo.innerHTML = '<p style="color: #dc3545;">❌ Geolocation is not supported by this browser.</p>';
    }
}

// Process emergency
async function processEmergency() {
    if (!transcriptText.trim()) {
        alert('Please record an emergency message first.');
        return;
    }

    updateStatus('processing', '🟡 Processing', 'Analyzing emergency and sending alerts...');
    
    const processButton = document.getElementById('processButton');
    const originalText = processButton.innerHTML;
    processButton.disabled = true;
    processButton.innerHTML = '<div class="loading"></div> Processing...';

    try {
        const response = await fetch('/api/process-emergency', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                transcript: transcriptText,
                location: currentLocation || {},
                timestamp: new Date().toISOString()
            })
        });

        const result = await response.json();

        if (result.success) {
            showResults(result.emergency_data, result.message);
            updateStatus('success', '✅ Complete', 'Emergency processed and alerts sent successfully');
        } else {
            throw new Error(result.error || 'Failed to process emergency');
        }

    } catch (error) {
        console.error('Error processing emergency:', error);
        updateStatus('error', '❌ Error', `Failed to process emergency: ${error.message}`);
        showResults(null, `Error: ${error.message}`, true);
    } finally {
        processButton.disabled = false;
        processButton.innerHTML = originalText;
    }
}

// Test alert system
async function testAlert() {
    const testButton = document.getElementById('testButton');
    const originalText = testButton.innerHTML;
    testButton.disabled = true;
    testButton.innerHTML = '<div class="loading"></div> Testing...';

    try {
        const response = await fetch('/api/test-alert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const result = await response.json();

        if (result.success) {
            showResults({
                timestamp: new Date().toISOString(),
                transcript: 'Test alert - system functioning normally',
                classification: { type: 'test', urgency: 5 },
                contacts_notified: result.result.notified || []
            }, 'Test alert sent successfully!');
            updateStatus('success', '✅ Test Complete', 'Alert system is working correctly');
        } else {
            throw new Error(result.error || 'Test failed');
        }

    } catch (error) {
        console.error('Test failed:', error);
        updateStatus('error', '❌ Test Failed', `Alert system test failed: ${error.message}`);
        showResults(null, `Test Error: ${error.message}`, true);
    } finally {
        testButton.disabled = false;
        testButton.innerHTML = originalText;
    }
}

// Show results
function showResults(emergencyData, message, isError = false) {
    const resultsPanel = document.getElementById('resultsPanel');
    const resultsContent = document.getElementById('resultsContent');

    let html = `<div style="margin-bottom: 15px; padding: 10px; background: ${isError ? '#f8d7da' : '#d1ecf1'}; border-radius: 5px; color: ${isError ? '#721c24' : '#0c5460'};">
        <strong>${isError ? '❌' : '✅'} ${message}</strong>
    </div>`;

    if (emergencyData && !isError) {
        html += `
        <div style="display: grid; gap: 15px;">
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                <h4 style="margin-bottom: 10px; color: #495057;">📋 Emergency Details</h4>
                <p><strong>Timestamp:</strong> ${new Date(emergencyData.timestamp).toLocaleString()}</p>
                <p><strong>Type:</strong> ${emergencyData.classification.type.replace('_', ' ').toUpperCase()}</p>
                <p><strong>Urgency Level:</strong> <span class="urgency-${emergencyData.classification.urgency}">${emergencyData.classification.urgency}/10</span></p>
                <p><strong>Message:</strong> "${emergencyData.transcript}"</p>
            </div>
            
            <div style="background: #e8f5e8; padding: 15px; border-radius: 8px;">
                <h4 style="margin-bottom: 10px; color: #28a745;">📧 Notification Status</h4>
                ${emergencyData.contacts_notified.length > 0 ? 
                    `<p style="color: #28a745;">✅ Successfully notified: ${emergencyData.contacts_notified.join(', ')}</p>` : 
                    `<p style="color: #856404;">⚠️ No contacts were notified (urgency level may be below threshold)</p>`
                }
            </div>
        </div>`;
    }

    resultsContent.innerHTML = html;
    resultsPanel.style.display = 'block';
    resultsPanel.scrollIntoView({ behavior: 'smooth' });
}

// Update status
function updateStatus(type, indicator, text) {
    const statusPanel = document.querySelector('.status-panel');
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');

    // Remove all status classes
    statusPanel.classList.remove('recording', 'processing');

    // Add appropriate class
    if (type === 'recording') {
        statusPanel.classList.add('recording');
    } else if (type === 'processing') {
        statusPanel.classList.add('processing');
    }

    statusIndicator.textContent = indicator;
    statusText.textContent = text;
}

// Clear all data
function clearAll() {
    if (confirm('Are you sure you want to clear all data?')) {
        // Stop recording if active
        if (isRecording) {
            stopRecording();
        }

        // Clear transcript
        transcriptText = '';
        updateTranscript('');

        // Clear location
        currentLocation = null;
        document.getElementById('locationInfo').innerHTML = '<p>Location not detected. Click button above to share your location.</p>';
        document.getElementById('locationButton').innerHTML = '📍 Get Current Location';

        // Hide panels
        document.getElementById('classificationPanel').style.display = 'none';
        document.getElementById('resultsPanel').style.display = 'none';

        // Reset status
        updateStatus('ready', '🟢 Ready', 'Click the microphone to report an emergency');

        // Reset classification display
        document.getElementById('emergencyType').textContent = '-';
        document.getElementById('emergencyUrgency').textContent = '-';
        document.getElementById('emergencyLocation').textContent = '-';
        document.getElementById('emergencyKeywords').textContent = '-';
    }
}

// Handle keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Space bar to toggle recording
    if (event.code === 'Space' && !event.repeat) {
        event.preventDefault();
        toggleRecording();
    }
    
    // Enter to process emergency
    if (event.code === 'Enter' && event.ctrlKey) {
        event.preventDefault();
        if (!document.getElementById('processButton').disabled) {
            processEmergency();
        }
    }
    
    // Escape to stop recording
    if (event.code === 'Escape') {
        event.preventDefault();
        if (isRecording) {
            stopRecording();
        }
    }
});

// Auto-save transcript to localStorage
function saveTranscript() {
    if (transcriptText) {
        localStorage.setItem('emergency_transcript', transcriptText);
        localStorage.setItem('emergency_timestamp', new Date().toISOString());
    }
}

// Load saved transcript
function loadSavedTranscript() {
    const saved = localStorage.getItem('emergency_transcript');
    const timestamp = localStorage.getItem('emergency_timestamp');
    
    if (saved && timestamp) {
        const savedDate = new Date(timestamp);
        const now = new Date();
        const hoursSinceLastSave = (now - savedDate) / (1000 * 60 * 60);
        
        // Only load if less than 1 hour old
        if (hoursSinceLastSave < 1) {
            transcriptText = saved;
            updateTranscript(transcriptText);
        } else {
            // Clear old data
            localStorage.removeItem('emergency_transcript');
            localStorage.removeItem('emergency_timestamp');
        }
    }
}

// Initialize saved data on load
document.addEventListener('DOMContentLoaded', function() {
    loadSavedTranscript();
});

// Save transcript when it changes
setInterval(saveTranscript, 5000); // Save every 5 seconds