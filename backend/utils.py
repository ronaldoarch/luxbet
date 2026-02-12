"""
Funções utilitárias para o sistema
"""
import random
from typing import Optional


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


def normalize_phone_for_gatebox(phone: Optional[str]) -> Optional[str]:
    """
    Normaliza telefone para formato E.164 com +55 (Brasil), exigido pela Gatebox.
    Ex.: 11999999999 -> +5511999999999 | 21987654321 -> +5521987654321
    Retorna None apenas se não houver dígitos suficientes para formar um número válido.
    """
    if not phone or not str(phone).strip():
        return None
    digits = "".join(c for c in str(phone) if c.isdigit())
    if not digits:
        return None
    # Brasil: +55 (DDI) + DDD (2) + número (8 ou 9 dígitos)
    # 10 dígitos: DDD + 8 (fixo)
    if len(digits) == 10:
        return f"+55{digits}"
    # 11 dígitos: DDD + 9 (celular)
    if len(digits) == 11:
        return f"+55{digits}"
    # 9 dígitos: apenas número (celular) — assume DDD 11 (SP) para formar +5511XXXXXXXXX
    if len(digits) == 9:
        return f"+5511{digits}"
    # Já vem com 55 na frente (12+ dígitos)
    if len(digits) >= 12 and digits.startswith("55"):
        return f"+{digits}"
    if len(digits) >= 12:
        return f"+{digits}"
    return None


def normalize_pix_key_for_gatebox(key: Optional[str], key_type: Optional[str]) -> str:
    """
    Normaliza a chave PIX conforme o tipo para envio à API Gatebox.
    - phoneNumber: E.164 com +55 (ex.: +5511999999999)
    - document (CPF/CNPJ): apenas dígitos
    - email, randomKey, paymentCode: valor limpo (strip)
    """
    if not key or not str(key).strip():
        return (key or "").strip()
    key = str(key).strip()
    key_type = (key_type or "").strip().lower()
    if key_type == "phonenumber" or key_type == "phone":
        normalized = normalize_phone_for_gatebox(key)
        return normalized if normalized else key
    if key_type == "document":
        return "".join(c for c in key if c.isdigit())
    # email, randomkey, paymentcode: retorna sem espaços extras
    return key
