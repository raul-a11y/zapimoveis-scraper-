from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Rodar em modo headless (sem interface gráfica)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def extract_listing_details(driver, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))) # Espera um elemento na página

    data = {}
    try:
        data['link'] = url
        data['preco'] = driver.find_element(By.CSS_SELECTOR, '.price__item').text if driver.find_elements(By.CSS_SELECTOR, '.price__item') else 'N/A'
        
        # Tipologia (apartamento já sabemos pelo filtro inicial)
        data['tipologia'] = 'Apartamento'

        # Quartos
        # Pode variar a forma como é exibido, exemplo de seletor CSS
        data['quantidade_quartos'] = driver.find_element(By.XPATH, "//span[contains(text(), 'Quarto')]").text.replace(' quarto', '').replace('s', '') if driver.find_elements(By.XPATH, "//span[contains(text(), 'Quarto')]") else 'N/A'

        # Metragem
        data['metragem'] = driver.find_element(By.XPATH, "//span[contains(text(), 'm²')]").text if driver.find_elements(By.XPATH, "//span[contains(text(), 'm²')]") else 'N/A'
        
        # Endereço (Rua, Número, Bairro) e Nome do Prédio
        # Isso pode ser tricky no Zap Imóveis, pois o endereço não está sempre em um único elemento.
        # Você precisará inspecionar a página para encontrar os seletores exatos.
        # Exemplo de como você PODE encontrar:
        address_element = driver.find_element(By.CSS_SELECTOR, '.address__description') if driver.find_elements(By.CSS_SELECTOR, '.address__description') else None
        if address_element:
            full_address = address_element.text
            # Tentar parsear o endereço completo para rua, número, bairro
            # Isso exigirá alguma lógica de string ou regex.
            # Por simplicidade, vou colocar o endereço completo aqui
            data['rua'] = full_address.split(',')[0].strip() if ',' in full_address else full_address
            data['numero'] = 'N/A' # Muitas vezes o número não é explícito
            data['bairro'] = full_address.split('-')[-1].strip() if '-' in full_address else 'N/A'
        else:
            data['rua'] = 'N/A'
            data['numero'] = 'N/A'
            data['bairro'] = 'N/A'

        data['nome_predio'] = 'N/A' # Raramente o nome do prédio é explícito.
                                    # Pode estar em detalhes adicionais ou título do anúncio.
                                    # Será necessário investigar o HTML.

    except Exception as e:
        print(f"Erro ao extrair detalhes do anúncio {url}: {e}")
        # Retorna N/A para todos os campos em caso de erro
        for key in ['link', 'preco', 'tipologia', 'quantidade_quartos', 'metragem', 'rua', 'numero', 'nome_predio', 'bairro']:
            if key not in data:
                data[key] = 'N/A'
    
    return data

def scrape_zapimoveis_goiania(num_pages=5):
    driver = setup_driver()
    base_url = 'https://www.zapimoveis.com.br/apartamentos/go/goiania/'
    all_listings_data = []

    for page in range(1, num_pages + 1):
        url = f'{base_url}?pagina={page}'
        driver.get(url)
        time.sleep(3) # Espera a página carregar
        
        # Role a página para carregar mais anúncios, se houver lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2) # Espera os novos elementos carregarem

        # Encontre todos os links dos anúncios na página atual
        # O seletor CSS pode precisar ser ajustado conforme o Zap Imóveis atualiza seu layout
        listing_elements = driver.find_elements(By.CSS_SELECTOR, 'a.result-card') 
        
        if not listing_elements:
            print(f"Não foram encontrados anúncios na página {page}. Fim da raspagem.")
            break

        for element in listing_elements:
            listing_url = element.get_attribute('href')
            if listing_url:
                print(f"Extraindo dados de: {listing_url}")
                details = extract_listing_details(driver, listing_url)
                all_listings_data.append(details)
                time.sleep(1) # Pequena pausa entre cada anúncio para evitar bloqueio

    driver.quit()
    return pd.DataFrame(all_listings_data)

if __name__ == '__main__':
    # Exemplo de como usar a função de raspagem
    df = scrape_zapimoveis_goiania(num_pages=2)
    print(df.head())
    df.to_excel('data/imoveis_teste.xlsx', index=False)
