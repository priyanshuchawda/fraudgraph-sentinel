from fraudgraph_sentinel.graph_stats import estimate_graph_size
from fraudgraph_sentinel.model import Transaction
import pytest

from fraudgraph_sentinel.sampling import (
    REQUIRED_COLUMNS,
    sample_transactions,
    sample_transactions_from_csv,
    sample_transactions_from_csv_with_stats,
)


def make_tx(index: int, fraud: bool = False) -> Transaction:
    return Transaction(
        step=index,
        transaction_type="TRANSFER" if fraud else "PAYMENT",
        amount=1000.0 + index,
        origin=f"C{index}",
        old_balance_origin=1000.0,
        new_balance_origin=0.0 if fraud else 500.0,
        destination=f"D{index % 3}",
        old_balance_destination=0.0,
        new_balance_destination=1000.0,
        is_fraud=fraud,
        is_flagged_fraud=False,
    )


def test_sampler_keeps_all_fraud_and_limits_non_fraud():
    rows = [make_tx(i, fraud=i in {2, 5, 9}) for i in range(12)]

    sampled = sample_transactions(rows, max_non_fraud=4)

    assert sum(tx.is_fraud for tx in sampled) == 3
    assert sum(not tx.is_fraud for tx in sampled) == 4
    assert {tx.step for tx in sampled if tx.is_fraud} == {2, 5, 9}


def test_graph_size_estimate_counts_unique_accounts_and_relationships():
    rows = [make_tx(1, fraud=True), make_tx(2, fraud=False), make_tx(3, fraud=False)]

    estimate = estimate_graph_size(rows)

    assert estimate.accounts == 6
    assert estimate.transactions == 3
    assert estimate.transaction_types == 2
    assert estimate.fraud_labels == 2
    assert estimate.nodes == 13
    assert estimate.relationships == 12
    assert estimate.fits_conservative_aura_free is True


def test_fast_csv_sampler_materializes_only_selected_rows(tmp_path):
    source = tmp_path / "transactions.csv"
    source.write_text(
        "\n".join(
            [
                "step,type,amount,nameOrig,oldbalanceOrg,newbalanceOrig,nameDest,oldbalanceDest,newbalanceDest,isFraud,isFlaggedFraud",
                "1,PAYMENT,10,C1,100,90,M1,0,0,0,0",
                "2,PAYMENT,20,C2,100,80,M2,0,0,0,0",
                "3,TRANSFER,30,C3,30,0,C9,0,30,1,0",
                "4,PAYMENT,40,C4,100,60,M4,0,0,0,0",
            ]
        ),
        encoding="utf-8",
    )

    sampled = sample_transactions_from_csv(source, max_non_fraud=1)

    assert [tx.step for tx in sampled] == [1, 3]
    assert sampled[1].is_fraud is True


def test_csv_sampler_reports_reproducible_selection_stats(tmp_path):
    source = tmp_path / "transactions.csv"
    source.write_text(
        "\n".join(
            [
                "step,type,amount,nameOrig,oldbalanceOrg,newbalanceOrig,nameDest,oldbalanceDest,newbalanceDest,isFraud,isFlaggedFraud",
                "1,PAYMENT,10,C1,100,90,M1,0,0,0,0",
                "2,TRANSFER,20,C2,20,0,C3,0,20,1,0",
                "3,CASH_OUT,30,C4,30,0,C5,0,30,1,0",
            ]
        ),
        encoding="utf-8",
    )

    result = sample_transactions_from_csv_with_stats(source, max_non_fraud=1)

    assert result.stats.source_dataset == "transactions.csv"
    assert result.stats.source_rows == 3
    assert result.stats.fraud_rows_selected == 2
    assert result.stats.non_fraud_rows_sampled == 1
    assert result.stats.sampling_rule == "all_fraud_plus_first_n_non_fraud"
    assert result.stats.deterministic_seed == "not_applicable_first_n"


def test_csv_sampler_rejects_missing_required_columns(tmp_path):
    source = tmp_path / "bad.csv"
    source.write_text("step,type,amount\n1,PAYMENT,10\n", encoding="utf-8")

    with pytest.raises(ValueError) as error:
        sample_transactions_from_csv_with_stats(source, max_non_fraud=1)

    assert "missing required columns" in str(error.value)
    assert "nameOrig" in str(error.value)
    assert set(REQUIRED_COLUMNS) >= {"step", "type", "amount", "nameOrig"}
