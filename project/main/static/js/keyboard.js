// Keyboard implementation for Wordlas game
// Reference game variables and functions from window object
let currentGameId;

$(document).ready(function() {
    console.log("Keyboard script loaded");
    
    // Wait a short time to ensure other elements are initialized
    setTimeout(function() {
        console.log("Initializing keyboard");
        // Initialize the keyboard
        initKeyboard();
        
        // Fetch current game state from API
        fetchGameState();
        
        // Initialize keyboard state from localStorage if available
        loadKeyboardState();
    }, 500); // Increased timeout to ensure other scripts are loaded
});

// Lithuanian keyboard layout with special characters
const keyboardLayout = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ą'],
    ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'Č', '⌫'],
    ['Ę', 'Ė', 'Į', 'Š', 'Ų', 'Ū', 'Ž']
];

// Lithuanian special characters mapping - kept for alternative character input
const lithuanianChars = {
    'A': ['A', 'Ą'],
    'C': ['C', 'Č'],
    'E': ['E', 'Ę', 'Ė'],
    'I': ['I', 'Į'],
    'S': ['S', 'Š'],
    'U': ['U', 'Ų', 'Ū'],
    'Z': ['Z', 'Ž']
};

// Initialize keyboard UI
function initKeyboard() {
    const $keyboard = $('<div>').attr('id', 'virtual-keyboard');
    
    // Create keyboard rows based on layout
    keyboardLayout.forEach(row => {
        const $row = $('<div>').addClass('keyboard-row');
        
        row.forEach(key => {
            let keyClass = 'keyboard-key';
            
            // Special styling for special keys
            if (key === 'ENTER') {
                keyClass += ' key-enter';
            } else if (key === '⌫') {
                keyClass += ' key-backspace';
            }
            
            const $key = $('<button>')
                .addClass(keyClass)
                .attr('data-key', key)
                .text(key)
                .on('click', handleKeyClick);
            
            // Long press handling for Lithuanian characters
            if (lithuanianChars[key]) {
                setupLongPress($key, key);
            }
            
            $row.append($key);
        });
        
        $keyboard.append($row);
    });
    
    // Add keyboard to the page in a dedicated container right after word-grid
    const $keyboardContainer = $('<div>').attr('id', 'keyboard-container');
    $keyboardContainer.append($keyboard);
    
    // Insert the keyboard container right after the word-grid element
    $('#word-grid').after($keyboardContainer);
    
    // Add event listener for physical keyboard
    $(document).on('keydown', handlePhysicalKeyboard);
}

// Handle keyboard key clicks
function handleKeyClick() {
    if (window.gameOver) return;
    
    const key = $(this).attr('data-key');
    processKey(key);
}

// Process a key press (virtual or physical)
function processKey(key) {
    // Find the currently focused input or the first empty input in the active row
    let $currentInput = $('.letter-cell:focus');
    const $activeRow = $('.game-row').eq(currRow);
    const $inputs = $activeRow.find('input');
    
    // If no input is focused, find the first empty one in active row
    if (!$currentInput.length) {
        const $emptyInputs = $inputs.filter(function() {
            return $(this).val() === '';
        });
        
        if ($emptyInputs.length > 0) {
            $currentInput = $emptyInputs.first();
            $currentInput.focus();
        } else if ($inputs.filter(':not(:disabled)').length > 0) {
            // If no empty inputs but row is active, focus on the last input
            $currentInput = $inputs.filter(':not(:disabled)').last();
            $currentInput.focus();
        } else {
            // No active row inputs found
            return;
        }
    }
    
    if (key === 'ENTER') {
        window.checkWord();
    } else if (key === '⌫') {
        // If current input is empty, move to previous input and clear it
        if ($currentInput.val() === '') {
            const currentIndex = $inputs.index($currentInput);
            if (currentIndex > 0) {
                $inputs.eq(currentIndex - 1).focus().val('');
            }
        } else {
            // Clear the current input
            $currentInput.val('').focus();
        }
    } else if (key.length === 1 && key.match(/[A-ZĄČĘĖĮŠŲŪŽ]/i)) {
        // Regular letter input
        $currentInput.val(key).trigger('input');
        
        // Move to next input after inserting a letter
        const currentIndex = $inputs.index($currentInput);
        if (currentIndex < $inputs.length - 1) {
            setTimeout(function() {
                $inputs.eq(currentIndex + 1).focus();
            }, 10); // Small delay to ensure proper focus handling
        }
        
        // Auto-scroll to make sure the active row is visible
        scrollToActiveRow();
    }
}

// Scroll to make the active row visible
function scrollToActiveRow() {
    const $activeRow = $('.game-row').eq(currRow);
    if ($activeRow.length) {
        const rowPosition = $activeRow.position().top;
        const windowHeight = $(window).height();
        const keyboardHeight = $('#virtual-keyboard').outerHeight();
        
        // If the active row is too close to the bottom of the viewport, scroll it into better view
        if (rowPosition > windowHeight - keyboardHeight - 150) {
            $('html, body').animate({
                scrollTop: rowPosition - 200
            }, 200);
        }
    }
}

// Handle physical keyboard input
function handlePhysicalKeyboard(event) {
    if (window.gameOver) return;
    
    const key = event.key.toUpperCase();
    
    if (key === 'ENTER') {
        event.preventDefault();
        processKey('ENTER');
    } else if (key === 'BACKSPACE') {
        event.preventDefault();
        processKey('⌫');
    } else if (key.length === 1 && key.match(/[A-ZĄČĘĖĮŠŲŪŽąčęėįšųūž]/i)) {
        event.preventDefault();
        processKey(key.toUpperCase());
    } else if (key === 'ARROWRIGHT') {
        // Handle right arrow key - move to next input
        event.preventDefault();
        const $currentInput = $('.letter-cell:focus');
        if ($currentInput.length) {
            const $activeRow = $('.game-row').eq(currRow);
            const $inputs = $activeRow.find('input');
            const currentIndex = $inputs.index($currentInput);
            if (currentIndex < $inputs.length - 1) {
                $inputs.eq(currentIndex + 1).focus();
            }
        }
    } else if (key === 'ARROWLEFT') {
        // Handle left arrow key - move to previous input
        event.preventDefault();
        const $currentInput = $('.letter-cell:focus');
        if ($currentInput.length) {
            const $activeRow = $('.game-row').eq(currRow);
            const $inputs = $activeRow.find('input');
            const currentIndex = $inputs.index($currentInput);
            if (currentIndex > 0) {
                $inputs.eq(currentIndex - 1).focus();
            }
        }
    }
}

// Setup long press for Lithuanian characters
function setupLongPress($key, baseKey) {
    let longPressTimer;
    let isLongPress = false;
    
    $key.on('mousedown touchstart', function(e) {
        e.preventDefault();
        const $this = $(this);
        
        longPressTimer = setTimeout(function() {
            isLongPress = true;
            showCharOptions($this, baseKey);
        }, 500); // 500ms for long press
    });
    
    $key.on('mouseup touchend', function() {
        clearTimeout(longPressTimer);
        
        if (!isLongPress) {
            handleKeyClick.call(this);
        }
        
        isLongPress = false;
        // Hide char options if they were shown
        $('.char-options').remove();
    });
    
    $key.on('mouseleave touchmove', function() {
        clearTimeout(longPressTimer);
        
        // Don't hide options here to allow selecting them
        isLongPress = false;
    });
}

// Show character options for long press
function showCharOptions($key, baseKey) {
    $('.char-options').remove();
    
    const chars = lithuanianChars[baseKey];
    if (!chars || chars.length <= 1) return;
    
    const $options = $('<div>').addClass('char-options');
    
    chars.forEach(char => {
        const $option = $('<span>')
            .addClass('char-option')
            .text(char)
            .on('click', function(e) {
                e.stopPropagation();
                processKey(char);
                $('.char-options').remove();
            });
        
        $options.append($option);
    });
    
    // Position options above the key
    const keyPosition = $key.position();
    $options.css({
        left: keyPosition.left,
        top: keyPosition.top - 40
    });
    
    $('#virtual-keyboard').append($options);
}

// Update keyboard UI with results after a guess
function updateKeyboard(userWord, result) {
    // Store key states
    let keyStates = JSON.parse(localStorage.getItem('keyboardState') || '{}');
    
    for (let i = 0; i < userWord.length; i++) {
        const letter = userWord[i];
        const $key = $(`.keyboard-key[data-key="${letter}"]`);
        
        // Update key state based on result
        if (result[i] === 'success') {
            $key.removeClass('key-warning key-neutral').addClass('key-success');
            keyStates[letter] = 'success';
        } else if (result[i] === 'warning' && keyStates[letter] !== 'success') {
            $key.removeClass('key-neutral').addClass('key-warning');
            if (keyStates[letter] !== 'success') {
                keyStates[letter] = 'warning';
            }
        } else if (!$key.hasClass('key-success') && !$key.hasClass('key-warning')) {
            $key.addClass('key-neutral');
            if (!keyStates[letter]) {
                keyStates[letter] = 'neutral';
            }
        }
    }
    
    // Save to localStorage
    localStorage.setItem('keyboardState', JSON.stringify(keyStates));
}

// Load keyboard state from localStorage
function loadKeyboardState() {
    const keyStates = JSON.parse(localStorage.getItem('keyboardState') || '{}');
    
    for (const [letter, state] of Object.entries(keyStates)) {
        const $key = $(`.keyboard-key[data-key="${letter}"]`);
        $key.addClass(`key-${state}`);
    }
}

// Reset keyboard state when starting a new game
function resetKeyboard() {
    $('.keyboard-key').removeClass('key-success key-warning key-neutral');
    localStorage.removeItem('keyboardState');
    
    // Start a new game via API
    startNewGame();
}

// Fetch current game state from the Django API
function fetchGameState() {
    // Since we don't have a specific endpoint for game state yet,
    // we'll retrieve the current game state from localStorage
    // and use the API once it's fully implemented
    console.log('Checking for saved game state');
    
    // Get current game ID from localStorage
    currentGameId = localStorage.getItem('currentGameId');
    
    if (currentGameId) {
        console.log('Found saved game with ID:', currentGameId);
        
        // In the future, this would make an API call to get the current game state
        // For now, we'll use the localStorage state
        const savedGuesses = JSON.parse(localStorage.getItem('gameGuesses') || '[]');
        
        if (savedGuesses.length > 0) {
            console.log('Restoring saved game with', savedGuesses.length, 'guesses');
            const gameData = {
                game_id: currentGameId,
                guesses: savedGuesses,
                active: !localStorage.getItem('gameOver')
            };
            
            // If there's a word of the day in localStorage, use it
            const savedWord = localStorage.getItem('wordOfDay');
            if (savedWord) {
                gameData.word = savedWord;
            }
            
            restoreGameState(gameData);
        }
    } else {
        console.log('No active game found, starting in local mode');
    }
}

// Restore a game in progress from API data
function restoreGameState(gameData) {
    // Reset the grid first to clear any existing state
    if (typeof resetGrid === 'function') {
        resetGrid();
    }
    
    // Set the word of the day if provided
    if (gameData.word && window.wordOfDay !== undefined) {
        window.wordOfDay = gameData.word;
    }
    
    // Restore each guess
    if (gameData.guesses && gameData.guesses.length > 0) {
        gameData.guesses.forEach((guess, rowIndex) => {
            // Fill in the row with the guess
            const $row = $('.game-row').eq(rowIndex);
            const $inputs = $row.find('input');
            
            // Fill in the letters
            for (let i = 0; i < guess.word.length; i++) {
                $inputs.eq(i).val(guess.word[i]);
            }
            
            // Enable the row for the current guess
            $inputs.prop('disabled', false);
            
            // For completed guesses, apply colors and disable
            if (guess.result) {
                // Call the colorWordHints function from word-grid.js
                if (typeof colorWordHints === 'function') {
                    colorWordHints($inputs, guess.word);
                } else {
                    // Fallback: apply colors directly
                    for (let i = 0; i < guess.word.length; i++) {
                        if (guess.result[i]) {
                            $inputs.eq(i).removeClass('neutral warning success')
                                .addClass(guess.result[i])
                                .css('border-color', '');
                        }
                    }
                }
                $inputs.prop('disabled', true);
                
                // Update global row counter
                if (window.currRow !== undefined) {
                    window.currRow = rowIndex + 1;
                }
                
                // If this was the winning guess, set game as won
                if (guess.word === window.wordOfDay) {
                    window.rightGuess = true;
                    window.gameOver = true;
                }
            }
        });
        
        // Focus the first input of the current active row
        const $currentRow = $('.game-row').eq(window.currRow);
        if ($currentRow.length) {
            const $currentInputs = $currentRow.find('input');
            $currentInputs.prop('disabled', false);
            $currentInputs.first().focus();
        }
        
        // If game is complete, disable inputs and show game end message
        if (gameData.completed) {
            window.gameOver = true;
            $('.letter-cell').prop('disabled', true);
            
            if (gameData.won) {
                displayWinMessage();
            } else {
                displayLoseMessage();
            }
        }
    }
}

// Start a new game via API
function startNewGame() {
    fetch('/api/game/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // Generate a unique game ID for localStorage tracking
        currentGameId = generateUUID();
        localStorage.setItem('currentGameId', currentGameId);
        
        // Clear game guesses in localStorage
        localStorage.setItem('gameGuesses', JSON.stringify([]));
        
        // Store the current word of the day in localStorage
        if (window.wordOfDay) {
            localStorage.setItem('wordOfDay', window.wordOfDay);
        }
        
        console.log('New game started with ID:', currentGameId);
        return response;
    })
    .catch(error => {
        console.error('Error starting new game:', error);
        // If API fails, fall back to local game
        console.log('Falling back to local game mode');
        
        // Still generate a game ID for local tracking
        currentGameId = generateUUID();
        localStorage.setItem('currentGameId', currentGameId);
        localStorage.setItem('gameGuesses', JSON.stringify([]));
        
        if (window.wordOfDay) {
            localStorage.setItem('wordOfDay', window.wordOfDay);
        }
    });
}

// Helper function to generate UUID for client-side tracking
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Submit a guess to the API and store locally
function submitGuess(word) {
    // If no game ID, we're in pure local mode
    if (!currentGameId) {
        console.log('No active game ID, operating in local mode');
        return;
    }
    
    // Get current guesses from localStorage
    const guesses = JSON.parse(localStorage.getItem('gameGuesses') || '[]');
    
    // Create the result pattern based on the current word
    const savedWord = localStorage.getItem('wordOfDay') || window.wordOfDay;
    const resultPattern = [];
    
    // Determine the pattern (success, warning, neutral)
    for (let i = 0; i < word.length; i++) {
        if (word[i] === savedWord[i]) {
            resultPattern.push('success');
        } else if (savedWord.includes(word[i])) {
            resultPattern.push('warning');
        } else {
            resultPattern.push('neutral');
        }
    }
    
    // Add this guess to the array
    guesses.push({
        word: word,
        result: resultPattern,
        timestamp: new Date().toISOString()
    });
    
    // Save updated guesses to localStorage
    localStorage.setItem('gameGuesses', JSON.stringify(guesses));
    
    // Check if game is completed (word matched or max attempts reached)
    const gameWon = word === savedWord;
    const gameLost = guesses.length >= window.gridSize.tries && !gameWon;
    
    if (gameWon || gameLost) {
        // Game is over
        window.gameOver = true;
        localStorage.setItem('gameOver', 'true');
        
        // Update the game state via API
        fetch('/api/game/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                id: currentGameId,
                isfinished: true
            })
        }).catch(error => {
            console.error('Error updating game state:', error);
        });
    }
}

// Helper function to get CSRF token
function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken='.length) === 'csrftoken=') {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken='.length));
                break;
            }
        }
    }
    return cookieValue;
}

// Override the original processKey function to add API integration
const originalProcessKey = processKey;
processKey = function(key) {
    originalProcessKey(key);
    
    // If Enter was pressed, check if we need to submit to API
    if (key === 'ENTER') {
        const $row = $('.game-row').eq(window.currRow);
        const $inputs = $row.find('input');
        const userWord = getUserWord($inputs);
        
        if (userWord && userWord.length === window.gridSize.letters) {
            // Submit the guess to the API
            submitGuess(userWord);
        }
    }
};

// Override the input handler in word-grid.js to work better with virtual keyboard
$(document).ready(function() {
    setTimeout(function() {
        // Override handleInput to avoid duplicate functionality
        $('.letter-cell').off('input').on('input', function() {
            if (window.gameOver) return;
            
            const $input = $(this);
            // Always convert to uppercase
            $input.val($input.val().toUpperCase());
            
            // Do not automatically move focus - let keyboard.js handle this
            // This prevents conflicts between physical and virtual keyboard handling
        });
    }, 600); // Wait a bit longer than keyboard initialization
});
