import os
import time
import logging

def setup_logging(log_file_path):
    """Configura il logging."""
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

def main(input_file_path, log_file_path, canale):
    output_file_name = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_utenti_secondo_livello_FINAL.ldif"
    setup_logging(log_file_path)

    start_time = time.time()
    script_name = os.path.basename(__file__)

    # Log dell'inizio dell'esecuzione
    logging.info(f"Start dello script: {script_name}")

    try:
        saved_entries = []
        excluded_entries = []
        current_entry = []

        with open(input_file_path, 'r') as input_file:
            for line in input_file:
                current_entry.append(line.strip())
                if line.startswith("dn:") and current_entry:
                    # Controlla se deve escludere l'entry
                    if any("passwordexpirationdate:" in entry for entry in current_entry):
                        expiration_date = [
                            entry.split("passwordexpirationdate:")[1].strip()
                            for entry in current_entry if "passwordexpirationdate:" in entry
                        ]
                        if expiration_date and int(expiration_date[0]) < 20240101:
                            excluded_entries.append("\n".join(current_entry))
                        else:
                            saved_entries.append("\n".join(current_entry))
                    else:
                        saved_entries.append("\n".join(current_entry))
                    current_entry = []
            
            # Controlla l'ultima entry
            if current_entry:
                if any("passwordexpirationdate:" in entry for entry in current_entry):
                    expiration_date = [
                        entry.split("passwordexpirationdate:")[1].strip()
                        for entry in current_entry if "passwordexpirationdate:" in entry
                    ]
                    if expiration_date and int(expiration_date[0]) < 20240101:
                        excluded_entries.append("\n".join(current_entry))
                    else:
                        saved_entries.append("\n".join(current_entry))
                else:
                    saved_entries.append("\n".join(current_entry))

        # Scrittura delle entry salvate nel file di output
        with open(output_file_name, 'w') as output_file:
            for entry in saved_entries:
                output_file.write(entry + "\n\n")  # Aggiunge una riga vuota tra le entry

        num_saved_entries = len(saved_entries)
        num_excluded_entries = len(excluded_entries)
        logging.info(f"Numero di utenti salvati nel file {output_file_name}: {num_saved_entries}")
        logging.info(f"Numero di utenti non salvati perché aventi passwordexpirationdate antecedente al 20240101: {num_excluded_entries}")

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
    input_file_path = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_utenti_secondo_livello_01.ldif"
    log_file_path = "/mnt/c/temporary/wind/migrationUsersProcedure/exportProcedure.log"

    main(input_file_path, log_file_path, canale)

