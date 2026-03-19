"""
nibo_api.py - Integração com a API do Nibo
Responsável pela extração de dados de Contas a Pagar e Receber
"""

import requests
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NiboAPI:
    """
    Classe para gerenciar conexões com a API do Nibo
    Endpoints suportados:
    - /empresas/v1/schedules/credit (Contas a Receber)
    - /empresas/v1/schedules/debit (Contas a Pagar)
    """
    
    BASE_URL = "https://api.nibo.com.br/empresas/v1"
    
    def __init__(self, api_token: str):
        """
        Inicializa a conexão com a API do Nibo
        
        Args:
            api_token (str): Token de autenticação da API do Nibo
        """
        self.api_token = api_token
        self.headers = {
            "ApiToken": api_token,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Realiza uma requisição GET à API do Nibo com tratamento de erros
        
        Args:
            endpoint (str): Endpoint da API (ex: 'schedules/credit')
            params (Dict): Parâmetros OData (filter, orderby, skip, top)
        
        Returns:
            Dict: Resposta JSON da API ou None em caso de erro
        """
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao conectar com Nibo API: {e}")
            return None
    
    def get_contas_receber(self, filtro: str = None, pagina: int = 0, tamanho_pagina: int = 500) -> pd.DataFrame:
        """
        Extrai dados de Contas a Receber (Agendamentos de Recebimentos)
        
        Args:
            filtro (str): Filtro OData (ex: "year(dueDate) eq 2026")
            pagina (int): Número da página (0-based)
            tamanho_pagina (int): Quantidade de registros por página (máx 500)
        
        Returns:
            pd.DataFrame: DataFrame com os dados de contas a receber
        """
        params = {
            "$orderby": "dueDate",
            "$skip": pagina * tamanho_pagina,
            "$top": tamanho_pagina
        }
        
        if filtro:
            params["$filter"] = filtro
        
        logger.info(f"Extraindo Contas a Receber - Página {pagina + 1}")
        response = self._make_request("schedules/credit", params)
        
        if response and "value" in response:
            return pd.DataFrame(response["value"])
        return pd.DataFrame()
    
    def get_contas_pagar(self, filtro: str = None, pagina: int = 0, tamanho_pagina: int = 500) -> pd.DataFrame:
        """
        Extrai dados de Contas a Pagar (Agendamentos de Pagamentos)
        
        Args:
            filtro (str): Filtro OData (ex: "year(dueDate) eq 2026")
            pagina (int): Número da página (0-based)
            tamanho_pagina (int): Quantidade de registros por página (máx 500)
        
        Returns:
            pd.DataFrame: DataFrame com os dados de contas a pagar
        """
        params = {
            "$orderby": "dueDate",
            "$skip": pagina * tamanho_pagina,
            "$top": tamanho_pagina
        }
        
        if filtro:
            params["$filter"] = filtro
        
        logger.info(f"Extraindo Contas a Pagar - Página {pagina + 1}")
        response = self._make_request("schedules/debit", params)
        
        if response and "value" in response:
            return pd.DataFrame(response["value"])
        return pd.DataFrame()
    
    def get_all_contas_receber(self, filtro: str = None) -> pd.DataFrame:
        """
        Extrai TODOS os dados de Contas a Receber com paginação automática
        
        Args:
            filtro (str): Filtro OData
        
        Returns:
            pd.DataFrame: DataFrame consolidado com todos os registros
        """
        all_data = []
        pagina = 0
        
        while True:
            df = self.get_contas_receber(filtro=filtro, pagina=pagina)
            if df.empty:
                break
            all_data.append(df)
            pagina += 1
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()
    
    def get_all_contas_pagar(self, filtro: str = None) -> pd.DataFrame:
        """
        Extrai TODOS os dados de Contas a Pagar com paginação automática
        
        Args:
            filtro (str): Filtro OData
        
        Returns:
            pd.DataFrame: DataFrame consolidado com todos os registros
        """
        all_data = []
        pagina = 0
        
        while True:
            df = self.get_contas_pagar(filtro=filtro, pagina=pagina)
            if df.empty:
                break
            all_data.append(df)
            pagina += 1
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()
    
    def testar_conexao(self) -> bool:
        """
        Testa a conexão com a API do Nibo
        
        Returns:
            bool: True se a conexão foi bem-sucedida, False caso contrário
        """
        try:
            response = self._make_request("schedules/credit", {"$top": 1, "$orderby": "dueDate"})
            if response is not None:
                logger.info("✅ Conexão com Nibo API bem-sucedida!")
                return True
            else:
                logger.error("❌ Falha ao conectar com Nibo API")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao testar conexão: {e}")
            return False


# Exemplo de uso
if __name__ == "__main__":
    # Teste com a API Key da Bllog
    api_token = "9164337AD3094A38B40ECD97A26F8B41"
    nibo = NiboAPI(api_token)
    
    # Testar conexão
    if nibo.testar_conexao():
        print("\n📊 Extraindo dados de Contas a Receber...")
        df_receber = nibo.get_all_contas_receber()
        print(f"Total de registros: {len(df_receber)}")
        print(df_receber.head())
        
        print("\n💰 Extraindo dados de Contas a Pagar...")
        df_pagar = nibo.get_all_contas_pagar()
        print(f"Total de registros: {len(df_pagar)}")
        print(df_pagar.head())
