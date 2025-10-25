// BRONZE: 1177 BC - Client-side JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('BRONZE: 1177 BC loaded');

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-info)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add loading state to action buttons (optional enhancement)
    const actionForms = document.querySelectorAll('form[method="POST"]');
    actionForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const button = this.querySelector('button[type="submit"]');
            if (button && !button.disabled) {
                button.classList.add('loading');
                button.disabled = true;
            }
        });
    });

    // Confirm dangerous actions
    const withdrawForm = document.querySelector('form[action*="withdraw"]');
    if (withdrawForm) {
        withdrawForm.addEventListener('submit', function(e) {
            if (!confirm('⚠️ Withdraw from Alliance?\n\nThis will:\n+10 Military\n-15 Stability\n-10 Prestige\n+5 Collapse\n\nContinue?')) {
                e.preventDefault();
            }
        });
    }

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
                    }
                });

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
