// Simple visitor counter using localStorage for demo
// For production, consider using a service like CountAPI, GoatCounter, or Umami

(function() {
    const STORAGE_KEY = 'site_visit_count';
    const API_URL = 'https://api.countapi.xyz/hit/cncsmonster.github.io/visits';
    
    async function updateCounter() {
        const counterElement = document.getElementById('visitor-count');
        if (!counterElement) return;
        
        try {
            // Try to use countapi.xyz
            const response = await fetch(API_URL);
            const data = await response.json();
            counterElement.textContent = data.value.toLocaleString();
        } catch (error) {
            // Fallback to localStorage
            let count = localStorage.getItem(STORAGE_KEY);
            if (!count) {
                count = Math.floor(Math.random() * 1000) + 100; // Simulate initial count
            } else {
                count = parseInt(count) + 1;
            }
            localStorage.setItem(STORAGE_KEY, count);
            counterElement.textContent = count.toLocaleString();
        }
    }
    
    updateCounter();
})();
