// BRONZE: 1177 BC - Client-side JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('BRONZE: 1177 BC loaded');

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-info)');
    alerts.forEach(alert => {
        setTimeout(() => {
            // Manually fade out and remove (no Bootstrap needed)
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.3s';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Close button functionality for alerts
    document.querySelectorAll('.btn-close').forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 0.3s';
                setTimeout(() => alert.remove(), 300);
            }
        });
    });

    // Add loading state to action buttons
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
});