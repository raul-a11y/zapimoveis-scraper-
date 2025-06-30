import pandas as pd
from scraper import scrape_zapimoveis_goiania
import os

def run_scraper_and_save():
    print("Iniciando a raspagem de dados do Zap Imóveis em Goiânia...")
    
    # Define o número de páginas a serem raspadas (ajuste conforme necessidade)
    num_pages_to_scrape = 5 
    df_listings = scrape_zapimoveis_goiania(num_pages=num_pages_to_scrape)

    if not df_listings.empty:
        output_file = 'data/imoveis_goiania.xlsx'
        
        # Cria o diretório 'data' se não existir
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        df_listings.to_excel(output_file, index=False)
        print(f"Dados salvos com sucesso em: {output_file}")
    else:
        print("Nenhum dado foi extraído.")

if __name__ == '__main__':
    run_scraper_and_save()
