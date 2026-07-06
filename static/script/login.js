const botao = document.querySelector("#entrar");
const erro = document.querySelector("#erro");

botao.addEventListener("click", (event) => {

    event.preventDefault();
    const usuario = document.querySelector("#usuario").value;
    const senha = document.querySelector("#senha").value;
    if(usuario === "admin" && senha === "1234"){
        window.location.href = "perfil.html";
    }else{
        erro.innerHTML = "Usuário ou senha incorretos";
        erro.style.color = "red";
        erro.style.marginTop = "10px";
    }

});