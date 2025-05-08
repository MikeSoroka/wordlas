// This is the place for main application logic (initialization, user I/O handling)
$(document).ready(function() {
    // Set the language and initialize game settings
    setLanguageSettings();
    
    // Initialize the game grid
    createGrid();
    
    // Button event listeners
    $("#check-word-btn").on("click", checkWord);
    $("#reset-grid-btn").on("click", resetGrid); 

    // Global keyboard event handler
    $(document).on("keydown", function(event) {
        // Submit word with Enter key
        if (event.key === "Enter") {
            event.preventDefault(); // Prevent default form submission behavior
            checkWord();
        }
        
        // If game is over, no keys should be processed except for buttons
        if (gameOver && !$(event.target).is('button')) {
            event.preventDefault();
            return;
        }
        
        // Only allow letter input when focused on an input field
        if ($(document.activeElement).hasClass('letter-cell')) {
            const key = event.key.toLowerCase();
            
            // Allow only letters, backspace and arrow keys
            if (!(key.length === 1 && key.match(/[a-zāčęėįšųūž]/i)) && 
                !['backspace', 'arrowleft', 'arrowright'].includes(key)) {
                // Not a letter, backspace or arrow key - let the input handlers handle it
                return;
            }
        }
    });
    
    // Check for dark mode preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        console.log('Dark mode is enabled by user preference');
    }
    
    // Listen for dark mode changes
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
            console.log('Dark mode preference changed:', event.matches ? 'enabled' : 'disabled');
        });
    }
    
    // Set up PWA capability checks
    checkPWACapability();
});

// Set language and input settings
function setLanguageSettings() {
    // Get browser language or use 'lt' (Lithuanian) as default
    const userLang = navigator.language || navigator.userLanguage || 'lt';
    console.log('User language:', userLang);
    
    // Provide keyboard input settings based on language
    window.keyboardSettings = {
        language: userLang.startsWith('lt') ? 'lt' : 'en',
        specialChars: true // Enable special character support
    };
}

// Check if the app can be installed as PWA
function checkPWACapability() {
    // Listen for beforeinstallprompt event
    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent the mini-info bar from appearing on mobile
        e.preventDefault();
        // Store the event so it can be triggered later
        window.deferredPrompt = e;
        
        // Show install button or notification if desired
        console.log('App can be installed as PWA');
    });
}

// Handle online/offline status for cached game state
window.addEventListener('online', function() {
    console.log('Game is online - syncing data with server');
    syncGameData();
});

window.addEventListener('offline', function() {
    console.log('Game is offline - will use cached data');
});

// Sync cached game data with server when connection restored
function syncGameData() {
    // If we have cached game data that hasn't been synced
    const cachedGuesses = JSON.parse(localStorage.getItem('gameGuesses') || '[]');
    const needsSync = localStorage.getItem('needsSync') === 'true';
    
    if (cachedGuesses.length > 0 && needsSync) {
        console.log('Syncing cached game data with server');
        // Future implementation: send cached data to server
        
        // Mark as synced
        localStorage.setItem('needsSync', 'false');
    }
}
