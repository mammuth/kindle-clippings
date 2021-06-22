// ------- books.html -------
const booksView = {
    // Hides books which doesn't match the search bar value
    searchBook() {
        const searchInput = document.querySelector('#search-book');
        const books = document.querySelectorAll('.js-book-element');
    
        function displayMatches() {
            const regex = new RegExp(this.value, 'gi');
    
            books.forEach(book => {
                const title = book.querySelector('.js-book-title').textContent;
                const author = book.querySelector('.js-book-author').textContent;
    
                if (title.match(regex) || author.match(regex)) {
                    book.classList.remove('hidden');
                }
                else {
                    book.classList.add('hidden');
                }
            })
        }
    
        searchInput.addEventListener('keyup', displayMatches);
    },
    // Switches between the list and the gallery book view + controls buttons' colors
    switchView() {
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
            bookView.className = this.dataset.view;
        }
    
        galleryBtn.addEventListener('click', viewControl);
        listBtn.addEventListener('click', viewControl);
    }
}
