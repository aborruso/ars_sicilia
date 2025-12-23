#!/usr/bin/env python3
"""
Esempi di utilizzo dell'API ARS Sicilia

Questo file mostra come utilizzare la client library per eseguire
diverse operazioni di ricerca sui Disegni di Legge.
"""

import sys
import os
import json

# Aggiungi il path della cartella parent per importare
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ars_api_client import ARSClient


def print_separator(title: str):
    """Print a formatted separator."""
    print(f"\n{'=' * 60}")
    print(f"  {title}  ")
    print(f"{'=' * 60}\n")


def example_1_search_all_bills():
    """Esempio 1: Ricerca di tutti i disegni di legge di una legislatura."""
    print_separator("ESEMPIO 1: Tutti i Disegni di Legge (XVIII Legislatura)")

    client = ARSClient()

    # Esegui la ricerca
    result = client.search(legisl=18)
    print(f"✓ Search eseguita. Totale risultati: {result['total_results']}")
    print(f"✓ Query ID: {client.current_query_id}")

    # Ottieni la lista dei risultati (prima pagina)
    list_result = client.get_results_list(page=1)
    print(f"✓ Pagine totali: {list_result['pagination'].get('total_pages', '?')}")

    # Mostra primi 5 risultati
    print("\nPrimi 5 risultati:")
    for i, item in enumerate(list_result["results"][:5], 1):
        print(
            f"  {i}. [{item['legislature']}] {item['number']} - {item['date']} - {item['title']}"
        )

    return list_result


def example_2_search_by_year():
    """Esempio 2: Ricerca disegni di legge per anno."""
    print_separator("ESEMPIO 2: Ricerca per Anno (2024)")

    client = ARSClient()

    # Ricerca disegni del 2024, legislatura 18
    query = "((18.LEGISL) AND 2024.ANNO)"
    result = client.search(legisl=18, query_text=query)
    print(f"✓ Query: {query}")
    print(f"✓ Risultati trovati: {result['total_results']}")

    # Ottieni risultati
    list_result = client.get_results_list(page=1)

    # Mostra primi 3
    print("\nPrimi 3 risultati del 2024:")
    for i, item in enumerate(list_result["results"][:3], 1):
        print(
            f"  {i}. [{item['legislature']}] {item['number']} - {item['date']} - {item['title']}"
        )

    return list_result


def example_3_search_by_signatory():
    """Esempio 3: Ricerca disegni di legge per firmatario."""
    print_separator("ESEMPIO 3: Ricerca per Firmatario")

    client = ARSClient()

    # Ricerca disegni firmati da Venezia
    query = "(Venezia.FIRMAT AND 18.LEGISL)"
    result = client.search(legisl=18, query_text=query)
    print(f"✓ Query: {query}")
    print(f"✓ Risultati trovati: {result['total_results']}")

    # Ottieni risultati
    list_result = client.get_results_list(page=1)

    if list_result["results"]:
        print("\nPrimi 3 disegni firmati da Venezia:")
        for i, item in enumerate(list_result["results"][:3], 1):
            print(f"  {i}. {item['number']} - {item['title']}")
    else:
        print("\nNessun risultato trovato.")

    return list_result


def example_4_search_by_number():
    """Esempio 4: Ricerca disegno di legge specifico per numero."""
    print_separator("ESEMPIO 4: Ricerca per Numero (DDL 1052)")

    client = ARSClient()

    # Esegui una nuova ricerca per il numero specifico
    result = client.search(legisl=18, legge="1052")
    print(f"✓ Search eseguita. Risultati: {result['total_results']}")

    # Ottieni lista risultati
    list_result = client.get_results_list(page=1)

    # Trova il disegno specifico nei risultati
    target_bill = None
    if list_result["results"]:
        for item in list_result["results"]:
            if item["number"] == "1052":
                target_bill = item
                break

    if target_bill:
        print(f"✓ Trovato: [{target_bill['legislature']}] {target_bill['number']}")
        print(f"✓ Titolo: {target_bill['title']}")

        # Ottieni contenuto completo
        print(f"\nCaricamento contenuto completo...")
        doc_result = client.get_document_content(
            client.current_query_id, target_bill["index"]
        )

        if doc_result:
            content = doc_result.get("content", {})

            # Mostra stato iter
            if "iteration" in content:
                iter_data = content["iteration"]
                attuale = iter_data.get("attuale", "N/A")
                storico = iter_data.get("storico", "N/A")
                print(f"\n✓ Iter Attuale: {attuale}")
                print(f"✓ Iter Storico: {storico}")

            # Mostra sezioni chiave
            sections = [
                k for k in content.keys() if k not in ["full_text", "iteration"]
            ]
            if sections:
                print(f"\n✓ Sezioni documento: {', '.join(sections)}")

            # Salva testo completo
            if "full_text" in content:
                text = content["full_text"]
                with open("disegno_1052_testo.txt", "w", encoding="utf-8") as f:
                    f.write(text)
                print(
                    f"\n✓ Testo salvato in disegno_1052_testo.txt ({len(text)} caratteri)"
                )
                print(f"✓ Parole: {len(text.split())}")
    else:
        print("✗ Disegno di legge non trovato.")

    return target_bill


def example_5_search_with_advanced_query():
    """Esempio 5: Ricerca con query avanzata multi-campo."""
    print_separator("ESIEMPIO 5: Ricerca Avanzata (Titolo E Sommario)")

    client = ARSClient()

    # Ricerca nel titolo e sommario disegni che contengono "peschicoltura"
    query = "(peschicoltura.TITOLO,SOMMAR AND 18.LEGISL)"
    result = client.search_by_query(query=query, legisl=18)

    if result:
        print(f"✓ Query: {query}")
        print(f"✓ Risultati trovati: {len(result)}")

        print("\nPrimi 3 disegni sulla peschicoltura:")
        for i, item in enumerate(result[:3], 1):
            print(f"  {i}. {item['number']} - {item['title']}")
    else:
        print("✗ Nessun risultato trovato.")

    return result


def example_6_pagination():
    """Esempio 6: Navigazione tra le pagine."""
    print_separator("ESIEMPIO 6: Navigazione tra Pagine")

    client = ARSClient()

    # Esegui ricerca base
    search_result = client.search(legisl=18)

    # Scarica pagina 1
    page_1 = client.get_results_list(page=1)
    print(f"✓ Pagina 1: {len(page_1['results'])} risultati")

    # Scarica pagina 2
    page_2 = client.get_results_list(page=2)
    print(f"✓ Pagina 2: {len(page_2['results'])} risultati")

    # Scarica pagina 3
    page_3 = client.get_results_list(page=3)
    print(f"✓ Pagina 3: {len(page_3['results'])} risultati")

    print(
        f"\n✓ Totale disegni scaricati: {len(page_1['results']) + len(page_2['results']) + len(page_3['results'])}"
    )

    return {
        "page_1": page_1["results"],
        "page_2": page_2["results"],
        "page_3": page_3["results"],
    }


def example_7_get_full_document():
    """Esempio 7: Ottenere contenuto completo di un disegno di legge."""
    print_separator("ESIEMPIO 7: Contenuto Completo Disegno di Legge")

    client = ARSClient()

    # Prima cerca il disegno 1052
    print("Cercando disegno DDL 1052...")
    list_result = client.get_results_list(page=1)

    # Trova il disegno specifico
    target_index = None
    if list_result["results"]:
        for i, item in enumerate(list_result["results"]):
            if item["number"] == "1052":
                target_index = i + 1  # Indice basato su 1
                break

    if target_index:
        print(f"✓ Trovato alla posizione {target_index}")

        # Ottieni contenuto completo
        doc_result = client.get_document_content(1, target_index)

        if doc_result:
            content = doc_result.get("content", {})

            # Mostra sezioni chiave
            sections = [
                k for k in content.keys() if k not in ["full_text", "iteration"]
            ]
            if sections:
                print(f"\n✓ Sezioni documento: {', '.join(sections)}")

            # Salva testo completo
            if "full_text" in content:
                text = content["full_text"]
                with open("disegno_1052_completo.txt", "w", encoding="utf-8") as f:
                    f.write(text)
                print(
                    f"\n✓ Testo completo salvato in disegno_1052_completo.txt ({len(text)} caratteri)"
                )
                print(f"✓ Prime 500 caratteri: {text[:500]}...")
                print(f"\n✓ Parole: {len(text.split())}")
    else:
        print("✗ Errore nel recupero del contenuto.")


def example_8_export_all_bills():
    """Esempio 8: Esportazione completa in JSON."""
    print_separator("ESIEMPIO 8: Esportazione Completa in JSON")

    client = ARSClient()

    # Ottieni primi 50 disegni della legislatura 18
    print("Recupero disegni (prime 2 pagine)...")
    all_bills = client.get_all_bills(legisl=18, max_pages=2, delay=1)

    print(f"✓ Totale disegni scaricati: {len(all_bills)}")

    # Statistiche per anno
    anni = {}
    for bill in all_bills:
        date_str = bill.get("date", "")
        if date_str:
            # Formato: DD.MM.YY -> estrai anno
            parts = date_str.split(".")
            if len(parts) == 3:
                # Normalizza anno (es. 25 -> 2025)
                year_short = parts[2]
                if len(year_short) == 2 and year_short.isdigit():
                    if year_short.startswith("0"):
                        year = "20" + year_short[1:]
                    else:
                        year = year_short
                else:
                    year = year_short

                if year:
                    anni[year] = anni.get(year, 0) + 1

    print(f"\n✓ Distribuzione per anno:")
    for anno in sorted(anni.keys(), reverse=True):
        count = anni[anno]
        print(f"  {anno}: {count} disegni")

    # Esporta in JSON
    with open("ddl_xviii_primi_50.json", "w", encoding="utf-8") as f:
        json.dump(all_bills, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Esportazione completata in ddl_xviii_primi_50.json")

    return all_bills


def example_9_search_with_range():
    """Esempio 9: Ricerca disegni in un range di numeri."""
    print_separator("ESIEMPIO 9: Ricerca per Range (DDL 1050-1055)")

    client = ARSClient()

    # Ricerca disegni dal 1050 al 1055
    query = "((18.LEGISL) AND (1050/1055).NUMDDL)"
    result = client.search_by_query(query=query, legisl=18)

    if result:
        print(f"✓ Query: {query}")
        print(f"✓ Disegni trovati: {len(result)}")

        print("\nDisegni nel range 1050-1055:")
        for i, item in enumerate(result[:10], 1):
            print(f"  {i}. {item['number']} - {item['date']} - {item['title']}")
    else:
        print("✗ Nessun risultato trovato.")

    return result


def example_10_exclude_terms():
    """Esempio 10: Ricerca con esclusione di termini."""
    print_separator("ESIEMPIO 10: Ricerca con Esclusione (NOT)")

    client = ARSClient()

    # Tutti i disegni legislativi, escludendo quelli governativi
    query = "((18.LEGISL) NOT (Governativa.FIRMAT))"
    result = client.search_by_query(query=query, legisl=18)

    if result:
        print(f"✓ Query: {query}")
        print(f"✓ Disegni non governativi: {len(result)}")

        print("\nPrimi 5 disegni non governativi:")
        for i, item in enumerate(result[:5], 1):
            iniziativa = item.get("iniziativa", "N/A")
            print(f"  {i}. {item['number']} - {item['date']} - {item['title']}")
            print(f"      Iniziativa: {iniziativa}")
    else:
        print("✗ Nessun risultato trovato.")

    return result


def main():
    """Menu principale per selezionare l'esempio."""

    print("""
╔════════════════════════════════════════════════╗
║      ESEMPI DI UTILIZZO API ARS SICILIA                   ║
╚═════════════════════════════════════════════════╝

Seleziona un esempio:
  1. Tutti i Disegni di Legge (XVIII Legislatura)
  2. Ricerca per Anno (2024)
  3. Ricerca per Firmatario
  4. Ricerca per Numero (DDL 1052)
  5. Ricerca Avanzata (Titolo E Sommario)
  6. Navigazione tra Pagine
  7. Contenuto Completo Disegno di Legge
  8. Esportazione Completa in JSON
  9. Ricerca per Range (DDL 1050-1055)
  10. Ricerca con Esclusione (NOT)
  0. Esci

""")

    try:
        choice = input("\nInserisci numero (1-10) o '0' per uscire: ").strip()

        if choice == "0":
            print("Uscita...")
            return

        choice_int = int(choice)

        examples = {
            1: example_1_search_all_bills,
            2: example_2_search_by_year,
            3: example_3_search_by_signatory,
            4: example_4_search_by_number,
            5: example_5_search_with_advanced_query,
            6: example_6_pagination,
            7: example_7_get_full_document,
            8: example_8_export_all_bills,
            9: example_9_search_with_range,
            10: example_10_exclude_terms,
        }

        if choice_int in examples:
            result = examples[choice_int]()
            print(f"\n✓ Esempio {choice_int} completato con successo!")
        else:
            print(f"\n✗ Scelta non valida. Inserisci un numero da 1 a 10.")

    except KeyboardInterrupt:
        print("\n\nInterruzione da utente.")
    except Exception as e:
        print(f"\n✗ Errore: {e}")


if __name__ == "__main__":
    main()
