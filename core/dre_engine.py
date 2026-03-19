"""
dre_engine.py - Motor de Inteligência Financeira
Responsável pela categorização de contas e cálculo de DRE/DFC
Regras de Negócio:
- 32: CPV Operações (Devs, Suporte, Onboarding)
- 411: ADM Pessoal (Folha de pagamento e benefícios)
- 412: ADM Geral (Despesas gerais e administrativas)
- 413: CPV Comercial (Folha comercial, comissões, marketing)
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DREEngine:
    """
    Motor para processamento de dados financeiros e geração de DRE/DFC
    """
    
    # Mapeamento de prefixos de contas para categorias
    CATEGORIA_MAPPING = {
        "32": "CPV_OPERACOES",
        "411": "ADM_PESSOAL",
        "412": "ADM_GERAL",
        "413": "CPV_COMERCIAL",
    }
    
    # Estrutura do DRE
    DRE_STRUCTURE = [
        ("receita_bruta", "Receita Bruta", "debit"),
        ("deducoes", "(-) Deduções e Impostos", "debit"),
        ("receita_liquida", "= Receita Líquida", "subtotal"),
        ("cpv_comercial", "(-) CPV Comercial (413)", "debit"),
        ("margem_comercial", "= Margem Comercial", "subtotal"),
        ("cpv_operacoes", "(-) CPV Operações (32)", "debit"),
        ("margem_bruta", "= Margem Bruta", "subtotal"),
        ("adm_pessoal", "(-) ADM Pessoal (411)", "debit"),
        ("adm_geral", "(-) ADM Geral (412)", "debit"),
        ("ebitda", "= EBITDA", "subtotal"),
        ("resultado_liquido", "= Resultado Líquido", "subtotal"),
    ]
    
    def __init__(self):
        """Inicializa o motor de DRE"""
        self.dados_processados = {}
    
    @staticmethod
    def extrair_prefixo_conta(codigo_conta: str) -> str:
        """
        Extrai os 2 primeiros dígitos do código da conta
        
        Args:
            codigo_conta (str): Código da conta (ex: "3201", "4110")
        
        Returns:
            str: Prefixo de 2 dígitos (ex: "32", "41")
        """
        if isinstance(codigo_conta, str) and len(codigo_conta) >= 2:
            return codigo_conta[:2]
        return ""
    
    @staticmethod
    def categorizar_conta(codigo_conta: str) -> str:
        """
        Categoriza uma conta baseado no seu prefixo
        
        Args:
            codigo_conta (str): Código da conta
        
        Returns:
            str: Categoria da conta ou "OUTRA" se não mapeada
        """
        prefixo = DREEngine.extrair_prefixo_conta(codigo_conta)
        return DREEngine.CATEGORIA_MAPPING.get(prefixo, "OUTRA")
    
    def processar_lançamentos(self, df_lancamentos: pd.DataFrame, empresa_nome: str = "Consolidado") -> Dict:
        """
        Processa lançamentos financeiros e agrupa por categoria
        
        Args:
            df_lancamentos (pd.DataFrame): DataFrame com os lançamentos (deve ter colunas: 'accountCode', 'value', 'dueDate')
            empresa_nome (str): Nome da empresa para identificação
        
        Returns:
            Dict: Dicionário com os dados processados por categoria
        """
        logger.info(f"Processando lançamentos para {empresa_nome}")
        
        # Validar colunas necessárias
        colunas_necessarias = ['accountCode', 'value', 'dueDate']
        if not all(col in df_lancamentos.columns for col in colunas_necessarias):
            logger.warning(f"Colunas esperadas não encontradas. Colunas disponíveis: {df_lancamentos.columns.tolist()}")
        
        # Adicionar coluna de categoria
        df_lancamentos['categoria'] = df_lancamentos['accountCode'].apply(self.categorizar_conta)
        
        # Agrupar por categoria e somar valores
        resumo_categorias = df_lancamentos.groupby('categoria')['value'].sum().to_dict()
        
        self.dados_processados[empresa_nome] = {
            'df_lancamentos': df_lancamentos,
            'resumo_categorias': resumo_categorias
        }
        
        logger.info(f"✅ Lançamentos processados: {len(df_lancamentos)} registros")
        return resumo_categorias
    
    def gerar_dre(self, empresa_nome: str = "Consolidado", regime: str = "competencia") -> pd.DataFrame:
        """
        Gera o DRE (Demonstração do Resultado do Exercício)
        
        Args:
            empresa_nome (str): Nome da empresa
            regime (str): "competencia" ou "caixa"
        
        Returns:
            pd.DataFrame: DataFrame com o DRE estruturado
        """
        if empresa_nome not in self.dados_processados:
            logger.warning(f"Empresa {empresa_nome} não processada. Retornando DRE vazio.")
            return pd.DataFrame()
        
        resumo = self.dados_processados[empresa_nome]['resumo_categorias']
        
        # Extrair valores por categoria
        receita_bruta = resumo.get('OUTRA', 0)  # Assumir receitas como "OUTRA" ou adicionar categoria específica
        deducoes = 0  # Será preenchido com impostos
        cpv_comercial = resumo.get('CPV_COMERCIAL', 0)
        cpv_operacoes = resumo.get('CPV_OPERACOES', 0)
        adm_pessoal = resumo.get('ADM_PESSOAL', 0)
        adm_geral = resumo.get('ADM_GERAL', 0)
        
        # Calcular subtotais
        receita_liquida = receita_bruta - deducoes
        margem_comercial = receita_liquida - cpv_comercial
        margem_bruta = margem_comercial - cpv_operacoes
        ebitda = margem_bruta - adm_pessoal - adm_geral
        resultado_liquido = ebitda  # Simplificado (sem impostos, juros, etc.)
        
        # Montar estrutura do DRE
        dre_data = []
        for linha_id, linha_nome, linha_tipo in self.DRE_STRUCTURE:
            if linha_tipo == "subtotal":
                valor = locals().get(linha_id, 0)
                dre_data.append({
                    'Linha': linha_nome,
                    'Valor': valor,
                    'Tipo': 'Subtotal'
                })
            elif linha_tipo == "debit":
                valor = locals().get(linha_id, 0)
                dre_data.append({
                    'Linha': linha_nome,
                    'Valor': valor,
                    'Tipo': 'Débito'
                })
        
        df_dre = pd.DataFrame(dre_data)
        logger.info(f"✅ DRE gerado para {empresa_nome}")
        return df_dre
    
    def gerar_dfc(self, df_lancamentos: pd.DataFrame, empresa_nome: str = "Consolidado") -> pd.DataFrame:
        """
        Gera o DFC (Demonstração do Fluxo de Caixa)
        
        Args:
            df_lancamentos (pd.DataFrame): DataFrame com os lançamentos
            empresa_nome (str): Nome da empresa
        
        Returns:
            pd.DataFrame: DataFrame com o DFC estruturado
        """
        logger.info(f"Gerando DFC para {empresa_nome}")
        
        # Agrupar por data e categoria
        df_lancamentos['data'] = pd.to_datetime(df_lancamentos['dueDate'])
        df_lancamentos['categoria'] = df_lancamentos['accountCode'].apply(self.categorizar_conta)
        
        dfc_diario = df_lancamentos.groupby(['data', 'categoria'])['value'].sum().reset_index()
        
        logger.info(f"✅ DFC gerado com {len(dfc_diario)} linhas")
        return dfc_diario
    
    def consolidar_multiplas_empresas(self, dados_empresas: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Consolida dados de múltiplas empresas
        
        Args:
            dados_empresas (Dict): Dicionário com {nome_empresa: df_lancamentos}
        
        Returns:
            pd.DataFrame: DataFrame consolidado
        """
        logger.info(f"Consolidando {len(dados_empresas)} empresas")
        
        dfs_consolidados = []
        for empresa_nome, df_lancamentos in dados_empresas.items():
            df_lancamentos['empresa'] = empresa_nome
            dfs_consolidados.append(df_lancamentos)
        
        if dfs_consolidados:
            df_consolidado = pd.concat(dfs_consolidados, ignore_index=True)
            logger.info(f"✅ Consolidação concluída: {len(df_consolidado)} registros")
            return df_consolidado
        
        return pd.DataFrame()


# Exemplo de uso
if __name__ == "__main__":
    # Criar dados de exemplo
    dados_exemplo = {
        'accountCode': ['3201', '4110', '4120', '4130', '3202'],
        'value': [5000, 2000, 1500, 3000, 4000],
        'dueDate': ['2026-01-15', '2026-01-10', '2026-01-20', '2026-01-25', '2026-01-12']
    }
    df_exemplo = pd.DataFrame(dados_exemplo)
    
    # Processar com DREEngine
    engine = DREEngine()
    resumo = engine.processar_lançamentos(df_exemplo, "Bllog Tecnologia")
    print("\n📊 Resumo por Categoria:")
    print(resumo)
    
    print("\n📈 DRE Gerado:")
    dre = engine.gerar_dre("Bllog Tecnologia")
    print(dre)
    
    print("\n💰 DFC Diário:")
    dfc = engine.gerar_dfc(df_exemplo, "Bllog Tecnologia")
    print(dfc)
