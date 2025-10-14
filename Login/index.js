document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.querySelector('.login');
    const registerForm = document.querySelector('.register');
    const registerLink = document.querySelector('.login .auth-sign-up a');
    const loginLink = document.querySelector('.register .auth-sign-up a');

    registerLink.addEventListener('click', (e) => {
        e.preventDefault();
        loginForm.classList.remove('active');
        registerForm.classList.add('active');
    });

    loginLink.addEventListener('click', (e) => {
        e.preventDefault();
        registerForm.classList.remove('active');
        loginForm.classList.add('active');
    });
});
