// Highlights the searched phrase ('Content contains') in clippings 
function highlightClippings(wordToHighlight) {
    // If empty -> stop the function
    if (!wordToHighlight) return;

    // Get all clippings' text
    const clippings = document.querySelectorAll('.clipping-content > em');

    // Highlighs searched-for phrase in each clipping (case-insensitive)
    clippings.forEach((clipping) => {
        const regex = new RegExp(wordToHighlight, 'gi');
        const highlightedClipping = clipping.innerHTML.replace(regex, (foundWord) => {
            return `<span class="highlight">${foundWord}</span>`;
        });

        clipping.innerHTML = highlightedClipping;
    });
}