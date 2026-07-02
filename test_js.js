
const user = { role: 'inst_admin' };
const isAdmin = (user.role === 'admin' || user.role === 'superadmin' || user.role === 'inst_admin');
console.log('isAdmin:', isAdmin);
if (!isAdmin) {
    console.log('Hiding items');
} else {
    console.log('Not hiding items');
}

