import os
import time
import logging

def setup_logging(log_file_path):
    """Configura il logging."""
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

def main(input_file_path, log_file_path, canale):
    output_file_name = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_users_to_import_FINAL.ldif"
    setup_logging(log_file_path)

    start_time = time.time()
    script_name = os.path.basename(__file__)

    # Log dell'inizio dell'esecuzione
    logging.info(f"Start dello script: {script_name}")

    try:
        with open(input_file_path, 'r') as input_file:
            entries = input_file.read().splitlines()

        total_entries = 0
        filtered_entries = []
        entries_to_remove = []
        current_entry = []

        for line in entries:
            current_entry.append(line)
            if line.startswith("dn:"):
                total_entries += 1  # Conta l'entry completa

            if line.startswith("dn:") and current_entry:
                # Se la entry corrente è completa, controlla la data di passwordexpirationtime
                if any("passwordexpirationtime:" in entry for entry in current_entry):
                    expiration_time = [entry.split("passwordexpirationtime:")[1].strip() for entry in current_entry if "passwordexpirationtime:" in entry]
                    if expiration_time and int(expiration_time[0]) < 20240101:
                        entries_to_remove.append("\n".join(current_entry))
                    else:
                        filtered_entries.append("\n".join(current_entry))
                else:
                    filtered_entries.append("\n".join(current_entry))
                current_entry = []
        
        # Controlla l'ultima entry
        if current_entry:
            if any("passwordexpirationtime:" in entry for entry in current_entry):
                expiration_time = [entry.split("passwordexpirationtime:")[1].strip() for entry in current_entry if "passwordexpirationtime:" in entry]
                if expiration_time and int(expiration_time[0]) < 20240101:
                    entries_to_remove.append("\n".join(current_entry))
                else:
                    filtered_entries.append("\n".join(current_entry))
            else:
                filtered_entries.append("\n".join(current_entry))

        num_password_expiration_time = len(entries_to_remove)
        num_entries_deleted = num_password_expiration_time
        logging.info(f"Numero di entry aventi passwordexpirationtime antecedente al 20240101: {num_password_expiration_time}")

        # Scrittura delle entry rimanenti nel file di output
        with open(output_file_name, 'w') as output_file:
            for entry in filtered_entries:
                output_file.write(entry + "\n\n")  # Aggiunge una riga vuota tra le entry

        num_remaining_entries = len(filtered_entries)
        logging.info(f"Numero di entry salvate nel file {output_file_name}: {num_remaining_entries}")
        logging.info(f"Numero totale di utenti letti: {total_entries}")

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
    input_file_path = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_users_to_import_02.ldif"
    log_file_path = "/mnt/c/temporary/wind/migrationUsersProcedure/exportProcedure.log"

    main(input_file_path, log_file_path, canale)

