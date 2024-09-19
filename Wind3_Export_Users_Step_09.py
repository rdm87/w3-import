import os
import time
import logging

def setup_logging(log_file_path):
    """Configura il logging."""
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

def is_valid_entry(current_entry):
    """Controlla se l'entry è valida secondo i criteri definiti."""
    dealername = None
    password_expiration_date = None

    for entry in current_entry:
        if entry.startswith("dealername:"):
            dealername = entry.split("dealername:")[1].strip()
        elif entry.startswith("passwordexpirationdate:"):
            password_expiration_date = entry.split("passwordexpirationdate:")[1].strip()

    # Controlla se dealername è numerico a 5 cifre
    if dealername and dealername.isdigit() and len(dealername) == 5:
        return False

    # Controlla se passwordexpirationdate è antecedente al 20240101
    if password_expiration_date and password_expiration_date < "20240101":
        return False

    return True

def main(input_ldif_path, log_file_path, canale):
    valid_output_file_name = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_parentuid_list_FINAL.ldif"
    eliminated_output_file_name = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_parentuid_list_eliminated.ldif"
    setup_logging(log_file_path)

    start_time = time.time()
    script_name = os.path.basename(__file__)

    # Log dell'inizio dell'esecuzione
    logging.info(f"Start dello script: {script_name}")

    try:
        valid_entries = []
        eliminated_entries = []
        
        with open(input_ldif_path, 'r') as ldif_file:
            current_entry = []
            for line in ldif_file:
                current_entry.append(line.strip())
                
                if line.startswith("dn:") and current_entry:
                    # Controlla se l'entry è valida
                    if is_valid_entry(current_entry):
                        valid_entries.append("\n".join(current_entry))
                    else:
                        eliminated_entries.append("\n".join(current_entry))

                    current_entry = []

            # Controlla l'ultima entry
            if current_entry:
                if is_valid_entry(current_entry):
                    valid_entries.append("\n".join(current_entry))
                else:
                    eliminated_entries.append("\n".join(current_entry))

        # Scrittura delle informazioni valide nel file di output
        with open(valid_output_file_name, 'w') as valid_output_file:
            for entry in valid_entries:
                valid_output_file.write(entry + "\n\n")  # Aggiungi una riga vuota tra le entry

        # Scrittura delle informazioni eliminate nel file di output
        with open(eliminated_output_file_name, 'w') as eliminated_output_file:
            for entry in eliminated_entries:
                eliminated_output_file.write(entry + "\n\n")  # Aggiungi una riga vuota tra le entry

        num_valid_entries = len(valid_entries)
        num_eliminated_entries = len(eliminated_entries)
        logging.info(f"Numero di entry valide salvate nel file {valid_output_file_name}: {num_valid_entries}")
        logging.info(f"Numero di entry eliminate salvate nel file {eliminated_output_file_name}: {num_eliminated_entries}")

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
    input_ldif_path = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_parentuid_list.ldif"
    log_file_path = "/mnt/c/temporary/wind/migrationUsersProcedure/exportProcedure.log"

    main(input_ldif_path, log_file_path, canale)

