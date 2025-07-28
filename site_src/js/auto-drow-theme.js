// Auto-apply drow theme to all pages under /monday/
document.addEventListener('DOMContentLoaded', function() {
    // Check if current page is under /monday/
    if (window.location.pathname.includes('/monday/')) {
        // Find the base URL for the drow theme CSS
        var pathParts = window.location.pathname.split('/');
        var mondayIndex = pathParts.indexOf('monday');
        var depth = pathParts.length - mondayIndex - 2; // -2 for monday and the file
        var cssPath = '../'.repeat(depth) + 'drow_theme.css';
        
        // Create and inject the CSS link
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = cssPath;
        document.head.appendChild(link);
    }
});