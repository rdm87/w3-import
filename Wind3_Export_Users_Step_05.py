import os
import time
import logging

def setup_logging(log_file_path):
    """Configura il logging."""
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

def main(dealername_file_path, input_ldif_path, log_file_path, canale):
    output_file_name = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_utenti_secondo_livello_01.ldif"
    setup_logging(log_file_path)

    start_time = time.time()
    script_name = os.path.basename(__file__)

    # Log dell'inizio dell'esecuzione
    logging.info(f"Start dello script: {script_name}")

    try:
        # Leggi i dealername dal file
        with open(dealername_file_path, 'r') as dealer_file:
            dealer_names = {line.strip() for line in dealer_file if line.strip()}  # Usa un set per evitare duplicati

        saved_entries = []
        total_dealers = len(dealer_names)
        logging.info(f"Numero di dealername letti: {total_dealers}")

        # Leggi il file LDIF e cerca gli utenti
        with open(input_ldif_path, 'r') as ldif_file:
            current_entry = []
            for line in ldif_file:
                if line.startswith("dn:") and current_entry:
                    dn = current_entry[0].strip()  # La prima riga è il DN
                    if any(dealername in dn for dealername in dealer_names) and "ou=Utenti secondo livello" in dn:
                        saved_entries.append("\n".join(current_entry))
                    current_entry = []
                current_entry.append(line.strip())

            # Controlla l'ultima entry
            if current_entry:
                dn = current_entry[0].strip()  # La prima riga è il DN
                if any(dealername in dn for dealername in dealer_names) and "ou=Utenti secondo livello" in dn:
                    saved_entries.append("\n".join(current_entry))

        # Scrittura delle entry salvate nel file di output
        with open(output_file_name, 'w') as output_file:
            for entry in saved_entries:
                output_file.write(entry + "\n\n")  # Aggiunge una riga vuota tra le entry

        num_saved_entries = len(saved_entries)
        logging.info(f"Numero di utenti salvati nel file {output_file_name}: {num_saved_entries}")

    except Exception as e:
        logging.error(f"Si è verificato un errore: {e}")
        return

    end_time = time.time()
    execution_time = end_time - start_time
    logging.info(f"Tempo di esecuzione dello script: {execution_time:.2f} secondi")
    logging.info(f"Fine dello script: {script_name}")

if __name__ == "__main__":
    # Parametri da passare tramite variabili
    canale = "FR"
    dealername_file_path = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_dealername_utenti_canale_list.txt"
    input_ldif_path = "/mnt/c/temporary/wind/migrationUsersProcedure/o=pos.wind.it.ldif"
    log_file_path = "/mnt/c/temporary/wind/migrationUsersProcedure/exportProcedure.log"

    main(dealername_file_path, input_ldif_path, log_file_path, canale)

