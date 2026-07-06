// Seleciona todos os itens do carrinho
const items = document.querySelectorAll(".item");

// Valores fixos (você pode mudar depois)
const desconto = 100.00;

// Elementos do resumo
const produtosEl = document.querySelector(".summary .line span:last-child");
const totalEl = document.querySelector(".total span:last-child");

// Atualiza os valores do resumo
function atualizarResumo() {
    let subtotal = 0;

    items.forEach(item => {
        const qtd = parseInt(item.querySelector(".qty span").innerText);
        const preco = parseFloat(item.dataset.price);
        subtotal += qtd * preco;
    });

    produtosEl.innerText = `R$ ${subtotal.toFixed(2).replace(".", ",")}`;
    totalEl.innerText = `R$ ${(subtotal - desconto).toFixed(2).replace(".", ",")}`;
}

// Configura os botões + e -
items.forEach(item => {
    const btnMais = item.querySelector(".qty button:last-child");
    const btnMenos = item.querySelector(".qty button:first-child");
    const qtdEl = item.querySelector(".qty span");
    const precoEl = item.querySelector(".price");

    const precoUnitario = parseFloat(item.dataset.price);

    btnMais.addEventListener("click", () => {
        let qtd = parseInt(qtdEl.innerText);
        qtd++;
        qtdEl.innerText = qtd;
        precoEl.innerText = `R$ ${(qtd * precoUnitario).toFixed(2).replace(".", ",")}`;
        atualizarResumo();
    });

    btnMenos.addEventListener("click", () => {
        let qtd = parseInt(qtdEl.innerText);
        if (qtd > 1) {
            qtd--;
            qtdEl.innerText = qtd;
            precoEl.innerText = `R$ ${(qtd * precoUnitario).toFixed(2).replace(".", ",")}`;
            atualizarResumo();
        }
    });
});

// Atualiza ao carregar a página
atualizarResumo();
