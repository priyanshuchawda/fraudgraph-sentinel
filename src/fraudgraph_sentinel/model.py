from __future__ import annotations

from dataclasses import dataclass


def parse_bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


@dataclass(frozen=True)
class Transaction:
    step: int
    transaction_type: str
    amount: float
    origin: str
    old_balance_origin: float
    new_balance_origin: float
    destination: str
    old_balance_destination: float
    new_balance_destination: float
    is_fraud: bool
    is_flagged_fraud: bool

    @property
    def transaction_id(self) -> str:
        return f"tx-{self.step}-{self.origin}-{self.destination}"

    @property
    def fraud_label(self) -> str:
        return "Fraud" if self.is_fraud else "Legitimate"

    @property
    def risk_text(self) -> str:
        verdict = "Fraudulent" if self.is_fraud else "Legitimate"
        origin_zeroed = self.old_balance_origin > 0 and self.new_balance_origin == 0
        zeroed_text = " origin balance zeroed" if origin_zeroed else ""
        flagged_text = " flagged by rule" if self.is_flagged_fraud else ""
        return (
            f"{verdict} {self.transaction_type} transaction for {self.amount:.2f}"
            f" from {self.origin} to {self.destination}.{zeroed_text}{flagged_text}"
        )

    @classmethod
    def from_csv_row(cls, row: dict[str, str]) -> "Transaction":
        return cls(
            step=int(row["step"]),
            transaction_type=row["type"],
            amount=float(row["amount"]),
            origin=row["nameOrig"],
            old_balance_origin=float(row["oldbalanceOrg"]),
            new_balance_origin=float(row["newbalanceOrig"]),
            destination=row["nameDest"],
            old_balance_destination=float(row["oldbalanceDest"]),
            new_balance_destination=float(row["newbalanceDest"]),
            is_fraud=parse_bool(row["isFraud"]),
            is_flagged_fraud=parse_bool(row["isFlaggedFraud"]),
        )
