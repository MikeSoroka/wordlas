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

// Function to set cookies
function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        let date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

// Update theme toggle to save to cookies
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            // Save theme preference in cookies
            setCookie('theme', currentTheme, 365); // Save for 1 year
        });
    }
});
