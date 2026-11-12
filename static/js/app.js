// adicionando o fundo via classe atraves do js
const titulo = document.title;
const corpo = document.body;
const carrinho_b = document.querySelector(".carrinho-badge");
const con_carrinho = document.querySelector(".conectar-bagde");
const b_card = document.querySelector(".b-card");
const logar = document.querySelector("#logar");

//formatar padrão BRL (REAL BRASILEIRO ou BRAZILIAN REAL - BRL)
const brl = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });



const { page, id } = document.querySelector("main").dataset;

const links = document.querySelectorAll("nav a")

//Aqui esta os svg dos ICONES editar e Deletar, usar quando popular a tabela com as informações do banco.
const iconeEditar = '<svg viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>';
const iconeDeletar = '<svg viewBox="0 0 24 24"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/></svg>';
const imgPreview = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='56' height='56'><rect width='56' height='56' fill='%23eee'/><path d='M14 40l10-12 8 9 5-6 5 9z' fill='%23bbb'/><circle cx='21' cy='19' r='4' fill='%23bbb'/></svg>"




//Links do nav, realiza uma buscar entre as tag e verificar se o conteudo do href é igual  
//URL que esta definida e troca a class
links.forEach(link => {
    if (link.getAttribute('href') === window.location.pathname) {
        link.classList.add('ativo')
    }

})

function dadosLocal(chave) {
    // Verificando se tem algo no storage, deixei dinamico pois assim eu posso verificar outras chaves.
    try {
        return lista = JSON.parse(localStorage.getItem(chave)) || [];
    } catch {
        // Se der erro para gerar ele retorna vazio e pode seguir.
        return lista = [];
    }
}

function mani_dadosLocal(chave, dados) {
    localStorage.setItem(chave, JSON.stringify(dados))
}

function validar_cod() {
    const codProduto = document.querySelector('#codProduto')

    codProduto.addEventListener('input', (e) => {
        codProduto.value = codProduto.value.replace(/\D/g, "")
    })
}

//Aqui fuciona para adicionar itens ao carrinho e no o icone balão que fica no svg do carrinho, assim informar o cliente que tem produtos no mesmo
function adiciona_item_carrinho() {
    b_card.addEventListener('click', (e) => {
        const link = e.target.closest(".conectar-bagde");
        if (!link) return;

        e.preventDefault();
        let dados = dadosLocal('produtos');
        produto = dados.find(item => item.id === link.dataset.id_item)
        
        // Verifica se já existe e se exister soma 
        if (produto) {
            produto.qtd += 1
            alert(`${produto.item} qtd: ${produto.qtd}`)
        }

        else {
            // Caso não tem o produto, vai criar e adicionar .
            dados.push({ 
                id: link.dataset.id_item, 
                item: link.dataset.item,
                preco: link.dataset.preco, 
                imagem: link.dataset.imagem, 
                qtd: 1 
            })
            
        }
        
        mani_dadosLocal('produtos', dados)
        
        carrinho_b.textContent = dados.length;

    });
}

function lista_item_carrinho() {

    let produtos = dadosLocal("produtos")

    const itens_carrinho = document.querySelector(".carrinho-itens")

    // svg de imagem casso não tenha. será implementado depois
    const img = '<img src="data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20160%2090%22%3E%3Crect%20width%3D%22160%22%20height%3D%2290%22%20fill%3D%22%23fff%22%2F%3E%3Ccircle%20cx%3D%2280%22%20cy%3D%2240%22%20r%3D%2222%22%20fill%3D%22none%22%20stroke%3D%22%23ccc%22%20stroke-width%3D%228%22%2F%3E%3Ctext%20x%3D%2280%22%20y%3D%2282%22%20font-size%3D%2211%22%20font-family%3D%22sans-serif%22%20font-weight%3D%22700%22%20fill%3D%22%23aaa%22%20text-anchor%3D%22middle%22%3ESem%20Imagem%3C%2Ftext%3E%3C%2Fsvg%3E"'

    // Para reutilizar essa parte é melhor garantir que não tenha nada no html que recebe os itens, para o for sempre escrever limpo
    itens_carrinho.innerHTML = '';

    for (let i = 0; i < produtos.length; i++) {
        const imagem = (produtos[i]['imagem'] || '').trim() || img;
        let item =
            `<article class="item">
            <img src="${imagem}"
                alt="${produtos[i]['item']}">

            <div class="item-info">
                <h2 class="item-titulo">${produtos[i]['item']}</h2>
                <p class="item-preco-un">R$ ${produtos[i]['preco']} un.</p>
                <a href="#" class="item-remover">Remover</a>
            </div>

            <div class="item-qtd" data-id_item="${produtos[i]['id']}">
                <a href="#" class="diminuir" aria-label="Diminuir">−</a>
                <span class="qtd">${produtos[i]['qtd']}</span>
                <a href="#" class="aumentar" aria-label="Aumentar">+</a>
            </div>`

        itens_carrinho.innerHTML += item
    }
}

//Mascara para celular 
function mascara_celular() {
    const celular = document.querySelector("#celular")

    celular.addEventListener('input', (e) => {
        celular.value = celular.value.replace(/\D/g, "").slice(0, 11).replace(/^(\d{2})(\d)/, '($1) $2').replace(/(\d{5})(\d)/, '$1-$2')
    })

}

async function filtrar() {
    const filtro = document.querySelector("select[name='categoria-s']")
    const pesquisar = document.querySelector("input[name='pesquisa']")

    dados = {
        filtro: filtro.value,
        busca: pesquisar.value
    }

    response = await fetch("/filtro/departamentos", {
        method: 'POST',
        headers: { "Content-Type": "Application/json" },
        body: JSON.stringify(dados)
    })

    if (response.status == 200) {
        const html = await response.text()

        const doc_html = new DOMParser().parseFromString(html, "text/html");

        const prod_filtro = doc_html.querySelector(".b-card")

        document.querySelector(".b-card").innerHTML = prod_filtro.innerHTML;
    } else {
        document.querySelector(".b-card").innerHTML = "";
    }

}


function calcular_carrinho() {
    const subtotal = document.querySelector(".subtotal").lastElementChild
    const total = document.querySelector(".total").lastElementChild
    let frete = 25

    let produtos = dadosLocal("produtos")

    let novo_subtotal = 0
    let novo_total = 0

    for (let i = 0; i < produtos.length; i++) {
        let auxiliar = 0
        auxiliar = parseFloat(produtos[i]['qtd']) * parseFloat(produtos[i]['preco'].replace(",", "."))
        novo_subtotal += auxiliar
    }

    subtotal.textContent = brl.format(novo_subtotal)

    if (novo_subtotal >= 250) {
        frete = 0
    }

    if (novo_subtotal === 0) {
        frete = 0
    }
    novo_total = frete + novo_subtotal

    total.textContent = brl.format(novo_total)
}

// Gerencia tudo em 1 só agora !
function controlar_qtd() {

    const itens_carrinho = document.querySelector(".carrinho-itens")

    itens_carrinho.addEventListener('click', (e) => {
        const botoes = e.target.closest(".diminuir, .aumentar")

        if (!botoes) return;

        e.preventDefault()

        const item_qtd = botoes.closest(".item-qtd")
        const quantidade = item_qtd.querySelector(".qtd")
        const atual = parseInt(quantidade.textContent)

        const id = item_qtd.dataset.id_item;

        // Alterando a quantidade no localstorage
        const lista = dadosLocal("produtos");

        if (botoes.classList.contains("aumentar")) {
            quantidade.textContent = atual + 1

        } else if (atual > 1) {
            quantidade.textContent = atual - 1
        }

        // Aqui é analisando se foi encontrando o item no carrinho.
        const produto = lista.find(p => String(p.id) === String(id));

        if (produto) {
            produto.qtd = Number(quantidade.textContent)

            mani_dadosLocal('produtos', lista)
        }

        calcular_carrinho()
    })
}

function remover_item_carrinho() {
    const itens_carrinho = document.querySelector(".carrinho-itens")

    itens_carrinho.addEventListener('click', (e) => {
        const remover = e.target.closest(".item-remover")
        if (!remover) return

        e.preventDefault()

        const info = remover.closest(".item-info")
        const titulo = info.querySelector(".item-titulo")

        confirmar = confirm("Certeza que quer remover: " + titulo.textContent)

        if (confirmar) {
            const id = document.querySelector(".item-qtd").dataset.id_item
            const dados = dadosLocal("produtos")
            const atualizar = dados.filter(item => item.id !== id)

            mani_dadosLocal("produtos", atualizar)

        }
        calcular_carrinho()
        lista_item_carrinho()

    }) // Fim eventclick
}

function limpar_carrinho(){
    const checkout = document.querySelector(".checkout")
    checkout.addEventListener('click', (e) => {
        e.preventDefault()
        dados = dadosLocal("produtos")
        
        if(dados.length > 0){
           check = confirm("Certeza que deseja remover todos os itens?")
        
            if (check){
                localStorage.clear()

                window.location.href = "/carrinho"
            }
        }

    })

}

//Funções antigas de controle de quantidade
function diminuir_qtd() {


    const itens_carrinho = document.querySelector(".carrinho-itens")

    itens_carrinho.addEventListener('click', (e) => {
        const diminuir = e.target.closest(".diminuir")
        if (!diminuir) return

        e.preventDefault();

        const item_qtd = diminuir.closest(".item-qtd");
        const qtd = item_qtd.querySelector(".qtd")
        const atual = parseInt(qtd.textContent)

        if (atual == 1) return

        qtd.textContent = atual - 1

    })


}

function aumentar_qtd() {


    const itens_carrinho = document.querySelector(".carrinho-itens")

    itens_carrinho.addEventListener('click', (e) => {
        const aumentar = e.target.closest(".aumentar")


        if (!aumentar) return

        e.preventDefault();

        const item_qtd = aumentar.closest(".item-qtd");
        const qtd = item_qtd.querySelector(".qtd")
        const atual = parseInt(qtd.textContent)


        qtd.textContent = atual + 1

    })


}

// Verificar para criar um Preview com JS
function imagem_prod() {
    const arq = document.querySelector("#img-produto")


    arq.addEventListener("change", (event) => {
        const img_pre = arq.files[0]
        const nova_img = document.querySelector("#preview")
        nova_img.setAttribute('src', URL.createObjectURL(img_pre))

    })

}

//Tratando o form e enviando ao back
function inserir_prod() {
    const nv_prod_f = document.querySelector('[name="produto-f"]')
    const alerta = document.querySelector('.alerta')


    nv_prod_f.addEventListener("submit", (event) => {
        event.preventDefault();

        // Como vamos trabalhar com arquivos podemos trabalhar com FormData
        dados = new FormData(nv_prod_f);

        fetch("/inserir/novo-produto", {
            method: 'POST',
            body: dados,
        }).then(response => response.json())
            .then(data => {
                if (data.status == "erro") {
                    alerta.innerHTML = data.mensagem
                    alerta.classList.add("visivel")
                    alerta.classList.add("erro")
                } else {
                    alerta.innerHTML = data.mensagem
                    alerta.classList.add("visivel")
                    alerta.classList.add("sucesso")
                    // Limpando os campos
                    document.querySelector("#codProduto").value = "";
                    document.querySelector("#item").value = "";
                    document.querySelector("#departamento").value = "";
                    document.querySelector("#preco").value = "";
                    document.querySelector("#preview").setAttribute('src', imgPreview);
                    document.querySelector("#img-produto").value = "";


                }
            })

    })

}

function alterar_prod() {
    const form_alt = document.querySelector('[name="alterar-f"]')
    const alerta = document.querySelector(".alerta")

    form_alt.addEventListener("submit", (e) => {
        e.preventDefault();

        dados = new FormData(form_alt);

        fetch(`/alterar/produto/${id}`, {
            method: 'UPDATE',
            body: dados
        }).then(response => response.json())
            .then(data => {
                if (data.status == "erro") {
                    alerta.innerHTML = data.mensagem
                    alerta.classList.add("visivel")
                    alerta.classList.add("erro")
                } else {
                    alerta.innerHTML = data.mensagem
                    alerta.classList.add("visivel")
                    alerta.classList.add("sucesso")
                }

            })

    })
}

function deletar_prod() {
    // Adicionar o evento no objeto que tem todos os elementos sobre ele e assim procurar o "alvo", e realizar a operação necessária
    const tabela = document.querySelector("table")
    tabela.addEventListener('click', async (e) => {
        const deletar = e.target.closest(".deletar") // aqui é nosso alvo dentro da tabela quero que somente quando clicar no botão deletar recupere o id e nome do item

        if (!deletar) return; // se for diferente do "alvo", não faz nada !

        e.preventDefault();

        // Confirmando que o usuário realmente queira deletar pois ele pode clicar por engano.
        confirma = confirm("Deletar " + deletar.dataset.item + " ?")

        if (confirma) {
            const res = await fetch(`/deletar/produto/${deletar.dataset.id_item}`, { method: "DELETE" })
            if (res.ok) {
                alert(`Produto: ${deletar.dataset.item} removido com sucesso!`)
                const qtd = document.querySelector(".produtos-c")
                const atual = parseInt(qtd.textContent)
                qtd.textContent = `${atual - 1} Produto(s)`
                deletar.closest("tr").remove();
            } else {
                alert(res.mensagem);
            }
        }
    })
}

// Enviar para o banco de dados o pedido.
function enviar_pedido() {
    const btn_finalizar = document.querySelector(".btn-submit")

    btn_finalizar.addEventListener('click', (e) => {
        e.preventDefault();

        let storage = dadosLocal("produtos")

        if (storage.length >= 1) {

            const itens = storage.map(({ id, qtd }) => ({ id, qtd })) // Criando uma lista somente com os id's e quantidade

            let dados = {
                nome: document.querySelector("#nome").value,
                endereco: document.querySelector("#endereco").value,
                celular: document.querySelector("#celular").value,
                tipo_pag: document.querySelector("#pagamento").value,
                itens: itens // aqui é inserido o array dos itens que estão no carrinho para criar o pedido
            }

            if (dados['celular'].length < 15) {
                alert("Celular invalido!")
                return
            }

            fetch("/inserir/pedido", {
                method: "POST",
                headers: { "Content-Type": "Application/json" },
                body: JSON.stringify(dados)
            }).then(response => response.json())
                .then(data => {
                    if (data.status == "sucesso") {
                        alert(data.mensagem)
                        document.querySelector("#nome").value = "";
                        document.querySelector("#endereco").value = "";
                        document.querySelector("#celular").value = "";
                        document.querySelector("#pagamento").value = "";

                        localStorage.removeItem("produtos")

                        window.location.href = "/produtos"

                    } else {
                        alert(data.mensagem)
                    }
                })


        } else {
            alert("Pedido não enviado, Carrinho vazio!")
        }
    })
}

// Formantando para padrão monetário brasileiro.
function formatoBRL(valor) {
    const formatado = valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
    return formatado
}

// Função de Login parte administrativa
function login() {
    logar.addEventListener('click', (event) => {
        event.preventDefault();

        // console.log("btn logar clicado !")

        const usuario = document.querySelector("#usuario");
        const senha = document.querySelector("#senha");

        dados_login = {
            usuario: usuario.value,
            senha: senha.value
        }
        // console.log(dados_login)

        fetch("/validar/login", {
            method: 'POST',
            headers: { 'Content-Type': 'Application/json' },
            body: JSON.stringify(dados_login)

        }).then(response => response.json())
            .then(data => {
                // console.log(data)
                if (data.mensagem == 'Autorizado') {
                    alert(data.mensagem)
                    window.location.href = "/admin/painel-produtos"
                }
                else {
                    alert(data.mensagem)
                }
            })
    })
}

//api
async function aviso(response){
    const dados = await response.json()
    const resposta = document.querySelector(".resposta")
    
    if(dados.status == "sucesso"){
                
        resposta.classList.remove("erro")
        resposta.classList.remove("visivel")
        resposta.classList.add("sucesso")
        resposta.classList.add("visivel")
        resposta.textContent = dados.mensagem

    }else{

        resposta.classList.remove("sucesso")
        resposta.classList.remove("visivel")
        resposta.classList.add("erro")
        resposta.classList.add("visivel")
        resposta.textContent = dados.mensagem
    }
}

function verificar_conexao(){
    const verificar = document.querySelector(".verificar")
    let retorno = null;

    verificar.addEventListener("click", async (e) => {
        e.preventDefault()

        const res = await fetch("/API/verificar/conexao")
        retorno = res
        aviso(res)
    })

    return retorno
}

function gerar_qr(){
    const qr = document.querySelector(".conectar-qr")
    const resposta = document.querySelector(".resposta")

    qr.addEventListener("click", async (e) => {
        e.preventDefault()
        const img = document.querySelector("#montarqr")
        const res = await fetch("/API/conectar/qr")
        const dados = await res.json()

        if (dados.status == "sucesso"){
            
            img.removeAttribute("hidden")
            img.src = "data:image/png;base64," + dados.mensagem
            resposta.textContent = "Escaneie o QRcode com o WhatsApp"

        }else {
            resposta.classList.remove("sucesso")
            resposta.classList.remove("visivel")
            resposta.classList.add("erro")
            resposta.classList.add("visivel")
            resposta.textContent = dados.mensagem
            img.setAttribute("hidden")
        }

    })
}

function reconectar(){
    
    const resposta = document.querySelector(".resposta")
    const reconectar = document.querySelector(".reconectar")
    

    reconectar.addEventListener("click", async (e) => {
        e.preventDefault()
        const verificar = await fetch("/API/verificar/conexao")

        if(verificar.status == 409){
            resposta.classList.remove("sucesso")
            resposta.classList.remove("visivel")
            resposta.classList.add("erro")
            resposta.classList.add("visivel")            
            resposta.textContent = "Não foi possivel reconectar!"    
        }else{
            const response = await fetch("/API/reconectar")
            const dados = await response.json()

            if(dados.status == "sucesso"){
                
                resposta.classList.remove("erro")
                resposta.classList.remove("visivel")
                resposta.classList.add("sucesso")
                resposta.classList.add("visivel")
                resposta.textContent = dados.mensagem
            }else{

                resposta.classList.remove("sucesso")
                resposta.classList.remove("visivel")
                resposta.classList.add("erro")
                resposta.classList.add("visivel")
                resposta.textContent = dados.mensagem
            }
        }
    })

    
}

function desconectar(){
    const desconectar = document.querySelector(".desconectar")

    desconectar.addEventListener("click", async (e) => {
        e.preventDefault()

        const response = await fetch("/API/desconectar")
        const dados = await response.json()
        const resposta = document.querySelector(".resposta")
        
        if(dados.status == "sucesso"){
            resposta.classList.remove("erro")
            resposta.classList.remove("visivel")
            resposta.classList.add("sucesso")
            resposta.classList.add("visivel")
            resposta.textContent = dados.mensagem
        }else{
            resposta.classList.remove("sucesso")
            resposta.classList.remove("visivel")
            resposta.classList.add("erro")
            resposta.classList.add("visivel")
            resposta.textContent = dados.mensagem
        }
    })
}

if (page == 'inserir_produto') {
    imagem_prod();
    inserir_prod();
    validar_cod();
}

if (page == 'editar') {
    imagem_prod();
    alterar_prod();
    validar_cod();
}

if (page == 'admin-produtos') {
    deletar_prod();
}

if (page == 'produtos') {
    adiciona_item_carrinho()
    
    // Adicionando o evento change no select e passando a função filtrar
    document.querySelector("select[name='categoria-s']").addEventListener("change", filtrar)
    
    // Adicionando o evento input e passando a função filtar porém com um timer para não ficar enviando toda hora que digitar.
    let timer
    document.querySelector("input[name='pesquisa']").addEventListener("input", () => {
        clearTimeout(timer)
        timer = setTimeout(filtrar, 300)
    })

    const carrinho = dadosLocal('produtos');
    if (carrinho.length > 0) {
        carrinho_b.textContent = carrinho.length
    }

}

if (page == 'exibir-carrinho') {
    lista_item_carrinho()
    controlar_qtd()
    calcular_carrinho()
    enviar_pedido()
    mascara_celular()
    remover_item_carrinho()
    limpar_carrinho()

}

if (page == "WhatsApp"){
    reconectar()
    let verifica = verificar_conexao()
    desconectar()
    gerar_qr()
    


}

if (titulo == 'Mercado da Ju') {
    corpo.classList.add("bg-p")
} else if (titulo == 'Mercado da Ju | Login') {
    login();
}