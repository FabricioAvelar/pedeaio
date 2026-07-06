console.log("Página de perfil carregada com sucesso!");

// BOTÃO SAIR

const sair = document.querySelector(".sair");

sair.addEventListener("click", () => {

    const confirmar = confirm("Deseja realmente sair da conta?");

    if(confirmar){
        window.location.href = "login.html";
    }

});

