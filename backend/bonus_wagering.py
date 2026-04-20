"""Regra de rollover: volume de apostas necessário antes de liberar saques após bônus com rollover."""

from sqlalchemy.orm import Session


def get_global_rollover_multiplier(db: Session) -> float:
    """Multiplicador único (configuração global em FTDSettings). 0 = sem rollover obrigatório."""
    from models import FTDSettings

    s = db.query(FTDSettings).filter(FTDSettings.is_active == True).first()
    if not s:
        return 0.0
    return float(getattr(s, "rollover_multiplier", 0) or 0.0)


def reduce_bonus_wagering_remaining(user, stake: float) -> None:
    """
    Reduz o saldo de rollover pendente pelo valor apostado (stake).
    Chamado após debitar uma aposta válida (seamless / Gold API).
    """
    if stake is None or stake <= 0:
        return
    rem = float(getattr(user, "bonus_wagering_remaining", 0) or 0.0)
    if rem <= 0:
        return
    user.bonus_wagering_remaining = max(0.0, rem - float(stake))


def add_rollover_requirement(user, bonus_amount: float, rollover_multiplier: float) -> None:
    """Incrementa o volume de apostas exigido: bônus * multiplicador."""
    if bonus_amount is None or bonus_amount <= 0:
        return
    m = float(rollover_multiplier or 0.0)
    if m <= 0:
        return
    current = float(getattr(user, "bonus_wagering_remaining", 0) or 0.0)
    user.bonus_wagering_remaining = current + float(bonus_amount) * m
