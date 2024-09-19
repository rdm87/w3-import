import os
import time
import logging

def setup_logging(log_file_path):
    """Configura il logging."""
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

def main(input_file_path, log_file_path, canale):
    output_file_name = f"{canale}_users_to_import_01.ldif"
    setup_logging(log_file_path)

    start_time = time.time()
    script_name = os.path.basename(__file__)

    # Log dell'inizio dell'esecuzione
    logging.info(f"Start dello script: {script_name}")

    try:
        with open(input_file_path, 'r') as input_file:
            entries = input_file.read().splitlines()

        total_entries = len(entries)
        logging.info(f"Numero totale di entry lette: {total_entries}")

        # Filtraggio delle entry con canale specificato
        filtered_entries = []
        current_entry = []
        for line in entries:
            if line.startswith("dn:") and current_entry:
                # Se la entry corrente è completa, controlla se ha il canale giusto
                if any(f'canale: {canale}' in entry for entry in current_entry):
                    filtered_entries.append("\n".join(current_entry))
                current_entry = []
            current_entry.append(line)
        
        # Controlla l'ultima entry
        if current_entry and any(f'canale: {canale}' in entry for entry in current_entry):
            filtered_entries.append("\n".join(current_entry))

        num_canale_entries = len(filtered_entries)
        logging.info(f"Numero di entry con canale {canale}: {num_canale_entries}")

        # Scrittura delle entry filtrate nel file di output
        output_file_path = os.path.join(os.path.dirname(input_file_path), output_file_name)
        with open(output_file_path, 'w') as output_file:
            for entry in filtered_entries:
                output_file.write(entry + "\n\n")  # Aggiunge una riga vuota tra le entry

        saved_entries = num_canale_entries
        logging.info(f"Numero di entry salvate nel file {output_file_path}: {saved_entries}")

    except Exception as e:
        logging.error(f"Si è verificato un errore: {e}")
        return

    end_time = time.time()
    execution_time = end_time - start_time
    logging.info(f"Tempo di esecuzione dello script: {execution_time:.2f} secondi")
    logging.info(f"Fine dello script: {script_name}")

if __name__ == "__main__":
    # Parametri da passare tramite variabili
    input_file_path = "/mnt/c/temporary/wind/migrationUsersProcedure/o=pos.wind.it.ldif"
    log_file_path = "/mnt/c/temporary/wind/migrationUsersProcedure/exportProcedure.log"
    canale = "FR"

    main(input_file_path, log_file_path, canale)

