// ------- browse.html -------
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

// ------- books.html -------
// Hides books which doesn't match the search bar value
function searchBook() {
    const searchInput = document.querySelector('#search-book');
    const books = document.querySelectorAll('.book-element');

    function displayMatches() {
        const regex = new RegExp(this.value, 'gi');

        books.forEach(book => {
            const title = book.querySelector('.book-title').textContent;
            const author = book.querySelector('.book-author').textContent;

            if (title.match(regex) || author.match(regex)) {
                book.style.display = 'block';
            }
            else {
                book.style.display = 'none';
            }
        })
    }

    searchInput.addEventListener('keyup', displayMatches);
}

// Switches between the list and the gallery book view + controls buttons' colors
function switchView() {
    const galleryBtn = document.querySelector('#btn-gallery');
    const listBtn = document.querySelector('#btn-list');
    const bookView = document.querySelector('#book-view');

    function viewControl() {
        buttonToDisable = (this === galleryBtn) ? listBtn : galleryBtn;

        // Swap buttons' colors
        buttonToDisable.classList.remove('btn-dark');
        buttonToDisable.classList.add('btn-light');

        this.classList.remove('btn-light');
        this.classList.add('btn-dark');

        // Switch the book view
        bookView.className = (this === galleryBtn) ? 'gallery-view' : 'list-view';
    }

    galleryBtn.addEventListener('click', viewControl);
    listBtn.addEventListener('click', viewControl);

}