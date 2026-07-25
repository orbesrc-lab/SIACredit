
        document.addEventListener("DOMContentLoaded", () => {
            const user = JSON.parse(localStorage.getItem('siac_user') || '{}');
            if(user.role === 'admin') {
                const crmLink = document.getElementById('menuCrm');
                if(crmLink) crmLink.style.display = 'block';
            }
        });
        