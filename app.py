import streamlit as st
from datetime import datetime, date
import os
import pandas as pd
import requests

Arqui_Prod = 'produtos.txt'
Arqui_Vend = 'vendas.txt'
Arqui_Cliente = 'clientes.txt'

# ---------- PRODUTOS ----------
def carregar_produtos():
    produtos = []
    if os.path.exists(Arqui_Prod):
        with open(Arqui_Prod, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split(';')
                if len(partes) == 3:
                    nome, preco, quantidade = partes
                    try:
                        produtos.append({
                            'nome': nome,
                            'preco': float(preco),
                            'quantidade': int(quantidade)
                        })
                    except ValueError:
                        print(f"Erro de conversão na linha: {linha.strip()}")
    return produtos

def salvar_produtos(produtos):
    with open(Arqui_Prod, 'w', encoding='utf-8') as f:
        for p in produtos:
            linha = f"{p['nome']};{p['preco']};{p['quantidade']}\n"
            f.write(linha)

# ---------- VENDAS ----------
def carregar_vendas():
    vendas = []
    if os.path.exists(Arqui_Vend):
        with open(Arqui_Vend, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split(';')
                if len(partes) == 5:
                    data, nome_produto, quantidade, total, cliente = partes
                    try:
                        vendas.append({
                            'data': data,
                            'produto': nome_produto,
                            'quantidade': int(quantidade),
                            'total': float(total),
                            'cliente': cliente
                        })
                    except ValueError:
                        print(f"Erro de conversão na linha: {linha.strip()}")
    return vendas

def salvar_vendas(vendas):
    with open(Arqui_Vend, 'w', encoding='utf-8') as f:
        for v in vendas:
            linha = f"{v['data']};{v['produto']};{v['quantidade']};{v['total']};{v['cliente']}\n"
            f.write(linha)

# ---------- CLIENTES ----------
def carregar_clientes():
    clientes = []
    if os.path.exists(Arqui_Cliente):
        with open(Arqui_Cliente, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split(';')
                if len(partes) == 6:
                    cpf, nome, data_nasc, cep, endereco, telefone = partes
                    clientes.append({
                        'cpf': cpf,
                        'nome': nome,
                        'data_nasc': data_nasc,
                        'cep': cep,
                        'endereco': endereco,
                        'telefone': telefone
                    })
    return clientes

def salvar_clientes(clientes):
    with open(Arqui_Cliente, 'w', encoding='utf-8') as f:
        for c in clientes:
            linha = f"{c['cpf']};{c['nome']};{c['data_nasc']};{c['cep']};{c['endereco']};{c['telefone']}\n"
            f.write(linha)

def buscar_endereco(cep):
    try:
        url = f"https://brasilapi.com.br/api/cep/v1/{cep}"
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            return f"{dados.get('street', '')}, {dados.get('neighborhood', '')}, {dados.get('city', '')} - {dados.get('state', '')}"
        else:
            return "CEP não encontrado"
    except:
        return "Erro ao consultar o CEP"

# ---------- INTERFACE ----------
st.title("Controle de Estoque Simples")

menu = st.sidebar.radio("Menu", ["Cadastro de Produtos", "Cadastro de Clientes", "Registro de Vendas", "Histórico de Vendas"])

produtos = carregar_produtos()
vendas = carregar_vendas()
clientes = carregar_clientes()

# ----- PRODUTOS -----
if menu == "Cadastro de Produtos":
    st.header("Cadastrar Produto")
    nome = st.text_input("Nome do produto")
    preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f")
    quantidade = st.number_input("Quantidade", min_value=0, step=1, format="%d")

    if st.button("Cadastrar"):
        if nome.strip() == "":
            st.error("Nome não pode estar vazio.")
        elif any(p['nome'].lower() == nome.lower() for p in produtos):
            st.error("Produto já cadastrado! Atualize o estoque em vez de duplicar.")
        else:
            produtos.append({'nome': nome, 'preco': preco, 'quantidade': quantidade})
            salvar_produtos(produtos)
            st.success(f"Produto '{nome}' cadastrado com sucesso!")

    st.subheader("Produtos cadastrados")
    if produtos:
        df_produtos = pd.DataFrame(produtos)
        st.dataframe(df_produtos)
    else:
        st.info("Nenhum produto cadastrado ainda.")

# ----- CLIENTES -----
elif menu == "Cadastro de Clientes":
    st.header("Cadastrar Cliente")
    cpf = st.text_input("CPF")
    nome = st.text_input("Nome completo")
    data_nasc = st.date_input("Data de nascimento", min_value=date(1900,1,1), max_value=date.today())
    cep = st.text_input("CEP")
    endereco = ""
    if cep:
        endereco = buscar_endereco(cep)
        st.text(f"Endereço: {endereco}")
    telefone = st.text_input("Telefone")

    if st.button("Cadastrar Cliente"):
        if any(c['cpf'] == cpf for c in clientes):
            st.error("Cliente já cadastrado!")
        else:
            clientes.append({
                'cpf': cpf,
                'nome': nome,
                'data_nasc': data_nasc.strftime("%d/%m/%Y"),
                'cep': cep,
                'endereco': endereco,
                'telefone': telefone
            })
            salvar_clientes(clientes)
            st.success(f"Cliente '{nome}' cadastrado com sucesso!")

    st.subheader("Clientes cadastrados")
    if clientes:
        df_clientes = pd.DataFrame(clientes)
        st.dataframe(df_clientes)
    else:
        st.info("Nenhum cliente cadastrado ainda.")

# ----- VENDAS -----
elif menu == "Registro de Vendas":
    st.header("Registrar Venda")

    if not produtos:
        st.warning("Nenhum produto cadastrado ainda.")
    elif not clientes:
        st.warning("Nenhum cliente cadastrado ainda.")
    else:
        nomes_prod = [p['nome'] for p in produtos]
        produto_sel = st.selectbox("Produto", nomes_prod)
        quantidade_venda = st.number_input("Quantidade vendida", min_value=1, step=1, format="%d")

        nomes_cli = [f"{c['nome']} - {c['cpf']}" for c in clientes]
        cliente_sel = st.selectbox("Cliente", nomes_cli)

        if st.button("Registrar Venda"):
            for p in produtos:
                if p['nome'] == produto_sel:
                    if quantidade_venda > p['quantidade']:
                        st.error("Estoque insuficiente!")
                    else:
                        p['quantidade'] -= quantidade_venda
                        total = p['preco'] * quantidade_venda
                        venda = {
                            'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                            'produto': p['nome'],
                            'quantidade': quantidade_venda,
                            'total': total,
                            'cliente': cliente_sel
                        }
                        vendas.append(venda)
                        salvar_produtos(produtos)
                        salvar_vendas(vendas)
                        st.success(f"Venda registrada: R${total:.2f}")
                    break

# ----- HISTÓRICO -----
elif menu == "Histórico de Vendas":
    st.header("Histórico de Vendas")
    if not vendas:
        st.info("Nenhuma venda registrada.")
    else:
        df_vendas = pd.DataFrame(vendas)
        st.dataframe(df_vendas)
