# Documentação da API — PedeAió

API REST do sistema de pedidos de lanches **PedeAió**, construída com Django REST Framework.

## Sumário

1. [Visão geral](#1-visão-geral)
2. [Autenticação](#2-autenticação)
3. [Resumo dos endpoints](#3-resumo-dos-endpoints)
4. [Autenticação (tokens)](#4-tokens)
5. [Usuários](#5-usuários)
6. [Endereços](#6-endereços)
7. [Categorias](#7-categorias)
8. [Produtos](#8-produtos)
9. [Carrinho](#9-carrinho)
10. [Pedidos](#10-pedidos)
11. [Entregas](#11-entregas)
12. [Erros e limites de uso](#12-erros-e-limites-de-uso)
13. [Fluxo completo de exemplo](#13-fluxo-completo-de-exemplo)

---

## 1. Visão geral

| Item | Valor |
|---|---|
| URL base | `http://127.0.0.1:8000/api/v1/` |
| Formato | JSON (`Content-Type: application/json`) |
| Exceção | Cadastro de produto com imagem usa `multipart/form-data` |
| Autenticação | JWT (Bearer token) ou sessão do navegador |
| Valores em dinheiro | Enviados como texto com 2 casas, ex.: `"45.00"` |
| Datas | Formato ISO 8601, ex.: `"2026-11-25T22:15:29-03:00"` |

### Legenda de permissões

| Ícone | Quem pode acessar |
|---|---|
| Qualquer pessoa, sem login |
| Usuário autenticado |
| Administrador (`is_staff`) para escrever; leitura é pública |
| Usuário autenticado com `is_entregador = true` |

---

## 2. Autenticação

A API usa **JWT** (JSON Web Token).

1. Faça login em `POST /token/` e receba um `access` e um `refresh`.
2. Envie o `access` em todas as requisições protegidas:

```
Authorization: Bearer <access>
```

| Token | Validade |
|---|---|
| `access` | 30 minutos |
| `refresh` | 1 dia |

Quando o `access` expirar, gere outro com `POST /token/refresh/`.
A API também aceita a sessão do navegador (quem está logado no site consegue acessar as rotas protegidas pelo navegador).

---

## 3. Resumo dos endpoints

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| POST | `/token/` | Login (retorna tokens) |
| POST | `/token/refresh/`  | Renova o token de acesso |
| POST | `/token/blacklist/` | Invalida um refresh token (logout) |
| POST | `/cadastro/`  | Cadastra um usuário |
| GET | `/eu/` | Dados do usuário logado |
| PUT / PATCH | `/eu/`  | Atualiza dados do usuário logado |
| GET | `/enderecos/`  | Lista os endereços do usuário |
| POST | `/enderecos/`  | Cadastra um endereço |
| PUT / PATCH | `/endereco_atualizar/{id}/`  | Atualiza um endereço |
| DELETE | `/endereco_deletar/{id}/`  | Exclui um endereço |
| GET | `/categorias/`  | Lista as categorias |
| POST | `/categorias/`  | Cria uma categoria |
| PUT / PATCH | `/categoria_atualizar/{id}/`  | Atualiza uma categoria |
| DELETE | `/categoria_deletar/{id}/`  | Exclui uma categoria |
| GET | `/produtos/` | Lista produtos (com busca e filtro) |
| POST | `/produtos/`  | Cria um produto |
| GET | `/produto_detalhes/{id}/` | Detalhes de um produto |
| PUT / PATCH | `/produto_atualizar/{id}/` | Atualiza um produto |
| DELETE | `/produto_deletar/{id}/`  | Exclui um produto |
| GET | `/carrinho/` | Mostra o carrinho |
| POST | `/carrinho_adicionar/{produto_id}/`  | Adiciona um produto ao carrinho |
| POST | `/carrinho_aumentar/{item_id}/` | Aumenta a quantidade de um item |
| POST | `/carrinho_diminuir/{item_id}/`  | Diminui a quantidade de um item |
| DELETE | `/carrinho_remover/{item_id}/` | Remove um item do carrinho |
| GET | `/pedidos/`  | Lista os pedidos do usuário |
| POST | `/pedidos/` | Cria um pedido a partir do carrinho |
| GET | `/entregas/` | Lista entregas disponíveis e as suas |
| POST | `/entregas/{pedido_id}/aceitar/` | Aceita uma entrega |
| POST | `/entregas/{pedido_id}/concluir/` | Conclui uma entrega |

---

## 4. Tokens

### `POST /token/` — Login 

O campo `username` recebe o **e-mail** do usuário.

**Corpo da requisição**
```json
{
  "username": "maria@email.com",
  "password": "MinhaSenha123"
}
```

**Resposta — 200 OK**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

| Código | Quando acontece |
|---|---|
| 200 | Login realizado |
| 401 | E-mail ou senha incorretos |
| 429 | Mais de 10 tentativas por minuto (mesmo IP) |

### `POST /token/refresh/` — Renovar o access 

**Corpo**
```json
{ "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```

**Resposta — 200 OK**
```json
{ "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```
Retorna `401` se o refresh for inválido ou estiver expirado.

### `POST /token/blacklist/` — Logout

Invalida o refresh token, que não poderá mais ser usado.

**Corpo**
```json
{ "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```
**Resposta — 200 OK** (corpo vazio `{}`).

---

## 5. Usuários

### `POST /cadastro/` — Cadastrar usuário

| Campo | Tipo | Obrigatório | Regras |
|---|---|---|---|
| `cpf` | texto | sim | Exatamente 11 números, sem pontos e traço |
| `first_name` | texto | sim | Não pode ser vazio |
| `last_name` | texto | não | |
| `email` | texto | sim | Deve ser um e-mail único |
| `nascimento` | data | sim | Formato `AAAA-MM-DD` |
| `password` | texto | sim | Segue as regras de senha do Django |
| `password2` | texto | sim | Deve ser igual a `password` |

**Corpo**
```json
{
  "cpf": "12345678901",
  "first_name": "Maria",
  "last_name": "Silva",
  "email": "maria@email.com",
  "nascimento": "2000-05-20",
  "password": "MinhaSenha123",
  "password2": "MinhaSenha123"
}
```

**Resposta — 201 Created** (já devolve os tokens, o usuário não precisa fazer login)
```json
{
  "usuario": {
    "cpf": "12345678901",
    "email": "maria@email.com",
    "first_name": "Maria",
    "last_name": "Silva",
    "nascimento": "2000-05-20",
    "is_entregador": false,
    "is_staff": false
  },
  "refresh": "eyJhbGciOi...",
  "access": "eyJhbGciOi..."
}
```

**Erro — 400 Bad Request**
```json
{ "email": ["Já existe um usuário com este e-mail."] }
```

| Código | Quando acontece |
|---|---|
| 201 | Usuário criado |
| 400 | Dados inválidos (CPF, e-mail repetido, senhas diferentes etc.) |
| 429 | Mais de 10 cadastros por hora (mesmo IP) |

### `GET /eu/` — Meus dados 

**Resposta — 200 OK**
```json
{
  "cpf": "12345678901",
  "email": "maria@email.com",
  "first_name": "Maria",
  "last_name": "Silva",
  "nascimento": "2000-05-20",
  "is_entregador": false,
  "is_staff": false
}
```

### `PUT /eu/` e `PATCH /eu/` — Atualizar meus dados 

Campos editáveis: `first_name`, `last_name`, `nascimento`.
Os campos `cpf`, `email`, `is_entregador` e `is_staff` são somente leitura.
Use `PATCH` para enviar só o que mudou. O `PUT` exige `nascimento`.

**Corpo (PATCH)**
```json
{ "first_name": "Maria Clara" }
```
**Resposta — 200 OK:** o usuário atualizado. **400** se os dados forem inválidos.

---

## 6. Endereços

Todas as rotas exigem login e só enxergam endereços do **próprio usuário**.

### Objeto Endereço
```json
{
  "id": 3,
  "rua": "Rua das Flores",
  "numero": "120",
  "cidade": "Canguaretama",
  "estado": "RN"
}
```
`estado` deve ter 2 letras (a API converte para maiúsculas).

### `GET /enderecos/` — Listar
**Resposta — 200 OK:** lista de objetos Endereço.

### `POST /enderecos/` — Cadastrar
**Corpo**
```json
{
  "rua": "Rua das Flores",
  "numero": "120",
  "cidade": "Canguaretama",
  "estado": "RN"
}
```
**Resposta — 201 Created:** o endereço criado. **400** se houver erro de validação.

### `PUT / PATCH /endereco_atualizar/{id}/` — Atualizar
**Resposta — 200 OK:** o endereço atualizado.
Retorna **404** se o endereço não existir ou for de outro usuário.

### `DELETE /endereco_deletar/{id}/` — Excluir

| Código | Quando acontece |
|---|---|
| 204 | Excluído (sem corpo) |
| 404 | Não existe ou é de outro usuário |
| 409 | Está vinculado a pedidos e não pode ser excluído |

```json
{ "detail": "Este endereço não pode ser excluído porque está vinculado a um ou mais pedidos." }
```

---

## 7. Categorias

Leitura pública. Criar, editar e excluir exigem  administrador.

### Objeto Categoria
```json
{ "id": 2, "nome": "Pizzas" }
```

### `GET /categorias/` — Listar 
Retorna as categorias em ordem alfabética. **200 OK**.

### `POST /categorias/` — Criar 
**Corpo**
```json
{ "nome": "Bebidas" }
```
**Resposta — 201 Created:** a categoria criada.

### `PUT / PATCH /categoria_atualizar/{id}/` — Atualizar 
**Resposta — 200 OK**, ou **404** se não existir.

### `DELETE /categoria_deletar/{id}/` — Excluir 

| Código | Quando acontece |
|---|---|
| 204 | Excluída |
| 404 | Não existe |
| 409 | Existem produtos vinculados à categoria |

| Código geral | Significado |
|---|---|
| 401 | Não enviou token (em rotas de escrita) |
| 403 | Está logado, mas não é administrador |

---

## 8. Produtos

Leitura pública . Criar, editar e excluir exigem administrador.

### Objeto Produto
```json
{
  "id": 1,
  "nome": "Pizza de calabresa",
  "descricao": "Pizza com calabresa, cebola e azeitonas.",
  "preco": "45.00",
  "categoria": 2,
  "categoria_nome": "Pizzas",
  "imagem": "http://127.0.0.1:8000/media/produtos/calabresa.jpg",
  "disponivel": true
}
```
`imagem` é `null` quando o produto não tem foto. `categoria` é o **id** da categoria.

### `GET /produtos/` — Listar 

Parâmetros opcionais na URL:

| Parâmetro | Descrição | Exemplo |
|---|---|---|
| `buscar` | Procura no nome e na descrição | `?buscar=calabresa` |
| `categoria` | Filtra pelo id da categoria | `?categoria=2` |

Podem ser combinados: `/produtos/?buscar=queijo&categoria=2`.
**Resposta — 200 OK:** lista de produtos em ordem alfabética.

### `GET /produto_detalhes/{id}/` — Detalhes 
**200 OK** com o produto, ou **404** se não existir.

### `POST /produtos/` — Criar

Enviar como **`multipart/form-data`** (para poder enviar a imagem).

| Campo | Tipo | Obrigatório | Regras |
|---|---|---|---|
| `nome` | texto | sim | Até 100 caracteres |
| `descricao` | texto | sim | |
| `preco` | decimal | sim | Maior que zero |
| `categoria` | número | sim | Id de uma categoria existente |
| `imagem` | arquivo | não | Imagem do produto |
| `disponivel` | booleano | não | Padrão: `true` |

**Resposta — 201 Created:** o produto criado. **400** se houver erro de validação.

### `PUT / PATCH /produto_atualizar/{id}/` — Atualizar 
`PATCH` altera só os campos enviados. `PUT` exige todos os campos obrigatórios.

**Exemplo (PATCH): marcar como indisponível**
```json
{ "disponivel": false }
```
**Resposta — 200 OK:** o produto atualizado.

### `DELETE /produto_deletar/{id}/` — Excluir 

| Código | Quando acontece |
|---|---|
| 204 | Excluído |
| 404 | Não existe |
| 409 | O produto faz parte de pedidos e não pode ser excluído |

---

## 9. Carrinho

Todas as rotas exigem login . Cada usuário tem um único carrinho.

Todas as rotas do carrinho devolvem o **carrinho atualizado** neste formato:

```json
{
  "itens": [
    {
      "id": 7,
      "produto": {
        "id": 1,
        "nome": "Pizza de calabresa",
        "descricao": "Pizza com calabresa, cebola e azeitonas.",
        "preco": "45.00",
        "categoria": 2,
        "categoria_nome": "Pizzas",
        "imagem": "http://127.0.0.1:8000/media/produtos/calabresa.jpg",
        "disponivel": true
      },
      "quantidade": 2,
      "subtotal": "90.00"
    }
  ],
  "total": "90.00",
  "quantidade_itens": 1
}
```

>  Atenção: `id` dentro de `itens` é o id do **item do carrinho**, e não o id do produto.
> Ele é o valor usado em `{item_id}` nas rotas de aumentar, diminuir e remover.

### `GET /carrinho/` — Ver o carrinho
**200 OK**. Se o carrinho estiver vazio: `{"itens": [], "total": "0.00", "quantidade_itens": 0}`.

### `POST /carrinho_adicionar/{produto_id}/` — Adicionar produto
Não precisa de corpo. Se o produto já está no carrinho, soma 1 à quantidade.

| Código | Quando acontece |
|---|---|
| 201 | Produto novo no carrinho |
| 200 | Produto já estava no carrinho (quantidade +1) |
| 400 | Produto indisponível |
| 404 | Produto não existe |

### `POST /carrinho_aumentar/{item_id}/` — Aumentar quantidade
Soma 1 à quantidade. **200 OK**; **400** se o produto estiver indisponível; **404** se o item não for seu.

### `POST /carrinho_diminuir/{item_id}/` — Diminuir quantidade
Subtrai 1. Se a quantidade era 1, o item é removido. **200 OK**; **404** se o item não for seu.

### `DELETE /carrinho_remover/{item_id}/` — Remover item
Remove o item por completo. **200 OK** com o carrinho atualizado; **404** se o item não for seu.

---

## 10. Pedidos

Todas as rotas exigem login.

### Objeto Pedido
```json
{
  "id": 15,
  "endereco": {
    "id": 3,
    "rua": "Rua das Flores",
    "numero": "120",
    "cidade": "Canguaretama",
    "estado": "RN"
  },
  "itens": [
    {
      "id": 21,
      "produto": { "id": 1, "nome": "Pizza de calabresa", "preco": "45.00", "...": "..." },
      "quantidade": 2,
      "preco_unitario": "45.00",
      "subtotal": "90.00"
    }
  ],
  "historico": [
    {
      "id": 40,
      "status": "Pendente",
      "alterado_por": "maria@email.com",
      "criado_em": "2026-11-25T22:15:29-03:00"
    }
  ],
  "entregador": null,
  "subtotal": "90.00",
  "taxa_entrega": "5.00",
  "desconto": "0.00",
  "valor_total": "95.00",
  "status": "Pendente",
  "forma_pagamento": "",
  "pago": false,
  "pago_em": null,
  "troco_para": null,
  "criado_em": "2026-11-25T22:15:29-03:00"
}
```

Como o valor é calculado: `valor_total = subtotal - desconto + taxa_entrega`.

### Status do pedido

| Status | Próximos status possíveis |
|---|---|
| Pendente | Preparando, Cancelado |
| Preparando | Pronto para entrega, Cancelado |
| Pronto para entrega | Saiu para entrega, Cancelado |
| Saiu para entrega | Entregue |
| Entregue | — |
| Cancelado | — |

### Formas de pagamento
`Pix`, `Cartão` (na entrega) e `Dinheiro` (na entrega). No momento, a forma de pagamento é escolhida pelo site, e não por esta API, então pedidos criados pela API ficam com `forma_pagamento` vazio.

### `GET /pedidos/` — Listar meus pedidos
Retorna os pedidos do usuário logado, do mais recente para o mais antigo. **200 OK**.

### `POST /pedidos/` — Criar pedido a partir do carrinho

**Corpo**
```json
{ "endereco": 3 }
```

| Campo | Tipo | Descrição |
|---|---|---|
| `endereco` | número | Id de um endereço **do próprio usuário** |

O pedido leva todos os itens do carrinho, que fica vazio em seguida.

**Taxas de entrega por cidade**

| Cidade | Taxa |
|---|---|
| Canguaretama | R$ 5,00 |
| Barra do Cunhaú | R$ 7,00 |
| Goianinha | R$ 8,00 |
| Natal | R$ 15,00 |

**Respostas**

| Código | Quando acontece |
|---|---|
| 201 | Pedido criado (retorna o objeto Pedido) |
| 400 | Carrinho vazio |
| 400 | Há produtos indisponíveis no carrinho |
| 400 | Endereço não informado |
| 400 | Não há entrega para a cidade do endereço |
| 404 | Endereço não existe ou é de outro usuário |

**Exemplo de erro — produtos indisponíveis**
```json
{
  "detail": "Remova do carrinho os produtos indisponíveis.",
  "produtos": ["Pizza de 4 queijos"]
}
```

>  Pedidos criados pela API **não aceitam cupom de desconto** (o campo `desconto` vem sempre `"0.00"`). Os cupons funcionam apenas pelo site.

---

## 11. Entregas

Rotas exclusivas para entregadores . Quem não for entregador recebe **403 Forbidden**:

```json
{ "detail": "Apenas entregadores podem acessar esta área." }
```

### Objeto Entrega
```json
{
  "id": 9,
  "pedido": { "id": 15, "status": "Pronto para entrega", "...": "..." },
  "data_saida": null,
  "data_conclusao": null,
  "observacoes": "",
  "criado_em": "2026-11-25T22:15:29-03:00"
}
```
O campo `pedido` traz o objeto Pedido completo.

### `GET /entregas/` — Listar entregas
Retorna, juntas, as entregas **disponíveis** (pedidos com status *Pronto para entrega* e sem entregador) e as entregas **do próprio entregador**.
**200 OK** ou **403** se não for entregador.

### `POST /entregas/{pedido_id}/aceitar/` — Aceitar entrega
Não precisa de corpo. O entregador assume o pedido, que muda para **Saiu para entrega**, e o horário de saída é registrado.

| Código | Quando acontece |
|---|---|
| 200 | Entrega aceita (retorna o objeto Entrega) |
| 400 | O pedido não está disponível (status diferente de *Pronto para entrega*) |
| 403 | O usuário não é entregador |
| 404 | Pedido não encontrado |
| 409 | O pedido já foi aceito por outro entregador |

Se o próprio entregador chamar a rota de novo para um pedido que já é dele, a API responde 200 com a entrega atual.

### `POST /entregas/{pedido_id}/concluir/` — Concluir entrega
Não precisa de corpo. O pedido muda para **Entregue**, é marcado como **pago** (se ainda não estava) e o horário de conclusão é registrado.

| Código | Quando acontece |
|---|---|
| 200 | Entrega concluída (retorna o objeto Entrega) |
| 400 | O pedido não está com status *Saiu para entrega* |
| 403 | O usuário não é entregador, ou o pedido não está atribuído a ele |
| 404 | Pedido não encontrado |

---

## 12. Erros e limites de uso

### Códigos de status usados

| Código | Significado |
|---|---|
| 200 | OK |
| 201 | Criado com sucesso |
| 204 | Sucesso, sem conteúdo (exclusões) |
| 400 | Requisição inválida (dados incorretos) |
| 401 | Não autenticado (token ausente, inválido ou expirado) |
| 403 | Sem permissão para esta ação |
| 404 | Recurso não encontrado |
| 409 | Conflito (ex.: item vinculado a pedidos) |
| 429 | Muitas requisições |

### Formato dos erros

Erro geral:
```json
{ "detail": "Mensagem explicando o problema." }
```

Erro de validação de campos:
```json
{
  "preco": ["O preço deve ser maior que zero."],
  "categoria": ["Este campo é obrigatório."]
}
```

### Limites de uso (anti-abuso)

| Rota | Limite |
|---|---|
| `POST /token/` | 10 requisições por minuto (por IP) |
| `POST /cadastro/` | 10 requisições por hora (por IP) |

---

## 13. Fluxo completo de exemplo

Fazendo um pedido do começo ao fim:

1. **Cadastrar-se:** `POST /cadastro/` (ou `POST /token/` se já tiver conta) e guardar o `access`.
2. **Ver os produtos:** `GET /produtos/`.
3. **Cadastrar um endereço:** `POST /enderecos/` e anotar o `id` retornado.
4. **Adicionar ao carrinho:** `POST /carrinho_adicionar/1/` (repetir para outros produtos).
5. **Conferir o carrinho:** `GET /carrinho/`.
6. **Criar o pedido:** `POST /pedidos/` com `{"endereco": <id do endereço>}`.
7. **Acompanhar:** `GET /pedidos/` e olhar o campo `status` e o `historico`.

Em todas as etapas protegidas, envie o cabeçalho `Authorization: Bearer <access>`.