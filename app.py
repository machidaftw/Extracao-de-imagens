import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

# O log_path=os.devnull serve para silenciar mensagens de erro chatas no terminal
service = Service(ChromeDriverManager().install(), log_path=os.devnull)
driver = webdriver.Chrome(service=service)

def baixa_imagens(url, pasta_destino):
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    driver.get(url)
    print("Aguardando carregamento inicial...")
    time.sleep(3) # Tempo para a página carregar a estrutura

    # --- IMPLEMENTAÇÃO DA ROLAGEM (SCROLL) ---
    print("Iniciando rolagem para carregar imagens (Lazy Loading)...")
    
    # Pegamos a altura total da página
    ultima_altura = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Rola até o fim da página atual
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Espera as imagens carregarem (essencial para sites pesados)
        time.sleep(2) 
        
        # Calcula a nova altura e compara com a última
        nova_altura = driver.execute_script("return document.body.scrollHeight")
        if nova_altura == ultima_altura:
            break # Se a altura não mudou, chegamos ao fim
        ultima_altura = nova_altura
    
    print("Rolagem concluída. Analisando HTML...")

    # Agora sim, pegamos o HTML com tudo carregado
    soup = BeautifulSoup(driver.page_source, 'lxml')
    campo_leitura = soup.find('div', class_='py-8')
    imagens = campo_leitura.find_all('img')
    
    print(f"Encontradas {len(imagens)} imagens. Iniciando download...")

    for i, img in enumerate(imagens):
        # Trick para Lazy Loading: tenta 'data-src' primeiro, se não tiver, usa 'src'
        link = img.get('data-src') or img.get('src')
        
        if not link or not link.startswith('http'):
            continue

        try:
            # Identificando-se como navegador para evitar bloqueio 403 (Forbidden)
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
    url_atual = url_inicial
    
    for i in range(total_capitulos):
        nome_pasta = os.path.join(pasta_base, f"capitulo_{i+1}")
        
        # 1. Chama a sua função de baixar imagens (que já criamos)
        # Importante: Remova o driver.quit() de dentro da função baixar_imagens 
        # para o navegador não fechar entre um capítulo e outro.
        baixa_imagens(url_atual, nome_pasta)
        
        # 2. Localiza o link do próximo capítulo
        try:
            # Buscamos um link que contenha a palavra "Next" ou ícones de seta
            # O seletor abaixo é um exemplo comum em 2026 para esses sites
            botao_proximo = driver.find_element(By.XPATH, "//h2[contains(@class, 'next') or contains(text(), 'Next')]")
            url_atual = botao_proximo.find_element(By.XPATH, "./ancestor::a[1]").get_attribute("href")
            print(f"Indo para o próximo capítulo: {url_atual}")
        except Exception:
            print("Fim da linha ou botão próximo não encontrado.")
            break



# Execução
processo_completo('https://asuracomic.net/series/a-wimps-strategy-guide-to-conquer-the-tower-5e2cf669/chapter/1', 'A Wimp’s Strategy Guide to Conquer the Tower Chapter 1-3', total_capitulos=3)
driver.quit()