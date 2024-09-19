import os
import time
import logging

def setup_logging(log_file_path):
    """Configura il logging."""
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

def main(input_file_path, log_file_path, canale):
    output_file_name = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_dealername_utenti_canale_list.txt"
    setup_logging(log_file_path)

    start_time = time.time()
    script_name = os.path.basename(__file__)

    # Log dell'inizio dell'esecuzione
    logging.info(f"Start dello script: {script_name}")

    try:
        dealer_names = set()  # Usa un set per evitare duplicati

        with open(input_file_path, 'r') as input_file:
            entries = input_file.read().splitlines()

            for line in entries:
                if "dealername:" in line:
                    dealername_value = line.split("dealername:")[1].strip()
                    dealer_names.add(dealername_value)

        # Scrittura dei dealername univoci nel file di output
        with open(output_file_name, 'w') as output_file:
            for dealername in sorted(dealer_names):  # Ordina i dealername
                output_file.write(dealername + "\n")

        num_unique_dealer_names = len(dealer_names)
        logging.info(f"Numero di dealername univoci recuperati per il canale {canale}: {num_unique_dealer_names}")

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
    input_file_path = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_users_to_import_FINAL.ldif"
    log_file_path = "/mnt/c/temporary/wind/migrationUsersProcedure/exportProcedure.log"

    main(input_file_path, log_file_path, canale)

