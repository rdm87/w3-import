import os
import time
import logging

def setup_logging(log_file_path):
    """Configura il logging."""
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

def main(input_file_path, log_file_path, canale):
    output_file_name = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_parentuid_secondo_livello_list.txt"
    setup_logging(log_file_path)

    start_time = time.time()
    script_name = os.path.basename(__file__)

    # Log dell'inizio dell'esecuzione
    logging.info(f"Start dello script: {script_name}")

    try:
        saved_entries = []
        total_users = 0

        with open(input_file_path, 'r') as input_file:
            current_entry = []
            for line in input_file:
                current_entry.append(line.strip())
                if line.startswith("dn:") and current_entry:
                    # Estrai uid, parentuid e dealername
                    uid = None
                    parentuid = None
                    dealername = None

                    for entry in current_entry:
                        if entry.startswith("uid:"):
                            uid = entry.split("uid:")[1].strip()
                        elif entry.startswith("parentuid:"):
                            parentuid = entry.split("parentuid:")[1].strip()
                        elif entry.startswith("dealername:"):
                            dealername = entry.split("dealername:")[1].strip()

                    # Verifica se parentuid e dealername sono diversi
                    if uid and parentuid and dealername and parentuid != dealername:
                        saved_entries.append(f"uid: {uid}; parentuid: {parentuid}; dealername: {dealername}")
                    
                    total_users += 1
                    current_entry = []
            
            # Controlla l'ultima entry
            if current_entry:
                uid = parentuid = dealername = None

                for entry in current_entry:
                    if entry.startswith("uid:"):
                        uid = entry.split("uid:")[1].strip()
                    elif entry.startswith("parentuid:"):
                        parentuid = entry.split("parentuid:")[1].strip()
                    elif entry.startswith("dealername:"):
                        dealername = entry.split("dealername:")[1].strip()

                if uid and parentuid and dealername and parentuid != dealername:
                    saved_entries.append(f"uid: {uid}; parentuid: {parentuid}; dealername: {dealername}")

                total_users += 1

        # Scrittura delle informazioni salvate nel file di output
        with open(output_file_name, 'w') as output_file:
            for entry in saved_entries:
                output_file.write(entry + "\n")

        num_saved_entries = len(saved_entries)
        logging.info(f"Numero di utenti che hanno parentuid e dealername diversi: {num_saved_entries}")

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
    input_file_path = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_utenti_secondo_livello_FINAL.ldif"
    log_file_path = "/mnt/c/temporary/wind/migrationUsersProcedure/exportProcedure.log"

    main(input_file_path, log_file_path, canale)

