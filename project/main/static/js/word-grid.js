// TEMPORARY SOLUTION; connect to the word database later
const words = ["LABAS", "GERAI", "KODAS", "VIETA", "IDEJA", "SAULE", "GATVE"]; 

const wordGrid = document.getElementById("word-grid");

// just in case we want to change something later 
// (for example, add dark mode or make game harder with 5+ letter words)
const gridSize = {"tries": 6, "letters": 5};
const defaultColor = "gray";
const includesColor = "yellow";
const rightPlaceColor = "lightgreen";

let wordOfDay = words[Math.floor(Math.random() * words.length)];
let currRow = 0; // can be used later to compare number of tries
let rightGuess = false;

function resetGrid() {
    createGrid();
    wordOfDay = words[Math.floor(Math.random() * words.length)];
    currRow = 0;
    rightGuess = false;
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
    const input = event.target;
	input.value = input.value.toUpperCase(); 
    if (input.value.length === 1) {
        const row = input.parentElement;
        const inputs = row.querySelectorAll("input");
        const currentIndex = Array.from(inputs).indexOf(input);
        if (currentIndex < inputs.length - 1) {
            inputs[currentIndex + 1].focus();
        }
    }
}

function handleKeyDown(event) {
    const input = event.target;
    if (event.key === "Backspace" && input.value === "") {
        const row = input.parentElement;
        const inputs = row.querySelectorAll("input");
        const currentIndex = Array.from(inputs).indexOf(input);
        if (currentIndex > 0) {
            inputs[currentIndex - 1].focus();
        }
    }
}

function getUserWord(inputs) { // EARLY VARIANT; add check if the word exist in dictionary
    let userWord = "";
    for (let input of inputs) {
        userWord += input.value.toUpperCase();
    }

    if (userWord.length !== 5) {
        // possible to give some response to user
        return;
    }
    return userWord;
}

function checkWord() {
    let row = document.getElementsByClassName("row")[currRow];
    let inputs = row.getElementsByTagName("input");

    const userWord = getUserWord(inputs);

    if (userWord) {
        colorWordHints(inputs, userWord);
        currRow++;

        if (rightGuess) { // can be trigger to congratulations screen
            console.log("You won");
            return;
        }

        if (currRow < 6) {
            const nextRow = document.getElementsByClassName("row")[currRow];
            const nextInputs = nextRow.getElementsByTagName("input");
            for (let input of nextInputs) input.disabled = false;
            nextInputs[0].focus();
        } else {
            console.log("You lost. Right answer was: " + wordOfDay); 
        }
    }
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

	// evaluating letters at right places first
	function colorAtRightPlace() {
		let rightIndices = [];
		for (let i = 0; i < gridSize.letters; i++) { 
			if (userWord[i] === wordOfDay[i] && letters[userWord[i]] > 0) {
				inputs[i].style.backgroundColor = rightPlaceColor;
				letters[userWord[i]]--;
				rightIndices.push(i);
			}
		}
		return rightIndices;
	}

	let rightIndices = colorAtRightPlace(); // I know that looks terrible but at least that prevents first-match error

	// then processing other letters/places
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

    if (userWord === wordOfDay) {
        rightGuess = true;
    }
}

