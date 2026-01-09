"""Coletor de imagens com Selenium + BeautifulSoup.

Abre capítulos de webcomic/mangá, rola para carregar imagens, coleta os links e
baixa para disco. Usa um único driver do Chrome para evitar reinicializações a
cada capítulo.
"""

import os
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install(), log_path=os.devnull)
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(service=service, options=options)

def baixa_imagens(url, pasta_destino):
    """Faz scroll completo na página, coleta e salva imagens.

    Args:
        url: Endereço da página do capítulo.
        pasta_destino: Pasta onde as imagens serão gravadas; cria se não existir.
    """
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    driver.get(url)
    print("Aguardando carregamento inicial...")
    time.sleep(3)
    print("Iniciando rolagem para carregar imagens (Lazy Loading)...")
    ultima_altura = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        nova_altura = driver.execute_script("return document.body.scrollHeight")
        if nova_altura == ultima_altura:
            break
        ultima_altura = nova_altura
    
    print("Rolagem concluída. Analisando HTML...")
    soup = BeautifulSoup(driver.page_source, 'lxml')
    campo_leitura = soup.find('div', class_='py-8')
    imagens = campo_leitura.find_all('img')
    
    print(f"Encontradas {len(imagens)} imagens. Iniciando download...")

    for i, img in enumerate(imagens):
        link = img.get('data-src') or img.get('src')
        
        if not link or not link.startswith('http'):
            continue

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0'}
            resposta = requests.get(link, headers=headers, timeout=15)
            
            if resposta.status_code == 200:
                caminho_arquivo = os.path.join(pasta_destino, f"imagem_{i:03d}.jpg")
                with open(caminho_arquivo, 'wb') as f:
                    f.write(resposta.content)
                print(f"Sucesso: {caminho_arquivo}")
        except Exception as e:
            print(f"Erro ao baixar {link}: {e}")

def processo_completo(url_inicial, pasta_base, total_capitulos=3):
    """Percorre capítulos sequenciais, salvando imagens em subpastas.

    Args:
        url_inicial: Primeiro capítulo a processar.
        pasta_base: Pasta raiz onde cada capítulo será criado.
        total_capitulos: Quantidade máxima de capítulos a baixar.
    """
    url_atual = url_inicial
    
    for i in range(total_capitulos):
        nome_pasta = os.path.join(pasta_base, f"capitulo_{i+1}")
        baixa_imagens(url_atual, nome_pasta)
        try:
            botao_proximo = driver.find_element(By.XPATH, "//h2[contains(@class, 'next') or contains(text(), 'Next')]")
            url_atual = botao_proximo.find_element(By.XPATH, "./ancestor::a[1]").get_attribute("href")
            print(f"Indo para o próximo capítulo: {url_atual}")
        except Exception:
            print("Fim da linha ou botão próximo não encontrado.")
            break



# Execução
processo_completo('https://asuracomic.net/series/a-wimps-strategy-guide-to-conquer-the-tower-5e2cf669/chapter/1', 'A Wimp’s Strategy Guide to Conquer the Tower Chapter 1-3', total_capitulos=3)
driver.quit()