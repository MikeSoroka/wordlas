// TEMPORARY SOLUTION; connect to the word database later
const words = ["LABAS", "GERAI", "KODAS", "VIETA", "IDEJA", "SAULE", "GATVE"]; 

// grid configuration
const gridSize = {"tries": 6, "letters": 5};
const defaultColor = "secondary"; // Bootstrap gray
const includesColor = "warning";  // Bootstrap yellow
const rightPlaceColor = "success"; // Bootstrap green

let wordOfDay = words[Math.floor(Math.random() * words.length)];
let currRow = 0; // current active row for input
let rightGuess = false;
let gameOver = false;

function resetGrid() {
    createGrid();
    wordOfDay = words[Math.floor(Math.random() * words.length)];
    currRow = 0;
    rightGuess = false;
    gameOver = false;
    
    // Remove win message if it exists
    $('.win-message').remove();
}

function createGrid() {
    $('#word-grid').empty();
    
    for (let i = 0; i < gridSize.tries; i++) {
        let $row = $('<div></div>').addClass('game-row'); // Using game-row to avoid conflict with Bootstrap row
        for (let j = 0; j < gridSize.letters; j++) {
            let $input = addRowInput(i);
            $row.append($input);
        }
        $('#word-grid').append($row);
    }
    // Focus the first input cell
    $('.game-row:first input:first').focus();
}

function addRowInput(rowIndex) {
    let $input = $('<input>')
        .attr('maxlength', '1')
        .addClass('letter-cell')
        .prop('disabled', rowIndex !== 0)
        .on('input', handleInput)
        .on('keydown', handleKeyDown);
    return $input;
}

function handleInput(event) {
    if (gameOver) return;
    
    const $input = $(this);
    // Always convert to uppercase
    $input.val($input.val().toUpperCase()); 
    
    if ($input.val().length === 1) {
        const $row = $input.parent();
        const $inputs = $row.find('input');
        const currentIndex = $inputs.index($input);
        // Move focus to next input when a letter is entered
        if (currentIndex < $inputs.length - 1) {
            $inputs.eq(currentIndex + 1).focus();
        }
    }
}

function handleKeyDown(event) {
    if (gameOver) return;
    
    const $input = $(this);
    const $row = $input.parent();
    const $inputs = $row.find('input');
    const currentIndex = $inputs.index($input);
    
    if (event.key === "Backspace") {
        // If current input is empty, move to previous input and clear it
        if ($input.val() === "" && currentIndex > 0) {
            $inputs.eq(currentIndex - 1).focus().val("");
        } else {
            // Clear the current input
            $input.val("");
        }
    } else if (event.key === "Enter") {
        // Submit word when Enter is pressed
        checkWord();
    } else if (event.key.match(/^[a-zA-Z]$/) && currentIndex === $inputs.length - 1 && $input.val() !== "") {
        // If typing at the last cell that already has a letter, do nothing (prevent overtyping)
        event.preventDefault();
    }
}

function getUserWord($inputs) {
    let userWord = "";
    $inputs.each(function() {
        userWord += $(this).val().toUpperCase();
    });

    if (userWord.length !== gridSize.letters) {
        return null; // Return null if the word is not complete
    }
    return userWord;
}

function checkWord() {
    if (gameOver) return;
    
    let $row = $('.game-row').eq(currRow);
    let $inputs = $row.find('input');

    const userWord = getUserWord($inputs);

    if (userWord) {
        colorWordHints($inputs, userWord);
        
        if (rightGuess) {
            // User won the game
            gameOver = true;
            displayWinMessage();
            return;
        }
        
        currRow++;

        if (currRow < gridSize.tries) {
            // Move to next row
            const $nextRow = $('.game-row').eq(currRow);
            const $nextInputs = $nextRow.find('input');
            $nextInputs.prop('disabled', false);
            $nextInputs.first().focus();
        } else {
            // Game over - no more rows
            gameOver = true;
            displayLoseMessage();
        }
    } else {
        // Word not complete - visual feedback could be added here
        animateInvalidWord($row);
    }
}

function animateInvalidWord($row) {
    // Simple animation for invalid word
    $row.addClass('shake');
    setTimeout(() => {
        $row.removeClass('shake');
    }, 500);
}

function displayWinMessage() {
    const $message = $('<div></div>')
        .addClass('win-message')
        .text('Congratulations! You won!');
    $('#game-container').append($message);
    
    // Disable all inputs when game is won
    $('.letter-cell').prop('disabled', true);
    
    // Visual effect for winning
    $('.game-row').eq(currRow).addClass('winning-row');
}

function displayLoseMessage() {
    const $message = $('<div></div>')
        .addClass('win-message')
        .css('color', '#d32f2f') // Red color for loss message
        .text(`Game over. The word was: ${wordOfDay}`);
    $('#game-container').append($message);
    
    // Disable all inputs when game is lost
    $('.letter-cell').prop('disabled', true);
}

function countLetters(word) {
    let counter = {};
    for (let letter of word) {
        if (!counter[letter]) {
            counter[letter] = 1;
        } else {
            counter[letter] += 1;
        }
    }
    return counter;
}

function colorWordHints($inputs, userWord) {
    let letters = countLetters(wordOfDay);

    // First pass: identify correct positions
    let rightIndices = [];
    for (let i = 0; i < gridSize.letters; i++) { 
        if (userWord[i] === wordOfDay[i] && letters[userWord[i]] > 0) {
            $inputs.eq(i)
                .removeClass('neutral warning')
                .addClass('success')
                .css('border-color', '');
            letters[userWord[i]]--;
            rightIndices.push(i);
        }
    }

    // Second pass: identify letters in wrong positions
    for (let i = 0; i < gridSize.letters; i++) { 
        if (rightIndices.includes(i)) continue;
        
        if (wordOfDay.includes(userWord[i]) && letters[userWord[i]] > 0) {
            $inputs.eq(i)
                .removeClass('neutral success')
                .addClass('warning')
                .css('border-color', '');
            letters[userWord[i]]--;
        } else {
            $inputs.eq(i)
                .removeClass('warning success')
                .addClass('neutral')
                .css('border-color', '');
        }
        $inputs.eq(i).prop('disabled', true);
    }

    // Check if the word is correct
    if (userWord === wordOfDay) {
        rightGuess = true;
    }
}
