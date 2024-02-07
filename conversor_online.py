import streamlit as st
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

chrome_version ='121.0.6167.160'
chrome_driver_path = ChromeDriverManager().install()

import pandas as pd

import time



st.markdown("<h1 style='text-align: center; color: #00497e;'>Índice de Preços - Banco Central:</h1>", unsafe_allow_html=True)
imagem1 = Image.open("Imgs//bacen.jpg")
largura_desejada = 800
altura_desejada = 449
imagem1_redimensionada = imagem1.resize((largura_desejada, altura_desejada))
st.image(imagem1_redimensionada, caption='', use_column_width=True)

st.markdown("<h1 style='text-align: center; color: #3C8C26;'></h1>", unsafe_allow_html=True)

indices = {
    'IGP-M (FGV)': '28655IGP-M',
    'IGP-DI (FGV)': '00190IGP-DI',
    'INPC (IBGE)': '00188INPC',
    'IPCA (IBGE)': '00433IPCA',
    'IPCA-E (IBGE)': '10764IPC-E',
    'IPC-BRASIL (FGV)': '00191IPC-BRASIL',
    'IPC-SP (FIPE)': '00193IPC-SP'
}

# Escolha do índice pelo usuário
escolha_indice = st.radio("Escolha o índice:", list(indices.keys()))

# Entrada do usuário para Mês e Ano iniciais
inicial = st.text_input("Digite o Mês e Ano iniciais (MMAAA): ")

# Entrada do usuário para Mês e Ano finais
final = st.text_input("Digite o Mês e Ano finais (MMAAA): ")

# Botão para acionar o script Selenium
if st.button("Obter Taxa"):
    # Configuração do Chrome para modo headless
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    #chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-features=NetworkService")
    #chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Configuração do WebDriver usando o ChromeDriverManager
    chrome_driver_path = ChromeDriverManager(chrome_type='googlechrome', version=chrome_version).install()
    driver = webdriver.Chrome(executable_path=chrome_driver_path)
    

    try:
        with st.spinner("Carregando..."):
            
            url = 'https://www3.bcb.gov.br/CALCIDADAO/publico/exibirFormCorrecaoValores.do?method=exibirFormCorrecaoValores'


            driver.get(url) #
            #time.sleep(2)

        # Preenche o campo 'selIndice'
            select_element = driver.find_element("xpath", '//select[@name="selIndice"]')
            select = Select(select_element)
            select.select_by_value(indices[escolha_indice])

                # Preenche os campos 'dataInicial', 'dataFinal' e 'valorCorrecao'
            driver.find_element("name", 'dataInicial').send_keys(f'{inicial}')
            driver.find_element("name", 'dataFinal').send_keys(f'{final}')

                # Clica no botão 'Corrigir valor'
            driver.find_element("class name", 'botao').click()

                # Aguarda um tempo para garantir que a ação seja concluída
            xpath_dinamico = "/html/body/div[6]/table/tbody/tr/td/div[2]/table[1]/tbody/tr[6]/td[2]"

                # Encontrar o elemento usando o XPath
            elemento = driver.find_element(by=By.XPATH, value=xpath_dinamico)

                # Imprimir o texto do elemento
            texto_do_elemento = elemento.text
            st.success(f"Resultado: {texto_do_elemento}")
    except Exception as e:
        st.error(f"Erro ao executar script Selenium: {str(e)}")
    finally:
        if driver:
        # Certifique-se de fechar o navegador ao finalizar
            driver.quit()
        

# Parte do Pandas para processar o CSV
uploaded_file = st.file_uploader("Carregue o arquivo CSV", type=["csv"])
nome_coluna = st.text_input("Digite o nome da coluna:")
valor_ponto_flutuante = st.number_input("Digite o valor do índice de correção no período:")
novo_arquivo_csv = st.text_input("Digite o nome para o novo arquivo CSV:")

# Botão para processar o CSV
if st.button("Processar CSV"):
    if uploaded_file and nome_coluna and novo_arquivo_csv:
        try:
            df = pd.read_csv(uploaded_file, encoding='latin1', delimiter=';')

            if nome_coluna not in df.columns:
                st.error(f"A coluna '{nome_coluna}' não existe no DataFrame.")
            else:
                df[nome_coluna] = pd.to_numeric(df[nome_coluna].replace('[R$]', '', regex=True).str.replace(',', '.'), errors='coerce')
                df[nome_coluna] = df[nome_coluna] * valor_ponto_flutuante
                df[nome_coluna] = df[nome_coluna].round(2)
                df[nome_coluna] = df[nome_coluna].apply(lambda x: f'R${x:,.2f}')
                df.to_csv(novo_arquivo_csv, index=False, decimal=',', sep=";")
                st.success(f"Arquivo {novo_arquivo_csv}.csv gerado com sucesso!")

                # Botão para baixar arquivo
                down1 = st.button("Baixar arquivo")
                if down1:
                    file_path = novo_arquivo_csv
                    with open(file_path, "rb") as file:
                        file_content = file.read()
                        st.download_button(label="Baixar arquivo", data=file_content, file_name=f'{novo_arquivo_csv}.csv', key=None, help=None)
        except Exception as e:
            st.error(f"Erro ao processar CSV: {str(e)}")
    else:
        st.warning("Carregue o arquivo CSV, digite o nome da coluna e o nome para o novo arquivo antes de processar.")
