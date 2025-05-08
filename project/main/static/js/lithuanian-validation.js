// Lithuanian character validation script

// Lithuanian alphabet regex pattern
const lithuanianCharPattern = /^[aąbcčdeęėfghiįyjklmnoprsštuųūvzžAĄBCČDEĘĖFGHIĮYJKLMNOPRSŠTUŲŪVZŽ]$/;

// Validation function that can be called from other JS files
function isValidLithuanianChar(char) {
    // Explicitly reject space characters
    if (char === ' ') return false;
    return lithuanianCharPattern.test(char);
}

// Validate the entire word
function isValidLithuanianWord(word) {
    // Make sure the word is 5 characters and all are Lithuanian
    return word.length === 5 && 
           Array.from(word).every(char => isValidLithuanianChar(char));
}

// Display error message for invalid characters
function showInvalidCharError() {
    const errorEl = $('#validation-errors');
    errorEl.text('Tik lietuviškos raidės leidžiamos').show();
    setTimeout(() => {
        errorEl.fadeOut(500);
    }, 3000);
}

// This function modifies the default input handling to check for Lithuanian characters
$(document).ready(function() {
    // Override the handleInput function from word-grid.js to validate Lithuanian chars
    $(document).on('input', '.letter-cell', function(event) {
        if (gameOver) return;
        
        const $input = $(this);
        const value = $input.val().toUpperCase();
        
        // If empty, just continue
        if (value === '') return;
        
        // Check if the character is a valid Lithuanian character
        if (!isValidLithuanianChar(value)) {
            // Clear the invalid input
            $input.val('');
            // Prevent default behavior
            event.preventDefault();
            event.stopPropagation();
            // Show error notification
            showInvalidCharError();
            // Animate the error
            animateInvalidWord($input.parent());
            // Keep focus on the current input
            $input.focus();
            return;
        }
        
        // Set the valid character
        $input.val(value);
        
        // Move to next input
        const $row = $input.parent();
        const $inputs = $row.find('input');
        const currentIndex = $inputs.index($input);
        
        if (currentIndex < $inputs.length - 1) {
            $inputs.eq(currentIndex + 1).focus();
        }
    });

    // Handle keydown to also catch space character
    $(document).on('keydown', '.letter-cell', function(event) {
        if (gameOver) return;
        
        // Explicitly catch space key and prevent it
        if (event.key === ' ' || event.key === 'Spacebar') {
            event.preventDefault();
            showInvalidCharError();
            animateInvalidWord($(this).parent());
            return false;
        }
    });

    // Extend checkWord function to validate the entire word
    const originalCheckWord = window.checkWord;
    window.checkWord = function() {
        if (gameOver) return;
        
        let $row = $('.game-row').eq(currRow);
        let $inputs = $row.find('input');
        const userWord = getUserWord($inputs);
        
        if (userWord && !isValidLithuanianWord(userWord)) {
            // Word contains non-Lithuanian characters
            showInvalidCharError();
            animateInvalidWord($row);
            return;
        }
        
        // Call the original function
        originalCheckWord();
    };
}); 