
// Exoplanet names for each slide
const exoplanets = [
    'Proxima Centauri b',
    'OGLE-2005-blg-390l',
    'Poltergeist',
];

let typed;
let currentIndex = 0;

// Function to update typed text
function updateTyped(index) {
    if (typed) {
        typed.destroy();
    }
    
    typed = new Typed('#typed', {
        strings: [exoplanets[index]],
        typeSpeed: 80,
        showCursor: true,
        cursorChar: '|',
        loop: false
    });
}

// Initialize Swiper
const swiper = new Swiper('.swiper', {
    direction: 'horizontal',
    loop: true,
    speed: 1500,
    effect: 'fade',
    fadeEffect: {
        crossFade: true
    },
    autoplay: {
        delay: 5000,
        disableOnInteraction: false,
    },
    pagination: {
        el: '.swiper-pagination',
        clickable: true,
    },
    on: {
        init: function() {
            updateTyped(0);
        },
        slideChange: function() {
            currentIndex = this.realIndex;
            updateTyped(currentIndex);
        }
    }
});

// Smooth scroll for navigation links
document.querySelectorAll('.nav-link[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        const targetSection = document.querySelector(targetId);
        
        if (targetSection) {
            targetSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
