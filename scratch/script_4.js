
(function(){
    const user = JSON.parse(localStorage.getItem('siac_user') || '{}');
    const role = user.role || localStorage.getItem('user_role') || '';
    if(['admin', 'super_admin', 'inst_admin', 'lider'].includes(role)){
        const b = document.getElementById('menuBackup');
        if(b) b.style.display = 'block';
    }
})();
