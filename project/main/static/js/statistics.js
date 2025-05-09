$(document).ready(function() {
    const statsModal = $('#stats-modal');
    const statsBtn = $('#stats-btn');
    const closeBtn = $('.close-popup');

    // Show statistics modal
    statsBtn.on('click', function() {
        // Check if user is logged in
        $.ajax({
            url: '/api/statistics/',
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'same-origin',  // Include cookies in the request
            success: function(data) {
                updateStatisticsDisplay(data);
                statsModal.fadeIn(300);
            },
            error: function(xhr, status, error) {
                console.error('Error fetching statistics:', error);
                console.error('Status:', status);
                console.error('Response:', xhr.responseText);
                
                if (xhr.status === 401 || xhr.status === 403) {
                    // User is not authenticated
                    alert('Please log in to view your statistics.');
                    // Use window.location.replace to avoid back button issues
                    window.location.replace('/login/');
                } else {
                    // Other errors
                    alert('Failed to load statistics. Please try again later.');
                }
            }
        });
    });

    // Close statistics modal
    closeBtn.on('click', function() {
        statsModal.fadeOut(300);
    });

    // Close modal when clicking outside
    $(window).on('click', function(event) {
        if (event.target === statsModal[0]) {
            statsModal.fadeOut(300);
        }
    });

    // Update the statistics display
    function updateStatisticsDisplay(data) {
        if (!data) {
            console.error('No data received from server');
            return;
        }

        try {
            $('#games-played').text(data.games_played || 0);
            $('#win-percentage').text((data.win_percentage || 0) + '%');
            $('#current-streak').text(data.current_streak || 0);
            $('#max-streak').text(data.max_streak || 0);
            $('#avg-guesses').text((data.average_guesses || 0).toFixed(1));
        } catch (error) {
            console.error('Error updating statistics display:', error);
            alert('Error displaying statistics. Please try again.');
            statsModal.fadeOut(300);
        }
    }

    // Helper function to get CSRF token
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
}); 