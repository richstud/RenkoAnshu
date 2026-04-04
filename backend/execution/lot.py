from backend.mt5.connection import AccountSession


def compute_lot_size(balance: float) -> float:
    if balance < 500:
        return 0.01
    if 500 <= balance <= 1000:
        return 0.5
    return 1.0


def normalize_lot(lot: float, min_lot: float = 0.01, step: float = 0.01, max_lot: float = 100.0) -> float:
    if lot < min_lot:
        return min_lot
    rounded = round((lot - min_lot) // step * step + min_lot, 2)
    rounded = min(max(rounded, min_lot), max_lot)
    return rounded


def get_lot_for_account(session: AccountSession) -> float:
    balance = session.get_balance()
    lot = compute_lot_size(balance)
    return normalize_lot(lot)
