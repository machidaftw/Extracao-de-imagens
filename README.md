# Scraping de Imagens

Documentação rápida do coletor de imagens com Selenium + BeautifulSoup.

## Visão geral

- Abre capítulos de um mangá/webcomic, faz rolagem para carregar imagens (lazy loading), coleta os links e baixa para disco.
- Usa Selenium com ChromeDriverManager para gerenciar o driver do Chrome automaticamente.
- Itera capítulos por meio do botão "Next" (ou h2 com classe `next`) até atingir o limite configurado ou não encontrar próximo.

## Fluxo principal (app.py)

1. `processo_completo(url_inicial, pasta_base, total_capitulos)`: controla capítulos, cria subpastas `capitulo_N`, chama `baixa_imagens` e navega para o próximo capítulo via XPath do botão.
2. `baixa_imagens(url, pasta_destino)`: abre a página, rola até o final carregando o conteúdo, extrai `<img>` dentro de `div.py-8`, escolhe `data-src` ou `src`, e salva como `imagem_XXX.jpg` com headers de navegador.
3. `driver` é global: instanciado antes das funções e encerrado no final com `driver.quit()`.

## Pré-requisitos

- Google Chrome instalado.
- Python 3.10+ recomendado.
- Pacotes: `selenium`, `webdriver-manager`, `beautifulsoup4`, `requests`, `lxml`.

## Instalação rápida

```bash
python -m venv venv
source venv/bin/activate
pip install -U pip
pip install selenium webdriver-manager beautifulsoup4 requests lxml
```

## Como executar

O script principal está no final do [app.py](app.py#L1). Ajuste os parâmetros conforme necessário e rode:

```bash
python app.py
```

Parâmetros atuais:

- URL inicial: capítulo 1 de "A Wimp’s Strategy Guide to Conquer the Tower" (exemplo).
- Pasta base: `A Wimp’s Strategy Guide to Conquer the Tower Chapter 1-3`.
- `total_capitulos`: 3.

## Configurações úteis

- Tempo de espera: `time.sleep(3)` antes do scroll e `time.sleep(2)` entre rolagens; ajuste se o site carregar lento/rápido.
- Seleção de imagens: hoje pega `<img>` dentro de `div.py-8`; se o site mudar o container, troque o seletor em `campo_leitura = soup.find('div', class_='py-8')`.
- Próximo capítulo: XPath `//h2[contains(@class, 'next') or contains(text(), 'Next')]` subindo para `ancestor::a`. Adapte para o HTML real se diferente.
- Nomes dos arquivos: `imagem_XXX.jpg`; altere extensão se o site servir PNG/WebP.
- Headers: user-agent definido para evitar 403; personalize em `headers` se precisar.

## Limitações e cuidados

- Driver fica aberto durante todo o loop para evitar re-instanciar; não chame `driver.quit()` dentro de `baixa_imagens`.
- Requer acesso HTTP direto às imagens; se o site bloquear referer/headers adicionais, ajuste as requisições.
- Sites com proteção anti-bot podem exigir delays maiores ou solving de captchas (não incluso).
- O XPath de "Next" pode quebrar se o HTML for diferente; inspecione e ajuste.

## Estrutura de pastas gerada

```
A Wimp’s Strategy Guide to Conquer the Tower Chapter 1-3/
  capitulo_1/
    imagem_000.jpg
    ...
  capitulo_2/
  capitulo_3/
```

## Troubleshooting

- Chrome não abre ou fecha na hora: verifique se o Chrome está instalado e compatível com o ChromeDriver gerenciado pelo webdriver-manager.
- Sem imagens baixadas: valide o seletor do container (`div.py-8`) e se os atributos são `data-src`/`src` com URLs absolutas.
- Botão "Next" não encontrado: inspecione o HTML e ajuste o XPath; se não existir, será necessário construir a próxima URL manualmente.

## Licença

Ver [LICENSE](LICENSE).
