/* Game Templates JavaScript */

// ===== COMMON GAME UTILITIES =====

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
    const secs = (seconds % 60).toString().padStart(2, '0');
    return `${minutes}:${secs}`;
}

function submitGameResults(results) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    return fetch(window.location.href, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(results)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            console.error('Redirect URL not provided by server. Falling back to patient dashboard.');
            window.location.href = '/patient-dashboard/';
        }
    })
    .catch(error => {
        console.error('Error submitting results:', error);
        alert('Could not save your results. Redirecting to the dashboard.');
        window.location.href = '/patient-dashboard/';
    });
}

// ===== COLOR GAME FUNCTIONALITY =====

class ColorGame {
    constructor() {
        this.colors = ['red', 'green', 'blue', 'yellow', 'orange', 'purple'];
        this.deck = [...this.colors, ...this.colors];
        this.first = null;
        this.second = null;
        this.moves = 0;
        this.matches = 0;
        this.seconds = 0;
        this.timer = null;
        this.lockBoard = false;
        
        this.board = document.getElementById('board');
        this.movesEl = document.getElementById('moves');
        this.timerEl = document.getElementById('timer');
        this.gameForm = document.getElementById('gameForm');
        this.finalMoves = document.getElementById('finalMoves');
        this.finalTime = document.getElementById('finalTime');
        
        this.init();
    }
    
    init() {
        this.shuffle();
        this.renderBoard();
        this.startTimer();
    }
    
    shuffle() {
        for (let i = this.deck.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [this.deck[i], this.deck[j]] = [this.deck[j], this.deck[i]];
        }
    }
    
    startTimer() {
        this.timer = setInterval(() => {
            this.seconds++;
            this.timerEl.textContent = formatTime(this.seconds);
        }, 1000);
    }
    
    renderBoard() {
        this.board.innerHTML = '';
        this.deck.forEach((color, index) => {
            const card = document.createElement('div');
            card.className = `card ${color} hidden`;
            card.dataset.index = index;
            card.addEventListener('click', () => this.flipCard(index));
            this.board.appendChild(card);
        });
    }
    
    flipCard(index) {
        if (this.lockBoard || this.deck[index] === 'matched') return;
        
        const card = this.board.children[index];
        card.classList.remove('hidden');
        card.classList.add('selected');
        
        if (!this.first) {
            this.first = index;
        } else if (!this.second && this.first !== index) {
            this.second = index;
            this.moves++;
            this.movesEl.textContent = this.moves;
            this.checkMatch();
        }
    }
    
    checkMatch() {
        this.lockBoard = true;
        
        if (this.deck[this.first] === this.deck[this.second]) {
            // Match found
            this.matches++;
            this.deck[this.first] = 'matched';
            this.deck[this.second] = 'matched';
            
            setTimeout(() => {
                this.board.children[this.first].classList.add('matched');
                this.board.children[this.second].classList.add('matched');
                this.resetSelection();
                
                if (this.matches === this.colors.length) {
                    this.gameCompleted();
                }
            }, 500);
        } else {
            // No match
            setTimeout(() => {
                this.board.children[this.first].classList.add('hidden');
                this.board.children[this.second].classList.add('hidden');
                this.resetSelection();
            }, 1000);
        }
    }
    
    resetSelection() {
        this.board.children[this.first].classList.remove('selected');
        this.board.children[this.second].classList.remove('selected');
        this.first = null;
        this.second = null;
        this.lockBoard = false;
    }
    
    gameCompleted() {
        clearInterval(this.timer);
        const results = {
            score: this.matches,
            total: this.colors.length,
            moves: this.moves,
            time: this.seconds,
            difficulty: 'easy'
        };
        submitGameResults(results);
    }
}

// ===== PAIRS GAME FUNCTIONALITY =====

class PairsGame {
    constructor() {
        this.allPairs = [
            { id: 1, emoji: '🐶', word: 'Dog' }, { id: 1, emoji: '🐱', word: 'Cat' },
            { id: 2, emoji: '🍎', word: 'Apple' }, { id: 2, emoji: '🍌', word: 'Banana' },
            { id: 3, emoji: '🌞', word: 'Sun' }, { id: 3, emoji: '🌙', word: 'Moon' },
            { id: 4, emoji: '🔥', word: 'Fire' }, { id: 4, emoji: '💧', word: 'Water' },
            { id: 5, emoji: '⚡', word: 'Lightning' }, { id: 5, emoji: '☁️', word: 'Cloud' },
            { id: 6, emoji: '🏠', word: 'House' }, { id: 6, emoji: '🏢', word: 'Building' },
            { id: 7, emoji: '📚', word: 'Book' }, { id: 7, emoji: '✏️', word: 'Pencil' },
            { id: 8, emoji: '🎵', word: 'Music' }, { id: 8, emoji: '🎤', word: 'Microphone' }
        ];
        
        this.state = {
            cards: [],
            flipped: [],
            matched: 0,
            moves: 0,
            startTime: null,
            timer: null,
            wrong: [],
            completed: false
        };
        
        this.lockBoard = false;
        this.gameBoard = document.getElementById('gameBoard');
        
        this.init();
    }
    
    init() {
        this.initializeGame();
    }
    
    initializeGame() {
        const pairCount = 8;
        let selected = this.allPairs.slice(0, pairCount * 2);
        let cards = [];
        selected.forEach(pair => {
            cards.push({ id: pair.id, emoji: pair.emoji, word: pair.word, matched: false });
        });
        cards = cards.sort(() => Math.random() - 0.5);
        
        this.state = {
            cards,
            flipped: [],
            matched: 0,
            moves: 0,
            startTime: null,
            timer: null,
            wrong: [],
            completed: false
        };
        
        this.renderGame();
        this.updateStats();
        this.clearInterval(this.state.timer);
        this.state.startTime = Date.now();
        this.state.timer = setInterval(() => this.updateTimer(), 1000);
    }
    
    renderGame() {
        this.gameBoard.innerHTML = '';
        this.state.cards.forEach((card, index) => {
            const el = document.createElement('div');
            el.className = 'card';
            el.innerHTML = `<div>${card.emoji}</div><div style="font-size: 0.5em;">${card.word}</div>`;
            
            if (card.matched) {
                el.classList.add('matched');
            } else if (this.state.wrong && this.state.wrong.includes(index)) {
                el.classList.add('wrong');
            } else if (this.state.flipped.includes(index)) {
                el.classList.add('selected');
            }
            
            if (!card.matched && !this.state.wrong.includes(index) && !this.state.flipped.includes(index) && !this.lockBoard) {
                el.addEventListener('click', () => this.flipCard(index));
            }
            
            this.gameBoard.appendChild(el);
        });
    }
    
    flipCard(index) {
        if (this.lockBoard || this.state.completed || this.state.flipped.length >= 2 || 
            this.state.cards[index].matched || this.state.flipped.includes(index)) {
            return;
        }
        
        this.state.flipped.push(index);
        this.renderGame();
        
        if (this.state.flipped.length === 2) {
            this.lockBoard = true;
            this.state.moves++;
            this.updateStats();
            
            const [i1, i2] = this.state.flipped;
            if (this.state.cards[i1].id === this.state.cards[i2].id) {
                // Match found
                setTimeout(() => {
                    this.state.cards[i1].matched = true;
                    this.state.cards[i2].matched = true;
                    this.state.matched++;
                    this.renderGame();
                    
                    setTimeout(() => {
                        this.state.flipped = [];
                        this.lockBoard = false;
                        this.renderGame();
                        
                        if (this.state.matched === this.state.cards.length / 2) {
                            this.state.completed = true;
                            setTimeout(() => this.gameCompleted(), 500);
                        }
                    }, 400);
                }, 300);
            } else {
                // No match
                this.state.wrong = [i1, i2];
                this.renderGame();
                
                setTimeout(() => {
                    this.state.flipped = [];
                    this.state.wrong = [];
                    this.lockBoard = false;
                    this.renderGame();
                }, 1000);
            }
        }
    }
    
    updateStats() {
        document.getElementById('moves').textContent = this.state.moves;
        document.getElementById('matches').textContent = this.state.matched;
    }
    
    updateTimer() {
        const elapsed = Math.floor((Date.now() - this.state.startTime) / 1000);
        document.getElementById('time').textContent = formatTime(elapsed);
    }
    
    gameCompleted() {
        clearInterval(this.state.timer);
        const elapsedSeconds = Math.floor((Date.now() - this.state.startTime) / 1000);
        const totalPairs = this.state.cards.length / 2;
        
        const results = {
            score: this.state.matched,
            total: totalPairs,
            moves: this.state.moves,
            time: elapsedSeconds,
            difficulty: 'easy'
        };
        
        submitGameResults(results);
    }
}

// ===== PUZZLE GAME FUNCTIONALITY =====

class PuzzleGame {
    constructor() {
        this.startTime = null;
        this.timerInterval = null;
        this.moveCount = 0;
        this.wordBank = document.getElementById('wordBank');
        
        this.init();
    }
    
    init() {
        this.setupDragAndDrop();
        this.shuffleWordBank();
        this.updateSubmitButton();
    }
    
    setupDragAndDrop() {
        document.querySelectorAll('.draggable').forEach(elem => {
            elem.addEventListener('dragstart', e => {
                e.dataTransfer.setData("text", e.target.id);
                this.startTimer();
            });
        });
        
        document.querySelectorAll('.drop-zone').forEach(zone => {
            zone.addEventListener('dragover', e => this.allowDrop(e));
            zone.addEventListener('drop', e => this.drop(e));
        });
    }
    
    startTimer() {
        if (!this.startTime) {
            this.startTime = Date.now();
            this.timerInterval = setInterval(() => {
                const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
                document.getElementById("timer").textContent = formatTime(elapsed);
            }, 1000);
        }
    }
    
    allowDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.add("dragover");
    }
    
    drop(e) {
        e.preventDefault();
        const id = e.dataTransfer.getData("text");
        const dragged = document.getElementById(id);
        e.currentTarget.appendChild(dragged);
        e.currentTarget.classList.remove("dragover");
        this.moveCount++;
        this.updateSubmitButton();
    }
    
    shuffleWordBank() {
        const items = Array.from(this.wordBank.children);
        for (let i = items.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            this.wordBank.appendChild(items[j]);
            items.splice(j, 1);
        }
    }
    
    updateSubmitButton() {
        const submitBtn = document.getElementById('submitBtn');
        const allDraggables = document.querySelectorAll('.draggable');
        const placedItems = document.querySelectorAll('.drop-zone .draggable');
        const remaining = allDraggables.length - placedItems.length;
        
        if (remaining === 0) {
            submitBtn.textContent = '✅ Submit';
            submitBtn.style.backgroundColor = '#4caf50';
            submitBtn.disabled = false;
        } else {
            submitBtn.textContent = `⏳ Place ${remaining} more item(s)`;
            submitBtn.style.backgroundColor = '#ff9800';
            submitBtn.disabled = true;
        }
    }
    
    submitPuzzle() {
        // Check if all items are placed
        const allDraggables = document.querySelectorAll('.draggable');
        const placedItems = document.querySelectorAll('.drop-zone .draggable');
        
        if (placedItems.length < allDraggables.length) {
            const remaining = allDraggables.length - placedItems.length;
            alert(`Please place all ${allDraggables.length} items before submitting. You still have ${remaining} item(s) to place.`);
            return;
        }
        
        // Prevent multiple submissions
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn.disabled) {
            return;
        }
        
        // Disable button and show loading state
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Submitting...';
        submitBtn.style.backgroundColor = '#666';
        
        // Clear any previous error messages
        document.getElementById('result').textContent = '';
        
        let score = 0;
        const total = document.querySelectorAll('.draggable').length;
        
        document.querySelectorAll('.draggable').forEach(elem => {
            if (elem.parentElement.classList.contains("drop-zone")) {
                if (elem.parentElement.id === elem.dataset.category) {
                    score++;
                }
            }
        });
        
        clearInterval(this.timerInterval);
        const elapsedSeconds = this.startTime ? Math.floor((Date.now() - this.startTime) / 1000) : 0;
        
        const results = {
            score: score,
            total: total,
            time: elapsedSeconds,
            moves: this.moveCount,
            difficulty: 'easy'
        };
        
        submitGameResults(results);
    }
}

// ===== RESULTS PAGE FUNCTIONALITY =====

function initializeResultsPage() {
    document.addEventListener('DOMContentLoaded', function() {
        const timeEl = document.getElementById('time-taken');
        if (timeEl) {
            let timeVal = timeEl.textContent.trim();
            // Time conversions
            if (/^\d+$/.test(timeVal)) {
                const timeInSeconds = parseInt(timeVal, 10);
                timeEl.textContent = formatTime(timeInSeconds);
            }
        }
    });
}

// ===== GAME INITIALIZATION =====

document.addEventListener('DOMContentLoaded', function() {
    // Initialize color game
    if (document.getElementById('board') && document.querySelector('.color-game')) {
        new ColorGame();
    }
    
    // Initialize pairs game
    if (document.getElementById('gameBoard') && document.querySelector('.pairs-game')) {
        new PairsGame();
    }
    
    // Initialize puzzle game
    if (document.getElementById('wordBank') && document.querySelector('.puzzle-game')) {
        new PuzzleGame();
    }
    
    // Initialize results page
    if (document.querySelector('.results-container')) {
        initializeResultsPage();
    }
    
    // Setup puzzle submit button
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', function() {
            if (window.puzzleGame) {
                window.puzzleGame.submitPuzzle();
            }
        });
    }
});

// Make puzzle game globally accessible for submit button
window.puzzleGame = null;
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('wordBank') && document.querySelector('.puzzle-game')) {
        window.puzzleGame = new PuzzleGame();
    }
}); 