// This is the place for main application logic (initialization, user I/O handling)
$(document).ready(function() {
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
            if (!(key.length === 1 && key.match(/[a-z]/i)) && 
                !['backspace', 'arrowleft', 'arrowright'].includes(key)) {
                // Not a letter, backspace or arrow key - let the input handlers handle it
                return;
            }
        }
    });
});
