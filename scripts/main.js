document.addEventListener('DOMContentLoaded', () => {
    // Add a subtle scroll animation to elements
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.article, .project-card, .skills-container, .education-item');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementPosition < windowHeight - 100) {
                element.classList.add('visible');
            }
        });
    };
    
    // Add CSS class for animation
    const style = document.createElement('style');
    style.textContent = `
        .article, .project-card, .skills-container, .education-item {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease-out, transform 0.6s ease-out;
        }
        .article.visible, .project-card.visible, .skills-container.visible, .education-item.visible {
            opacity: 1;
            transform: translateY(0);
        }
    `;
    document.head.appendChild(style);
    
    // Initial check and scroll listener
    animateOnScroll();
    window.addEventListener('scroll', animateOnScroll);
    
    // Handle newsletter form submission
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const emailInput = newsletterForm.querySelector('input[type="email"]');
            
            if (emailInput.value) {
                // This would normally send the data to a server
                // For now, just show a thank you message
                const formParent = newsletterForm.parentElement;
                newsletterForm.style.display = 'none';
                
                const thankYouMessage = document.createElement('div');
                thankYouMessage.classList.add('thank-you-message');
                thankYouMessage.innerHTML = `
                    <h3>Thank you for subscribing!</h3>
                    <p>You've been added to the newsletter with the email: ${emailInput.value}</p>
                `;
                formParent.appendChild(thankYouMessage);
            }
        });
    }
    
    // Handle dark/light mode toggle (if we add this feature later)
    // const themeToggle = document.querySelector('.theme-toggle');
    // if (themeToggle) {
    //     themeToggle.addEventListener('click', () => {
    //         document.body.classList.toggle('light-mode');
    //         // Save preference to localStorage
    //         const currentTheme = document.body.classList.contains('light-mode') ? 'light' : 'dark';
    //         localStorage.setItem('theme', currentTheme);
    //     });
    // }
});