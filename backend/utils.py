"""
Funções utilitárias para o sistema
"""
import random


def generate_fake_cpf() -> str:
    """
    Gera um CPF válido mas falso (não existe na Receita Federal).
    O CPF gerado passa na validação de dígitos verificadores mas não é um CPF real.
    
    Returns:
        str: CPF formatado (XXX.XXX.XXX-XX)
    """
    # Gerar 9 primeiros dígitos aleatórios
    cpf = [random.randint(0, 9) for _ in range(9)]
    
    # Calcular primeiro dígito verificador
    sum1 = sum(cpf[i] * (10 - i) for i in range(9))
    digit1 = (sum1 * 10) % 11
    if digit1 >= 10:
        digit1 = 0
    cpf.append(digit1)
    
    # Calcular segundo dígito verificador
    sum2 = sum(cpf[i] * (11 - i) for i in range(10))
    digit2 = (sum2 * 10) % 11
    if digit2 >= 10:
        digit2 = 0
    cpf.append(digit2)
    
    # Formatar CPF (XXX.XXX.XXX-XX)
    cpf_str = ''.join(map(str, cpf))
    return f"{cpf_str[:3]}.{cpf_str[3:6]}.{cpf_str[6:9]}-{cpf_str[9:]}"


def format_cpf(cpf: str) -> str:
    """
    Formata CPF removendo caracteres não numéricos e aplicando máscara.
    
    Args:
        cpf: CPF com ou sem formatação
        
    Returns:
        str: CPF formatado (XXX.XXX.XXX-XX)
    """
    # Remove caracteres não numéricos
    cpf_clean = ''.join(filter(str.isdigit, cpf))
    
    # Verifica se tem 11 dígitos
    if len(cpf_clean) != 11:
        return cpf_clean
    
    # Formata
    return f"{cpf_clean[:3]}.{cpf_clean[3:6]}.{cpf_clean[6:9]}-{cpf_clean[9:]}"


def clean_cpf(cpf: str) -> str:
    """
    Remove formatação do CPF, deixando apenas números.
    
    Args:
        cpf: CPF formatado ou não
        
    Returns:
        str: CPF apenas com números
    """
    return ''.join(filter(str.isdigit, cpf))
