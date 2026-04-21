document.addEventListener('DOMContentLoaded', function () {
    // Manejo de alertas automáticas
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 3000);
    });

    console.log("ERP Limpieza System Initialized");
});