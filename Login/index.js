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
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value.trim();  
        const respostatela = document.getElementById('sucess')

        respostatela.innerText = "";
        respostatela.style.color = "";

        if (!username || !password) {
            respostatela.style.color = "red";
            respostatela.innerText = "Preencha todos os campos!";
            return;
        }

        try {
            const resp = await fetch(`http://127.0.0.1:8000/${type}`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username, password}),
                credentials: "include"
            });

            if (resp.ok) {
                respostatela.style.color = "green";
                respostatela.innerText = "Login realizado com sucesso!";
            } else { 
                const dataErro = await resp.json(); // Caso responda fora da condição, o erro esperado ser gerado vai ser exibido na div de ID resposta
                respostatela.innerText = dataErro.detail
                    ? `Erro: ${dataErro.detail}`
                    : "Error fetching explanation.";
            }
        } catch (error) {
            respostatela.style.color = "red";
            respostatela.innerText = "Ocorreu um erro no servidor, tente novamente mais tarde!";
        }    
    } else if (type == 'register') {
        const username = document.getElementById('register-username').value.trim();
        const password = document.getElementById('register-password').value.trim();  
        const respostatela = document.getElementById('error')
        
        respostatela.innerText = "";
        respostatela.style.color = "";

        if (!username  || !password) {
            respostatela.style.color = "red";
            respostatela.innerText = "Preencha todos os campos!";
            return;
        }

        

        if (password.length < 8) {
            respostatela.style.color = "red";
            respostatela.innerText = "Senha deve ter pelo menos 8 digitos";
            return;
        }
    
        try {
            const resp = await fetch(`http://127.0.0.1:8000/${type}`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username, password})
            });

            if (resp.ok) {
                respostatela.style.color = "green";
                respostatela.innerText = "Registro realizado com sucesso!";
            } else { 
                const dataErro = await resp.json(); // Caso responda fora da condição, o erro esperado ser gerado vai ser exibido na div de ID resposta
                respostatela.innerText = dataErro.detail
                    ? `Erro: ${dataErro.detail}`
                    : "Error fetching explanation.";
            }
        } catch (error) {
            respostatela.style.color = "red";
            respostatela.innerText = "Ocorreu um erro no servidor, tente novamente mais tarde!";
        } 
    }

    
}

