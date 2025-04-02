// This is the place for main application logic (initialization, user I/O handling)
document.addEventListener("DOMContentLoaded", () => {
    createGrid();
    document.getElementById("check-word-btn").addEventListener("click", checkWord);
    document.getElementById("reset-grid-btn").addEventListener("click", resetGrid); 

    document.addEventListener("keydown", (event) => {
        if (event.key === "Enter") checkWord();
    });

    // add functional keyboard layout to the screen with color hints (as on grid)
    // add hint logic (optional)
    // add preferences settings (optional)
});
