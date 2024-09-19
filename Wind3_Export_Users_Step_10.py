import os
import time
import logging

def setup_logging(log_file_path):
    """Configura il logging."""
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

def main(uid_file_path, input_ldif_path, log_file_path, canale):
    output_file_name = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_parentuid_child.ldif"
    setup_logging(log_file_path)

    start_time = time.time()
    script_name = os.path.basename(__file__)

    # Log dell'inizio dell'esecuzione
    logging.info(f"Start dello script: {script_name}")

    try:
        # Leggi gli uid dal file
        with open(uid_file_path, 'r') as uid_file:
            uids = {line.split(':')[1].strip() for line in uid_file if line.strip() and line.startswith("uid:")}

        logging.info(f"Numero di uid letti: {len(uids)}")
        logging.debug(f"Lista degli uid recuperati: {uids}")  # Opzione di debug

        # Verifica nel file LDIF e trova gli utenti con parentuid corrispondenti
        matched_dns = []
        with open(input_ldif_path, 'r') as ldif_file:
            current_entry = []
            for line in ldif_file:
                current_entry.append(line.strip())
                
                if line.startswith("dn:") and current_entry:
                    dn = current_entry[0]  # La prima riga è il DN
                    parentuid = None

                    for entry in current_entry:
                        if entry.startswith("parentuid:"):
                            parentuid = entry.split("parentuid:")[1].strip()

                    # Controlla se il parentuid è presente nel set di uid
                    if parentuid in uids:
                        matched_dns.append(dn)
                        logging.debug(f"Utente trovato: {dn} con parentuid: {parentuid}")  # Stampa il DN come opzione di debug

                    current_entry = []

            # Controlla l'ultima entry
            if current_entry:
                dn = current_entry[0]  # La prima riga è il DN
                parentuid = None

                for entry in current_entry:
                    if entry.startswith("parentuid:"):
                        parentuid = entry.split("parentuid:")[1].strip()

                if parentuid in uids:
                    matched_dns.append(dn)
                    logging.debug(f"Utente trovato: {dn} con parentuid: {parentuid}")  # Stampa il DN come opzione di debug

        # Scrittura dei DN salvati nel file di output
        with open(output_file_name, 'w') as output_file:
            for dn in matched_dns:
                output_file.write(dn + "\n")  # Scrivi ogni DN su una nuova riga

        num_saved_entries = len(matched_dns)
        logging.info(f"Numero di DN salvati nel file {output_file_name}: {num_saved_entries}")

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
    uid_file_path = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_parentuid_list.ldif"
    input_ldif_path = "/mnt/c/temporary/wind/migrationUsersProcedure/o=pos.wind.it.ldif"
    log_file_path = "/mnt/c/temporary/wind/migrationUsersProcedure/exportProcedure.log"

    main(uid_file_path, input_ldif_path, log_file_path, canale)

