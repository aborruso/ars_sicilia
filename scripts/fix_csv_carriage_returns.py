#!/usr/bin/env python3
"""
Fix carriage returns (\r) in CSV field values.

Rimuove \r dai valori dei campi senza modificare la struttura del CSV.
"""
import csv
from pathlib import Path

def fix_csv_cr(input_path: str, output_path: str = None):
    """
    Rimuove carriage returns dai valori CSV.

    Args:
        input_path: Path CSV input
        output_path: Path CSV output (default: sovrascrive input)
    """
    if output_path is None:
        output_path = input_path

    input_file = Path(input_path)
    temp_file = input_file.with_suffix('.tmp')

    rows_fixed = 0
    total_rows = 0

    # Leggi e pulisci
    with open(input_file, 'r', newline='', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames

        cleaned_rows = []
        for row in reader:
            total_rows += 1
            row_fixed = False

            # Rimuovi \r da ogni valore
            for key in row:
                if '\r' in row[key]:
                    row[key] = row[key].replace('\r', '')
                    row_fixed = True

            if row_fixed:
                rows_fixed += 1

            cleaned_rows.append(row)

    # Scrivi pulito
    with open(temp_file, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    # Sostituisci originale
    temp_file.replace(output_path)

    print(f"✓ CSV pulito")
    print(f"  Righe totali:  {total_rows}")
    print(f"  Righe corrette: {rows_fixed}")
    print(f"  File: {output_path}")


if __name__ == '__main__':
    anagrafica_path = 'data/anagrafica_video.csv'
    fix_csv_cr(anagrafica_path)
