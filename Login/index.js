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

async function auth(type) {
    if (type == 'login') {
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value.trim();  
        const respostatela = document.getElementById('sucess')

        if (!email || !password)
            return mostrarErro(respostatela, "Preencha todos os campos!");

        await sendRequest("login", {email, password}, respostatela);
    }
        
    if (type == 'register') {
        const email = document.getElementById('register-email').value.trim();
        const username = document.getElementById('register-username').value.trim();
        const password = document.getElementById('register-password').value.trim();
        const number = document.getElementById('register-number').value.trim();
        const respostatela = document.getElementById('error')

        if (!email  || !password || !number || !username) 
            return mostrarErro(respostatela, "Preencha todos os campos!");
        

        if (password.length < 8) 
            return mostrarErro(respostatela, "Senha deve ter pelo menos 8 digitos");
        
        
        await sendRequest("register", {email, username, password, number}, respostatela); 
    }
}


async function sendRequest(endpoint, body, resposta) {
    try {
        const resp = await fetch(`http://127.0.0.1:8000/${endpoint}`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(body),
            credentials: "include",
        });

        const data = await resp.json();

        if (resp.ok) {
                resposta.style.color = "green";
                resposta.innerText = "Login realizado com sucesso!";
        } else { 
                const dataErro = await resp.json(); // Caso responda fora da condição, o erro esperado ser gerado vai ser exibido na div de ID resposta
                resposta.innerText = dataErro.detail
                    ? `Erro: ${dataErro.detail}`
                    : "Error fetching explanation.";
            }
    } catch (err) {
        resposta.style.color = "red";
        resposta.innerText = "Erro do servidor, tente novamente mais tarde.";
    }
}

function mostrarErro(iderrorHTML, msg) {
    iderrorHTML.style.color = "red";
    iderrorHTML.innerText = msg;
}