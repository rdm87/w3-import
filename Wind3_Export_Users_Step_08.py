import os
import time
import logging

def setup_logging(log_file_path):
    """Configura il logging."""
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

def main(parentuid_file_path, input_ldif_path, log_file_path, canale):
    output_file_name = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_parentuid_list.ldif"
    setup_logging(log_file_path)

    start_time = time.time()
    script_name = os.path.basename(__file__)

    # Log dell'inizio dell'esecuzione
    logging.info(f"Start dello script: {script_name}")

    try:
        # Leggi i parentuid dal file
        with open(parentuid_file_path, 'r') as parentuid_file:
            parent_uids = {line.split(';')[1].strip() for line in parentuid_file if line.strip()}
            parent_uids = {uid.split(': ')[1].strip() for uid in parent_uids}  # Rimuovi "parentuid:"

        logging.info(f"Numero di parentuid letti: {len(parent_uids)}")
        logging.debug(f"Lista dei parentuid recuperati: {parent_uids}")  # Opzione di debug

        # Leggi il file LDIF e cerca gli utenti con uid corrispondenti ai parentuid
        found_entries = []
        with open(input_ldif_path, 'r') as ldif_file:
            current_entry = []
            for line in ldif_file:
                current_entry.append(line.strip())
                
                if line.startswith("dn:"):
                    dn = current_entry[0]  # La prima riga è il DN

                    # Escludi le entry con il prefisso "realm=sso,"
                    if "realm=sso," in dn:
                        current_entry = []  # Reset current_entry
                        continue  # Salta questa entry

                # Se abbiamo un DN, controlliamo gli UID
                if "uid:" in line:
                    uid = None
                    for entry in current_entry:
                        if entry.startswith("uid:"):
                            uid = entry.split("uid:")[1].strip()
                            break

                    # Controlla se l'uid è presente nel set di parentuid
                    if uid and uid in parent_uids:
                        found_entries.append("\n".join(current_entry))
                        logging.debug(f"Utente trovato: {dn} con uid: {uid}")  # Stampa il DN come opzione di debug

                    current_entry = []

            # Controlla l'ultima entry
            if current_entry:
                dn = current_entry[0]  # La prima riga è il DN

                # Escludi le entry con il prefisso "realm=sso,"
                if "realm=sso," not in dn:
                    uid = None
                    for entry in current_entry:
                        if entry.startswith("uid:"):
                            uid = entry.split("uid:")[1].strip()
                            break

                    if uid and uid in parent_uids:
                        found_entries.append("\n".join(current_entry))
                        logging.debug(f"Utente trovato: {dn} con uid: {uid}")  # Stampa il DN come opzione di debug

        # Scrittura delle informazioni salvate nel file di output
        with open(output_file_name, 'w') as output_file:
            for entry in found_entries:
                output_file.write(entry + "\n\n")  # Aggiungi una riga vuota tra le entry

        num_saved_entries = len(found_entries)
        logging.info(f"Numero di entry salvate nel file {output_file_name}: {num_saved_entries}")

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
    parentuid_file_path = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_parentuid_secondo_livello_list.txt"
    input_ldif_path = "/mnt/c/temporary/wind/migrationUsersProcedure/o=pos.wind.it.ldif"
    log_file_path = "/mnt/c/temporary/wind/migrationUsersProcedure/exportProcedure.log"

    main(parentuid_file_path, input_ldif_path, log_file_path, canale)

