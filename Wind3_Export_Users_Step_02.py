import os
import time
import logging

def setup_logging(log_file_path):
    """Configura il logging."""
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

def is_five_digit_number(value):
    """Controlla se il valore è un numero a 5 cifre."""
    return value.isdigit() and len(value) == 5

def main(input_file_path, log_file_path, canale):
    output_file_name = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_users_to_import_02.ldif"
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

        # Filtraggio delle entry
        filtered_entries = []
        entries_to_remove = []
        current_entry = []

        for line in entries:
            if line.startswith("dn:") and current_entry:
                # Se la entry corrente è completa, controlla se deve essere rimossa
                if any("dealername:" in entry for entry in current_entry):
                    dealername_value = [entry.split("dealername:")[1].strip() for entry in current_entry if "dealername:" in entry]
                    if any(is_five_digit_number(dn) for dn in dealername_value):
                        entries_to_remove.append("\n".join(current_entry))
                    else:
                        filtered_entries.append("\n".join(current_entry))
                else:
                    filtered_entries.append("\n".join(current_entry))
                current_entry = []
            current_entry.append(line)
        
        # Controlla l'ultima entry
        if current_entry:
            if any("dealername:" in entry for entry in current_entry):
                dealername_value = [entry.split("dealername:")[1].strip() for entry in current_entry if "dealername:" in entry]
                if any(is_five_digit_number(dn) for dn in dealername_value):
                    entries_to_remove.append("\n".join(current_entry))
                else:
                    filtered_entries.append("\n".join(current_entry))
            else:
                filtered_entries.append("\n".join(current_entry))

        num_five_digit_dealername = sum(1 for entry in entries_to_remove)
        num_entries_deleted = num_five_digit_dealername
        logging.info(f"Numero di entry aventi dealername a 5 cifre: {num_five_digit_dealername}")

        # Scrittura delle entry rimanenti nel file di output
        with open(output_file_name, 'w') as output_file:
            for entry in filtered_entries:
                output_file.write(entry + "\n\n")  # Aggiunge una riga vuota tra le entry

        num_remaining_entries = len(filtered_entries)
        logging.info(f"Numero di entry salvate nel file {output_file_name}: {num_remaining_entries}")

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
    input_file_path = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_users_to_import_01.ldif"
    log_file_path = "/mnt/c/temporary/wind/migrationUsersProcedure/exportProcedure.log"

    main(input_file_path, log_file_path, canale)

