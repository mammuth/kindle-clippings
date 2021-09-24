// ------- browse.html -------
// Highlights the searched phrase ('Content contains') in clippings 
function highlightClippings(wordToHighlight) {
    // If empty -> stop the function
    if (!wordToHighlight) return;

    // Get all clippings' text
    const clippings = document.querySelectorAll('.js-clipping-content > em');

    // Highlighs searched-for phrase in each clipping (case-insensitive)
    clippings.forEach((clipping) => {
        const regex = new RegExp(wordToHighlight, 'gi');
        const highlightedClipping = clipping.innerHTML.replace(regex, (foundWord) => {
            return `<span class="highlight">${foundWord}</span>`;
        });

        clipping.innerHTML = highlightedClipping;
    });
}

// Injects the clipping's id to the modal's form
// when a user clicks the delete icon
function deleteModelControl() {
    const deleteButtons = document.querySelectorAll('.js-delete-clipping');
    const modalClippingInput = document.querySelector('#modal_delete_clipping .js-clipping-id-input');

    deleteButtons.forEach(btn => btn.addEventListener('click', function (e) {
        // Get clipping's ID
        const clippingId = this.dataset.clippingId;

        // Inject it to the modal
        modalClippingInput.value = clippingId;
    }));
}