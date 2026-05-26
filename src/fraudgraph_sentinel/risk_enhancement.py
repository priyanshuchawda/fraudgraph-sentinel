from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path

RISK_INDICATORS: dict[str, str] = {
    "PhishingEmailLabel": "Email sample is labeled phishing in the synthetic email dataset.",
    "ContainsLink": "Email sample contains a link.",
    "HasAttachment": "Email sample contains an attachment.",
    "UrgentLanguage": "Email sample has an urgency flag.",
    "SuspiciousUrlLabel": "URL sample is labeled suspicious/phishing in the URL dataset.",
    "InsecureHTTP": "URL sample does not use HTTPS.",
    "PasswordInputSignal": "URL page has a password input signal.",
    "PaymentKeywordSignal": "URL page includes bank, payment, or crypto keyword signals.",
    "FraudTransaction": "Transaction is labeled fraud in the synthetic transaction dataset.",
    "HighAmountTransfer": "Fraud transaction is a high-value transfer or cash-out.",
    "ZeroedOriginBalance": "Transaction leaves the origin account balance at zero.",
    "RepeatedFraudDestination": "Destination account receives repeated fraud transactions.",
}


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1", "1.0", "true", "yes"}


def email_risk_indicators(row: dict[str, str]) -> list[str]:
    indicators: list[str] = []
    if row.get("label", "").lower() == "phishing":
        indicators.append("PhishingEmailLabel")
    if _truthy(row.get("has_link")):
        indicators.append("ContainsLink")
    if _truthy(row.get("has_attachment")):
        indicators.append("HasAttachment")
    if _truthy(row.get("urgency_flag")):
        indicators.append("UrgentLanguage")
    return indicators


def url_risk_indicators(row: dict[str, str]) -> list[str]:
    indicators: list[str] = []
    if str(row.get("label", "")).strip() == "0":
        indicators.append("SuspiciousUrlLabel")
    if not _truthy(row.get("IsHTTPS")):
        indicators.append("InsecureHTTP")
    if _truthy(row.get("HasPasswordField")):
        indicators.append("PasswordInputSignal")
    if (
        _truthy(row.get("Bank"))
        or _truthy(row.get("Pay"))
        or _truthy(row.get("Crypto"))
    ):
        indicators.append("PaymentKeywordSignal")
    return indicators


def transaction_risk_indicators(
    row: dict[str, str], *, repeated_destinations: set[str]
) -> list[str]:
    indicators: list[str] = []
    amount = float(row.get("amount", "0") or 0)
    old_origin = float(row.get("oldBalanceOrigin", "0") or 0)
    new_origin = float(row.get("newBalanceOrigin", "0") or 0)
    tx_type = row.get("type", "")
    if _truthy(row.get("isFraud")):
        indicators.append("FraudTransaction")
    if amount >= 1_000_000 and tx_type in {"TRANSFER", "CASH_OUT"}:
        indicators.append("HighAmountTransfer")
    if old_origin > 0 and new_origin == 0:
        indicators.append("ZeroedOriginBalance")
    if row.get("destination") in repeated_destinations:
        indicators.append("RepeatedFraudDestination")
    return indicators


def read_email_xlsx(path: Path) -> list[dict[str, str]]:
    with zipfile.ZipFile(path) as archive:
        ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        shared: list[str] = []
        shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        for item in shared_root.findall("a:si", ns):
            shared.append(
                "".join(text.text or "" for text in item.findall(".//a:t", ns))
            )
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        parsed_rows: list[list[str]] = []
        for row in sheet.findall(".//a:sheetData/a:row", ns):
            values: list[str] = []
            for cell in row.findall("a:c", ns):
                ref = cell.attrib.get("r", "")
                col = re.sub(r"\d", "", ref)
                index = 0
                for char in col:
                    index = index * 26 + ord(char) - 64
                while len(values) < index - 1:
                    values.append("")
                value_node = cell.find("a:v", ns)
                value = "" if value_node is None else value_node.text or ""
                if cell.attrib.get("t") == "s" and value:
                    value = shared[int(value)]
                values.append(value)
            parsed_rows.append(values)
    headers = parsed_rows[0]
    return [dict(zip(headers, row, strict=False)) for row in parsed_rows[1:]]


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def export_risk_bundle(
    *,
    email_xlsx: Path,
    url_csv: Path,
    transactions_csv: Path,
    output_dir: Path,
    max_phishing_urls: int = 300,
    max_legitimate_urls: int = 100,
) -> dict[str, int | bool]:
    output_dir.mkdir(parents=True, exist_ok=True)

    indicator_rows = [
        {"name": name, "description": description}
        for name, description in sorted(RISK_INDICATORS.items())
    ]
    email_rows: list[dict[str, str]] = []
    email_rels: list[dict[str, str]] = []
    for row in read_email_xlsx(email_xlsx):
        email_id = f"email-{int(float(row['id']))}"
        email_rows.append(
            {
                "emailId": email_id,
                "subject": row.get("subject", ""),
                "sender": row.get("sender", ""),
                "label": row.get("label", ""),
            }
        )
        for indicator in email_risk_indicators(row):
            email_rels.append({"emailId": email_id, "indicator": indicator})

    url_rows: list[dict[str, str]] = []
    url_rels: list[dict[str, str]] = []
    selected_phishing = 0
    selected_legitimate = 0
    with url_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            is_phishing = row.get("label") == "0"
            if is_phishing and selected_phishing >= max_phishing_urls:
                continue
            if not is_phishing and selected_legitimate >= max_legitimate_urls:
                continue
            if is_phishing:
                selected_phishing += 1
            else:
                selected_legitimate += 1
            url_id = f"url-{len(url_rows) + 1}"
            url_rows.append(
                {
                    "urlId": url_id,
                    "url": row.get("URL", ""),
                    "domain": row.get("Domain", ""),
                    "label": row.get("label", ""),
                }
            )
            for indicator in url_risk_indicators(row):
                url_rels.append({"urlId": url_id, "indicator": indicator})
            if (
                selected_phishing >= max_phishing_urls
                and selected_legitimate >= max_legitimate_urls
            ):
                break

    with transactions_csv.open(newline="", encoding="utf-8") as handle:
        tx_rows = list(csv.DictReader(handle))
    destination_counts = Counter(
        row["destination"] for row in tx_rows if _truthy(row.get("isFraud"))
    )
    repeated_destinations = {
        destination for destination, count in destination_counts.items() if count > 1
    }
    tx_rels: list[dict[str, str]] = []
    for row in tx_rows:
        if not _truthy(row.get("isFraud")):
            continue
        for indicator in transaction_risk_indicators(
            row, repeated_destinations=repeated_destinations
        ):
            tx_rels.append(
                {"transactionId": row["transactionId"], "indicator": indicator}
            )

    write_rows(
        output_dir / "risk_indicators.csv", ["name", "description"], indicator_rows
    )
    write_rows(
        output_dir / "email_samples.csv",
        ["emailId", "subject", "sender", "label"],
        email_rows,
    )
    write_rows(
        output_dir / "url_samples.csv", ["urlId", "url", "domain", "label"], url_rows
    )
    write_rows(
        output_dir / "email_risk_relationships.csv",
        ["emailId", "indicator"],
        email_rels,
    )
    write_rows(
        output_dir / "url_risk_relationships.csv", ["urlId", "indicator"], url_rels
    )
    write_rows(
        output_dir / "transaction_risk_relationships.csv",
        ["transactionId", "indicator"],
        tx_rels,
    )

    manifest = {
        "riskIndicators": len(indicator_rows),
        "emailSamples": len(email_rows),
        "urlSamples": len(url_rows),
        "emailRiskRelationships": len(email_rels),
        "urlRiskRelationships": len(url_rels),
        "transactionRiskRelationships": len(tx_rels),
        "additionalNodes": len(indicator_rows) + len(email_rows) + len(url_rows),
        "additionalRelationships": len(email_rels) + len(url_rels) + len(tx_rels),
        "causalityClaimed": False,
    }
    (output_dir / "risk_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest
