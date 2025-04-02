// TEMPORARY SOLUTION; connect to the word database later
const words = ["LABAS", "GERAI", "KODAS", "VIETA", "IDEJA", "SAULE", "GATVE"]; 

const wordGrid = document.getElementById("word-grid");

// grid configuration
const gridSize = {"tries": 6, "letters": 5};
const defaultColor = "gray";
const includesColor = "yellow";
const rightPlaceColor = "lightgreen";

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
    const winMessage = document.querySelector('.win-message');
    if (winMessage) {
        winMessage.remove();
    }
}

function createGrid() {
    wordGrid.innerHTML = '';
    
    for (let i = 0; i < gridSize.tries; i++) {
        let row = document.createElement("div");
        row.classList.add("row");
        for (let j = 0; j < gridSize.letters; j++) {
            let input = addRowInput(i);
            row.appendChild(input);
        }
        wordGrid.appendChild(row);
    }
    // Focus the first input cell
    wordGrid.querySelector(".row input").focus();
}

function addRowInput(rowIndex) {
    let input = document.createElement("input");
    input.setAttribute("maxlength", "1");
    input.classList.add("letter-cell");
    input.disabled = rowIndex !== 0;
    input.addEventListener("input", handleInput);
    input.addEventListener("keydown", handleKeyDown);
    return input;
}

function handleInput(event) {
    if (gameOver) return;
    
    const input = event.target;
    // Always convert to uppercase
    input.value = input.value.toUpperCase(); 
    
    if (input.value.length === 1) {
        const row = input.parentElement;
        const inputs = row.querySelectorAll("input");
        const currentIndex = Array.from(inputs).indexOf(input);
        // Move focus to next input when a letter is entered
        if (currentIndex < inputs.length - 1) {
            inputs[currentIndex + 1].focus();
        }
    }
}

function handleKeyDown(event) {
    if (gameOver) return;
    
    const input = event.target;
    const row = input.parentElement;
    const inputs = row.querySelectorAll("input");
    const currentIndex = Array.from(inputs).indexOf(input);
    
    if (event.key === "Backspace") {
        // If current input is empty, move to previous input and clear it
        if (input.value === "" && currentIndex > 0) {
            inputs[currentIndex - 1].focus();
            inputs[currentIndex - 1].value = "";
        } else {
            // Clear the current input
            input.value = "";
        }
    } else if (event.key === "Enter") {
        // Submit word when Enter is pressed
        checkWord();
    } else if (event.key.match(/^[a-zA-Z]$/) && currentIndex === inputs.length - 1 && input.value !== "") {
        // If typing at the last cell that already has a letter, do nothing (prevent overtyping)
        event.preventDefault();
    }
}

function getUserWord(inputs) {
    let userWord = "";
    for (let input of inputs) {
        userWord += input.value.toUpperCase();
    }

    if (userWord.length !== gridSize.letters) {
        return null; // Return null if the word is not complete
    }
    return userWord;
}

function checkWord() {
    if (gameOver) return;
    
    let row = document.getElementsByClassName("row")[currRow];
    let inputs = row.getElementsByTagName("input");

    const userWord = getUserWord(inputs);

    if (userWord) {
        colorWordHints(inputs, userWord);
        
        if (rightGuess) {
            // User won the game
            gameOver = true;
            displayWinMessage();
            return;
        }
        
        currRow++;

        if (currRow < gridSize.tries) {
            // Move to next row
            const nextRow = document.getElementsByClassName("row")[currRow];
            const nextInputs = nextRow.getElementsByTagName("input");
            for (let input of nextInputs) {
                input.disabled = false;
            }
            nextInputs[0].focus();
        } else {
            // Game over - no more rows
            gameOver = true;
            displayLoseMessage();
        }
    } else {
        // Word not complete - visual feedback could be added here
        animateInvalidWord(row);
    }
}

function animateInvalidWord(row) {
    // Simple animation for invalid word
    row.classList.add('shake');
    setTimeout(() => {
        row.classList.remove('shake');
    }, 500);
}

function displayWinMessage() {
    const message = document.createElement("div");
    message.classList.add("win-message");
    message.textContent = "Congratulations! You won!";
    document.getElementById("game-container").appendChild(message);
}

function displayLoseMessage() {
    const message = document.createElement("div");
    message.classList.add("win-message");
    message.style.color = "#d3112d";
    message.textContent = `Game over. The word was: ${wordOfDay}`;
    document.getElementById("game-container").appendChild(message);
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

function colorWordHints(inputs, userWord) {
    let letters = countLetters(wordOfDay);

    // First pass: identify correct positions
    let rightIndices = [];
    for (let i = 0; i < gridSize.letters; i++) { 
        if (userWord[i] === wordOfDay[i] && letters[userWord[i]] > 0) {
            inputs[i].style.backgroundColor = rightPlaceColor;
            letters[userWord[i]]--;
            rightIndices.push(i);
        }
    }

    // Second pass: identify letters in wrong positions
    for (let i = 0; i < gridSize.letters; i++) { 
        if (rightIndices.includes(i)) continue;
        
        if (wordOfDay.includes(userWord[i]) && letters[userWord[i]] > 0) {
            inputs[i].style.backgroundColor = includesColor;
            letters[userWord[i]]--;
        } else {
            inputs[i].style.backgroundColor = defaultColor;
        }
        inputs[i].disabled = true;
    }

    // Check if the word is correct
    if (userWord === wordOfDay) {
        rightGuess = true;
    }
}
