
// Auto-load drow theme for Monday campaign pages
(function() {
    // Check if we're on a Monday campaign page
    const currentPath = window.location.pathname;
    const isMondayPage = currentPath.includes('/monday/') || 
                        currentPath.includes('/dnd_session_logs/monday/') ||
                        currentPath.endsWith('/monday') ||
                        currentPath.endsWith('/monday.html');
    
    if (isMondayPage) {
        // Create and inject the drow theme CSS link
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.type = 'text/css';
        
        // Determine the correct path to the CSS file based on current location
        const pathParts = currentPath.split('/');
        const mondayIndex = pathParts.findIndex(part => part === 'monday');
        
        if (mondayIndex !== -1) {
            // Calculate relative path back to the monday directory
            const levelsDeep = pathParts.length - mondayIndex - 2; // -2 for monday and current page
            const relativePath = '../'.repeat(Math.max(0, levelsDeep));
            link.href = relativePath + 'drow_theme.css';
        } else {
            // Fallback to absolute path
            link.href = '/dnd_session_logs/monday/drow_theme.css';
        }
        
        // Add to document head
        document.head.appendChild(link);
        
        console.log('Drow theme loaded for Monday campaign page');
    }
})();