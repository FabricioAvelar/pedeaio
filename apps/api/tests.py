import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.pedidos.models import Pedido, ItemPedido
from apps.produtos.models import Categoria, Produto, Carrinho, ItemCarrinho
from apps.usuarios.models import Usuario, Endereco


class UsuariosApiTests(APITestCase):
    def setUp(self):
        self.dados = {
            'first_name': 'Maria',
            'last_name': 'Silva',
            'email': 'maria@exemplo.com',
            'cpf': '12345678901',
            'nascimento': '2000-05-20',
            'password': 'Senha@12345',
            'password2': 'Senha@12345',
        }

    def cadastrar(self, **mudancas):
        dados = {**self.dados, **mudancas}
        return self.client.post(reverse('api_cadastro'), dados, format='json')

    def login(self):
        return self.client.post(
            reverse('api_token'),
            {'username': 'maria@exemplo.com', 'password': 'Senha@12345'},
            format='json',
        )

    def autenticar(self):
        r = self.cadastrar()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")

    # Cadastro
    def test_cadastro_cria_usuario_e_devolve_tokens(self):
        r = self.cadastrar()
        self.assertEqual(r.status_code, 201)
        self.assertIn('access', r.data)
        self.assertIn('refresh', r.data)
        self.assertNotIn('password', r.data['usuario'])

        u = Usuario.objects.get(pk='12345678901')
        self.assertEqual(u.username, 'maria@exemplo.com')
        self.assertTrue(u.check_password('Senha@12345'))

    def test_cadastro_rejeita_cpf_com_pontuacao(self):
        r = self.cadastrar(cpf='123.456.789-01')
        self.assertEqual(r.status_code, 400)
        self.assertIn('cpf', r.data)

    def test_cadastro_rejeita_email_duplicado(self):
        self.cadastrar()
        r = self.cadastrar(cpf='98765432100')
        self.assertEqual(r.status_code, 400)
        self.assertIn('email', r.data)

    def test_cadastro_rejeita_cpf_duplicado(self):
        self.cadastrar()
        r = self.cadastrar(email='outra@exemplo.com')
        self.assertEqual(r.status_code, 400)
        self.assertIn('cpf', r.data)

    def test_cadastro_rejeita_senhas_diferentes(self):
        r = self.cadastrar(password2='Outra@12345')
        self.assertEqual(r.status_code, 400)
        self.assertIn('password2', r.data)

    # Login e logout
    def test_login_retorna_tokens(self):
        self.cadastrar()
        r = self.login()
        self.assertEqual(r.status_code, 200)
        self.assertIn('access', r.data)
        self.assertIn('refresh', r.data)

    def test_login_com_senha_errada(self):
        self.cadastrar()
        r = self.client.post(
            reverse('api_token'),
            {'username': 'maria@exemplo.com', 'password': 'errada'},
            format='json',
        )
        self.assertEqual(r.status_code, 401)

    def test_blacklist_invalida_refresh(self):
        self.cadastrar()
        refresh = self.login().data['refresh']

        r = self.client.post(reverse('api_token_blacklist'), {'refresh': refresh}, format='json')
        self.assertEqual(r.status_code, 200)

        r = self.client.post(reverse('api_token_refresh'), {'refresh': refresh}, format='json')
        self.assertEqual(r.status_code, 401)

    # Perfil (eu)
    def test_eu_exige_autenticacao(self):
        r = self.client.get(reverse('api_eu'))
        self.assertEqual(r.status_code, 401)

    def test_eu_get(self):
        self.autenticar()
        r = self.client.get(reverse('api_eu'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['cpf'], '12345678901')

    def test_eu_put_atualiza_nome_e_ignora_campos_protegidos(self):
        self.autenticar()
        r = self.client.put(
            reverse('api_eu'),
            {
                'first_name': 'Mariana',
                'last_name': 'Souza',
                'nascimento': '2000-05-21',
                'email': 'troca@exemplo.com',
                'is_staff': True,
            },
            format='json',
        )
        self.assertEqual(r.status_code, 200)

        u = Usuario.objects.get(pk='12345678901')
        self.assertEqual(u.first_name, 'Mariana')
        self.assertEqual(u.email, 'maria@exemplo.com')
        self.assertFalse(u.is_staff)

    def test_eu_patch_parcial(self):
        self.autenticar()
        r = self.client.patch(reverse('api_eu'), {'first_name': 'Mari'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Usuario.objects.get(pk='12345678901').first_name, 'Mari')


class EnderecosApiTests(APITestCase):
    def setUp(self):
        self.maria = Usuario.objects.create_user(
            username='maria@exemplo.com', email='maria@exemplo.com',
            password='Senha@12345', cpf='12345678901', nascimento='2000-05-20',
        )
        self.joao = Usuario.objects.create_user(
            username='joao@exemplo.com', email='joao@exemplo.com',
            password='Senha@12345', cpf='98765432100', nascimento='1999-01-10',
        )
        self.dados = {'rua': 'Rua das Flores', 'numero': '10', 'cidade': 'Ceará-Mirim', 'estado': 'rn'}
        self.client.force_authenticate(self.maria)

    def test_exige_autenticacao(self):
        self.client.force_authenticate(None)
        r = self.client.get(reverse('api_enderecos'))
        self.assertEqual(r.status_code, 401)

    def test_cria_endereco_para_o_usuario_logado(self):
        r = self.client.post(reverse('api_enderecos'), self.dados, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['estado'], 'RN')
        self.assertEqual(Endereco.objects.get(id=r.data['id']).usuario, self.maria)

    def test_rejeita_estado_invalido(self):
        r = self.client.post(reverse('api_enderecos'), {**self.dados, 'estado': 'Rio'}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('estado', r.data)

    def test_lista_somente_os_proprios(self):
        Endereco.objects.create(usuario=self.maria, **{**self.dados, 'estado': 'RN'})
        Endereco.objects.create(usuario=self.joao, **{**self.dados, 'estado': 'RN'})
        r = self.client.get(reverse('api_enderecos'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)

    def test_atualiza_endereco(self):
        e = Endereco.objects.create(usuario=self.maria, **{**self.dados, 'estado': 'RN'})
        r = self.client.put(
            reverse('api_endereco_atualizar', args=[e.id]),
            {**self.dados, 'numero': '99'}, format='json',
        )
        self.assertEqual(r.status_code, 200)
        e.refresh_from_db()
        self.assertEqual(e.numero, '99')

    def test_nao_mexe_no_endereco_de_outro_usuario(self):
        e = Endereco.objects.create(usuario=self.joao, **{**self.dados, 'estado': 'RN'})
        r = self.client.put(reverse('api_endereco_atualizar', args=[e.id]), self.dados, format='json')
        self.assertEqual(r.status_code, 404)
        r = self.client.delete(reverse('api_endereco_deletar', args=[e.id]))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(Endereco.objects.filter(id=e.id).exists())

    def test_deleta_endereco(self):
        e = Endereco.objects.create(usuario=self.maria, **{**self.dados, 'estado': 'RN'})
        r = self.client.delete(reverse('api_endereco_deletar', args=[e.id]))
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Endereco.objects.filter(id=e.id).exists())

    def test_endereco_com_pedido_nao_pode_ser_deletado(self):
        e = Endereco.objects.create(usuario=self.maria, **{**self.dados, 'estado': 'RN'})
        Pedido.objects.create(usuario=self.maria, endereco=e, valor_total=10)
        r = self.client.delete(reverse('api_endereco_deletar', args=[e.id]))
        self.assertEqual(r.status_code, 409)
        self.assertTrue(Endereco.objects.filter(id=e.id).exists())


GIF_1X1 = (
    b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00'
    b'\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
)
MEDIA_TESTE = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_TESTE)
class ProdutosApiTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TESTE, ignore_errors=True)

    def setUp(self):
        self.staff = Usuario.objects.create_user(
            username='dono@exemplo.com', email='dono@exemplo.com', password='Senha@12345',
            cpf='11111111111', nascimento='1990-01-01', is_staff=True,
        )
        self.cliente = Usuario.objects.create_user(
            username='cli@exemplo.com', email='cli@exemplo.com', password='Senha@12345',
            cpf='22222222222', nascimento='1995-01-01',
        )
        self.lanches = Categoria.objects.create(nome='Lanches')
        self.bebidas = Categoria.objects.create(nome='Bebidas')
        self.x_burger = Produto.objects.create(
            nome='X-Burger', descricao='Pão e carne', preco='18.50',
            categoria=self.lanches, imagem='produtos/x.jpg',
        )
        self.suco = Produto.objects.create(
            nome='Suco de caju', descricao='Natural', preco='7.00',
            categoria=self.bebidas, imagem='produtos/s.jpg',
        )

    def dados_produto(self, **mudancas):
        dados = {
            'nome': 'Pastel', 'descricao': 'De queijo', 'preco': '6.00',
            'categoria': self.lanches.id,
            'imagem': SimpleUploadedFile('p.gif', GIF_1X1, content_type='image/gif'),
        }
        dados.update(mudancas)
        return dados

    # Categorias
    def test_lista_categorias_e_publica(self):
        r = self.client.get(reverse('api_categorias'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual([c['nome'] for c in r.data], ['Bebidas', 'Lanches'])

    def test_criar_categoria_exige_staff(self):
        url = reverse('api_categorias')
        self.assertEqual(self.client.post(url, {'nome': 'Doces'}, format='json').status_code, 401)

        self.client.force_authenticate(self.cliente)
        self.assertEqual(self.client.post(url, {'nome': 'Doces'}, format='json').status_code, 403)

        self.client.force_authenticate(self.staff)
        r = self.client.post(url, {'nome': 'Doces'}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertTrue(Categoria.objects.filter(nome='Doces').exists())

    def test_atualiza_categoria(self):
        self.client.force_authenticate(self.staff)
        r = self.client.put(
            reverse('api_categoria_atualizar', args=[self.lanches.id]),
            {'nome': 'Salgados'}, format='json',
        )
        self.assertEqual(r.status_code, 200)
        self.lanches.refresh_from_db()
        self.assertEqual(self.lanches.nome, 'Salgados')

    def test_deleta_categoria_vazia(self):
        vazia = Categoria.objects.create(nome='Vazia')
        self.client.force_authenticate(self.staff)
        r = self.client.delete(reverse('api_categoria_deletar', args=[vazia.id]))
        self.assertEqual(r.status_code, 204)

    def test_categoria_com_produtos_nao_pode_ser_deletada(self):
        self.client.force_authenticate(self.staff)
        r = self.client.delete(reverse('api_categoria_deletar', args=[self.lanches.id]))
        self.assertEqual(r.status_code, 409)
        self.assertTrue(Categoria.objects.filter(id=self.lanches.id).exists())

    # Produtos
    def test_lista_produtos_e_publica(self):
        r = self.client.get(reverse('api_produtos'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 2)
        self.assertEqual(r.data[0]['categoria_nome'], 'Bebidas')

    def test_filtra_por_busca_e_categoria(self):
        url = reverse('api_produtos')
        r = self.client.get(url, {'buscar': 'burger'})
        self.assertEqual([p['nome'] for p in r.data], ['X-Burger'])

        r = self.client.get(url, {'categoria': self.bebidas.id})
        self.assertEqual([p['nome'] for p in r.data], ['Suco de caju'])

        r = self.client.get(url, {'categoria': 'abc'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 2)

    def test_detalhes_do_produto(self):
        r = self.client.get(reverse('api_produto_detalhes', args=[self.x_burger.id]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['nome'], 'X-Burger')
        self.assertEqual(self.client.get(reverse('api_produto_detalhes', args=[9999])).status_code, 404)

    def test_criar_produto_exige_staff(self):
        url = reverse('api_produtos')
        self.assertEqual(self.client.post(url, self.dados_produto(), format='multipart').status_code, 401)

        self.client.force_authenticate(self.cliente)
        self.assertEqual(self.client.post(url, self.dados_produto(), format='multipart').status_code, 403)

    def test_staff_cria_produto_com_imagem(self):
        self.client.force_authenticate(self.staff)
        r = self.client.post(reverse('api_produtos'), self.dados_produto(), format='multipart')
        self.assertEqual(r.status_code, 201)
        self.assertIn('/media/produtos/', r.data['imagem'])
        self.assertTrue(Produto.objects.filter(nome='Pastel').exists())

    def test_rejeita_preco_invalido(self):
        self.client.force_authenticate(self.staff)
        r = self.client.post(reverse('api_produtos'), self.dados_produto(preco='0'), format='multipart')
        self.assertEqual(r.status_code, 400)
        self.assertIn('preco', r.data)

    def test_patch_atualiza_so_o_preco(self):
        self.client.force_authenticate(self.staff)
        r = self.client.patch(
            reverse('api_produto_atualizar', args=[self.x_burger.id]),
            {'preco': '20.00'}, format='json',
        )
        self.assertEqual(r.status_code, 200)
        self.x_burger.refresh_from_db()
        self.assertEqual(str(self.x_burger.preco), '20.00')
        self.assertEqual(self.x_burger.nome, 'X-Burger')

    def test_cliente_nao_atualiza_nem_deleta_produto(self):
        self.client.force_authenticate(self.cliente)
        r = self.client.patch(
            reverse('api_produto_atualizar', args=[self.x_burger.id]),
            {'preco': '1.00'}, format='json',
        )
        self.assertEqual(r.status_code, 403)
        r = self.client.delete(reverse('api_produto_deletar', args=[self.x_burger.id]))
        self.assertEqual(r.status_code, 403)

    def test_deleta_produto(self):
        self.client.force_authenticate(self.staff)
        r = self.client.delete(reverse('api_produto_deletar', args=[self.suco.id]))
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Produto.objects.filter(id=self.suco.id).exists())

    def test_produto_em_pedido_nao_pode_ser_deletado(self):
        endereco = Endereco.objects.create(
            usuario=self.cliente, rua='Rua A', numero='1', cidade='Ceará-Mirim', estado='RN',
        )
        pedido = Pedido.objects.create(usuario=self.cliente, endereco=endereco, valor_total=18.5)
        ItemPedido.objects.create(
            pedido=pedido, produto=self.x_burger, quantidade=1, preco_unitario='18.50',
        )
        self.client.force_authenticate(self.staff)
        r = self.client.delete(reverse('api_produto_deletar', args=[self.x_burger.id]))
        self.assertEqual(r.status_code, 409)
        self.assertTrue(Produto.objects.filter(id=self.x_burger.id).exists())


class CarrinhoApiTests(APITestCase):
    def setUp(self):
        self.maria = Usuario.objects.create_user(
            username='maria@exemplo.com', email='maria@exemplo.com', password='Senha@12345',
            cpf='12345678901', nascimento='2000-05-20',
        )
        self.joao = Usuario.objects.create_user(
            username='joao@exemplo.com', email='joao@exemplo.com', password='Senha@12345',
            cpf='98765432100', nascimento='1999-01-10',
        )
        categoria = Categoria.objects.create(nome='Lanches')
        self.x_burger = Produto.objects.create(
            nome='X-Burger', descricao='Pão e carne', preco='18.50',
            categoria=categoria, imagem='produtos/x.jpg',
        )
        self.suco = Produto.objects.create(
            nome='Suco de caju', descricao='Natural', preco='7.00',
            categoria=categoria, imagem='produtos/s.jpg',
        )
        self.client.force_authenticate(self.maria)

    def adicionar(self, produto):
        return self.client.post(reverse('api_carrinho_adicionar', args=[produto.id]))

    def test_exige_autenticacao(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(reverse('api_carrinho')).status_code, 401)
        self.assertEqual(self.adicionar(self.x_burger).status_code, 401)

    def test_carrinho_vazio(self):
        r = self.client.get(reverse('api_carrinho'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['itens'], [])
        self.assertEqual(r.data['total'], '0.00')
        self.assertEqual(r.data['quantidade_itens'], 0)

    def test_adicionar_cria_item_e_repetir_soma_quantidade(self):
        r = self.adicionar(self.x_burger)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['quantidade_itens'], 1)
        self.assertEqual(r.data['itens'][0]['quantidade'], 1)

        r = self.adicionar(self.x_burger)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['quantidade_itens'], 1)
        self.assertEqual(r.data['itens'][0]['quantidade'], 2)

    def test_adicionar_produto_inexistente(self):
        r = self.client.post(reverse('api_carrinho_adicionar', args=[9999]))
        self.assertEqual(r.status_code, 404)

    def test_total_e_subtotal(self):
        self.adicionar(self.x_burger)
        self.adicionar(self.x_burger)
        r = self.adicionar(self.suco)
        self.assertEqual(r.data['total'], '44.00')
        self.assertEqual(r.data['quantidade_itens'], 2)
        self.assertEqual(r.data['itens'][0]['subtotal'], '37.00')

    def test_aumentar_e_diminuir(self):
        item_id = self.adicionar(self.x_burger).data['itens'][0]['id']

        r = self.client.post(reverse('api_carrinho_aumentar', args=[item_id]))
        self.assertEqual(r.data['itens'][0]['quantidade'], 2)

        r = self.client.post(reverse('api_carrinho_diminuir', args=[item_id]))
        self.assertEqual(r.data['itens'][0]['quantidade'], 1)

    def test_diminuir_com_quantidade_um_remove_o_item(self):
        item_id = self.adicionar(self.x_burger).data['itens'][0]['id']
        r = self.client.post(reverse('api_carrinho_diminuir', args=[item_id]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['itens'], [])

    def test_remover_item(self):
        item_id = self.adicionar(self.x_burger).data['itens'][0]['id']
        self.adicionar(self.suco)
        r = self.client.delete(reverse('api_carrinho_remover', args=[item_id]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual([i['produto']['nome'] for i in r.data['itens']], ['Suco de caju'])

    def test_carrinho_e_por_usuario(self):
        self.adicionar(self.x_burger)
        self.client.force_authenticate(self.joao)
        r = self.client.get(reverse('api_carrinho'))
        self.assertEqual(r.data['itens'], [])

    def test_nao_mexe_no_item_de_outro_usuario(self):
        item_id = self.adicionar(self.x_burger).data['itens'][0]['id']
        self.client.force_authenticate(self.joao)

        for nome, metodo in [
            ('api_carrinho_aumentar', self.client.post),
            ('api_carrinho_diminuir', self.client.post),
            ('api_carrinho_remover', self.client.delete),
        ]:
            r = metodo(reverse(nome, args=[item_id]))
            self.assertEqual(r.status_code, 404, nome)

        self.assertEqual(ItemCarrinho.objects.get(id=item_id).quantidade, 1)