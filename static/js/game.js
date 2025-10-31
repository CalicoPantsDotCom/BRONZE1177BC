// BRONZE: 1177 BC - Client-side JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('BRONZE: 1177 BC loaded');

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-info)');
    alerts.forEach(alert => {
        setTimeout(() => {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {
                console.error('Error dismissing alert:', e);
            }
        }, 5000);
    });

    // Add loading state to action buttons and error handling
    const actionForms = document.querySelectorAll('form[method="POST"]');
    actionForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            try {
                const button = this.querySelector('button[type="submit"]');
                if (button && !button.disabled) {
                    button.classList.add('loading');
                    button.disabled = true;
                    
                    // Re-enable button after timeout in case server doesn't respond
                    setTimeout(() => {
                        try {
                            button.classList.remove('loading');
                            button.disabled = false;
                        } catch (err) {
                            console.error('Error re-enabling button:', err);
                        }
                    }, 10000); // 10 second timeout
                }
            } catch (err) {
                console.error('Error handling form submit:', err);
                // Allow form to submit even if there's an error
            }
        });
    });

    // Confirm dangerous actions
    const withdrawForm = document.querySelector('form[action*="withdraw"]');
    if (withdrawForm) {
        withdrawForm.addEventListener('submit', function(e) {
            try {
                if (!confirm('⚠️ Withdraw from Alliance?\n\nThis will:\n+10 Military\n-15 Stability\n-10 Prestige\n+5 Collapse\n\nContinue?')) {
                    e.preventDefault();
                }
            } catch (err) {
                console.error('Error showing confirmation:', err);
            }
        });
    }

    // Log page errors for debugging
    window.addEventListener('error', function(e) {
        console.error('Page error:', e.error);
    });

    // Optional: AJAX action handling (if you want instant updates without page reload)
    // Uncomment to enable AJAX mode
    /*
    actionForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const button = this.querySelector('button[type="submit"]');
            button.classList.add('loading');
            button.disabled = true;

            try {
                const response = await fetch(this.action, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: new FormData(this)
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                if (data.game_over) {
                    window.location.href = '/victory';
                } else {
                    // Update UI with new game state
                    updateGameUI(data.game);
                    displayMessages(data.messages);
                }
            } catch (error) {
                console.error('Action failed:', error);
                alert('Action failed. Please refresh the page.');
                // Refresh page on error
                window.location.reload();
            } finally {
                button.classList.remove('loading');
                button.disabled = false;
            }
        });
    });

    function updateGameUI(game) {
        // Update resources
        document.querySelector('.card-body span:contains("Grain")').nextElementSibling.textContent = game.grain;
        // ... (implement full UI update)
    }

    function displayMessages(messages) {
        const messageArea = document.getElementById('message-area');
        messageArea.innerHTML = '';
        messages.forEach(msg => {
            const alert = document.createElement('div');
            alert.className = `alert alert-${msg.type} alert-dismissible fade show`;
            alert.innerHTML = `${msg.text} <button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
            messageArea.appendChild(alert);
        });
    }
    */
});
