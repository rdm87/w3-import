from datetime import datetime
import time
import logging

# Procedura che recupera tutti i child dei parentuid
# Dizionario 1: Dizionario globale
# Dizionario 2: Dizionario finale degli utenti
# Dizionario 3: Dizionario finale degli utenti di secondo livello
def search_child_for_parent_uid(parent_uid_list,dizionario1,dizionario2,dizionario3,file_name_parentuid_child):
    #print("Sono nella funzione search_parentuid_for_second_level_user")
    logging.debug("Sono nella funzione search_child_for_parent_uid")
    
    dizionario_child_to_filter = {}
    
    logging.debug("Inizio la ricerca dei child nel dizionario che contiene tutti gli utenti")
    for dn, attrs in dizionario1.items():
        logging.debug(f"Controllo se la entry {dn} contiene il parentuid")
        if 'parentuid' in attrs:
            logging.debug(f"la entry {dn} contiene il parentuid")
            logging.debug(f"Verifico se il parentuid {attrs['parentuid']} è presente nella lista dei parentuid")
            if attrs['parentuid'] in parent_uid_list:
                logging.debug(f"Il parent uid {attrs['parentuid']} è presente nella lista dei parent uid")
                logging.debug(f"Verifico se il parent uid {attrs['parentuid']} è già presente nel file degli utenti finale")
                for dn2, attrs2 in dizionario2.items():
                    trovato=False
                    if 'parentuid' in attrs:
                        if dn2 == dn:
                            if attrs2['parentuid'] in parent_uid_list:
                                trovato=True
                                logging.debug(f"L'utente child {dn} già esiste nel file degli utenti finali da importare")
                if trovato == False:
                    for dn3, attrs3 in dizionario3.items():
                        trovato=False
                        if 'parentuid' in attrs:
                            if dn3 == dn:
                                if attrs3['parentuid'] in parent_uid_list:
                                    trovato=True
                                    logging.debug(f"L'utente child {dn} già esiste nel file degli utenti di secondo livello")
                if trovato == False:
                    logging.debug(f"Trovato child da aggiungere al dizionario")
                    dizionario_child_to_filter[dn] = attrs
                    
    logging.debug(f"il numero di child recuperati è {dictionaryCountEntity(dizionario_child_to_filter)}")
    return dizionario_child_to_filter
    
    
    
# Procedura che recupera tutte le entry parentuid
def search_parentuid_global(parent_uid_list,dizionario1,file_name_parentuid_global):
    #print("Sono nella funzione search_parentuid_global")
    logging.debug("Sono nella funzione search_parentuid_global")
    dizionario_parent_uid = {}
    for dn, attrs in dizionario1.items():
        if 'uid' in attrs:
            if attrs['uid'] in parent_uid_list:
                #print(f"trovato il parentuid: {attrs['uid']}")
                logging.debug(f"trovato il parentuid: {attrs['uid']}")
                dizionario_parent_uid[dn] = attrs
                
    return dizionario_parent_uid
    
# Procedura che recupera la lista di parentuid da ricercare nel dizionario globale
def search_parentuid_for_second_level_user(dizionario1,dizionario2,nome_file):
    #print("Sono nella funzione search_parentuid_for_second_level_user")
    logging.debug("Sono nella funzione search_parentuid_for_second_level_user")
    parent_uid_list = []
    parent_uid_list_Alessio = []
    for dn, attrs in dizionario1.items():
        if 'dealername' in attrs and 'parentuid' in attrs:
            if attrs['dealername'] != attrs['parentuid']:
                for dn2, attrs2 in dizionario2.items():
                    if 'canale' in attrs2:
                        if attrs2['uid'] = attrs['parentuid']:
                        parent_uid_list_Alessio.append(f"{dn}|{attrs['dealername']}|{attrs['parentuid']}|{attr2['canale']}")
                if attrs['parentuid'] not in parent_uid_list:
                    parent_uid_list.append(attrs['parentuid'])
    
    write_lists_file(parent_uid_list_Alessio,nome_file)
    for parentuid in parent_uid_list:
        #print(f"parent uid recuperato: {parentuid}")
        logging.debug(f"parent uid recuperato: {parentuid}")
        
    #for dn in parent_uid_list_Alessio:
        #print(f"{dn}")
        
    return parent_uid_list
    
# procedura che cerca gli utenti di secondo livello #
# dizionario 1: lista degli utenti da importare OK: dizionarioUtenti_OK
# dizionario 2: dizionario generale con tutto: dizionarioUtenti
def find_second_level_user(dizionario,dizionario2):
    #print("Sono nella funzione find_second_level_user")
    logging.debug("Sono nella funzione find_second_level_user")
    lista_dealername = []
    diz_utenti_sec_lvl_filt_pwdexpdt = {} # Dizionario che contiene la lista degli utenti di secondo livello che andrà filtrata togliendo la passwordexpirationdate scaduta
    
    for dn, attrs in dizionario.items():
        if 'dealername' in attrs:
            lista_dealername.append(attrs['dealername'])
            
    #for dealername in lista_dealername:
        #print(f"dealername recuperato: {dealername}")
        #print(f"il numero di dealername recuperati è: {len(lista_dealername)}")
        
    for dn, attrs in dizionario2.items():
        isvalid = False
        if 'dealername' in attrs:
            #print("il dealername è presente tra gli attributi dell'utente che si sta controllando")
            if "ou=Utenti secondo livello" in dn:
                #print(f"sto analizzando un dn di un utente di secondo livello: {dn}")
                if attrs['dealername'] in lista_dealername:
                    #print(f"l'utente {dn} è da considerarsi come figlio da salvare")
                    isvalid = True
        if isvalid:
            diz_utenti_sec_lvl_filt_pwdexpdt[dn] = attrs
    
    #print(f"Gli utenti di secondo livello recuperati sono: {dictionaryCountEntity(diz_utenti_sec_lvl_filt_pwdexpdt)}")
    logging.debug(f"Gli utenti di secondo livello recuperati sono: {dictionaryCountEntity(diz_utenti_sec_lvl_filt_pwdexpdt)}")
    return diz_utenti_sec_lvl_filt_pwdexpdt
                    

### dizionario 1 è il dizionario delle sso, dizionario2 è il dizionario degli utenti
def searchEntrySSOPasswordexpired(dizionario1,dizionario2,data):
    #print("Sono nella funzione searchEntrySSOPasswordexpired")
    logging.debug("Sono nella funzione searchEntrySSOPasswordexpired")
    diz_sso_pwd_exp_removed = {}
    diz_users_pwd_exp_removed = {}
    list_sso_to_remove = []
    data_rif = datetime.strptime(data, "%Y%m%d")
    for dn, attrs in dizionario1.items():
        has_passwordexpirationdate = True
        if 'passwordexpirationdate' in attrs:
            for data_check in attrs['passwordexpirationdate']:
                # Assicurati che data_check sia una stringa prima di convertirla
                if isinstance(data_check, str):  # Controlla se è una stringa
                    data_check_dt = datetime.strptime(data_check, "%Y%m%d")  # Converte in datetime
                    if data_check_dt < data_rif:
                        #print(f"il dn del realm da rimuovere è: {dn}")
                        has_passwordexpirationdate = False
                        dnUtente=dn.replace("realm=SSO,", "")
                        list_sso_to_remove.append(dnUtente)
                        #print(f"il dn dell'utente da rimuovere è: {dnUtente}")
                        break  # Esci dal ciclo se trovi una data scaduta
        if has_passwordexpirationdate:
                diz_sso_pwd_exp_removed[dn]=attrs
                
    for dn, attrs in dizionario2.items():
        has_valid_passwordexpirationdate = True
        if dn in list_sso_to_remove:
            has_valid_passwordexpirationdate = False
        if has_valid_passwordexpirationdate:
            diz_users_pwd_exp_removed[dn] = attrs
        
    #print(f"il numero di utenti dopo la cancellazione delle passwordxepirationdate è: {dictionaryCountEntity(diz_users_pwd_exp_removed)}")
    logging.debug(f"il numero di utenti dopo la cancellazione delle passwordxepirationdate è: {dictionaryCountEntity(diz_users_pwd_exp_removed)}")
    return diz_sso_pwd_exp_removed,diz_users_pwd_exp_removed

def searchEntrySSO(dizionario, dizionarioGlobale):
    diz_sso_entry = {}
    #print("Sono nella funzione searchEntrySSO")
    logging.debug("Sono nella funzione searchEntrySSO")
    for dn, attrs in dizionario.items():
        dnSSO="realm=SSO,"+dn
        dnSSO_lower="realm=sso,"+dn
        for dn2, attrs2 in dizionarioGlobale.items():
            has_valid_sso=False
            if dnSSO == dn2:
                #print(f"la entry ricercata è {dnSSO} --> la entry trovata è {dn2}")
                has_valid_sso = True
            else:
                if dnSSO_lower == dn2:
                    #print(f"la entry ricercata è {dnSSO_lower} --> la entry trovata è {dn2}")
                    has_valid_sso = True
            if has_valid_sso:
                diz_sso_entry[dnSSO] = attrs2
        
    
    return diz_sso_entry
    
#Funzione che elimina gli utenti con passwordexpirationdate
def remove_passwordexpirationdate_user(dizionario,data):
    #print("Sono nella funzione remove_passwordexpirationdate_user")
    logging.info("Sono nella funzione remove_passwordexpirationdate_user")
    
    logging.info("Inizializzo il dizionario che sarà ritornato dalla funzione")
    diz_passwd_exp_delete = {}
    
    logging.info("Converto la data da controllare in formato date")
    data_rif = datetime.strptime(data, "%Y%m%d")
    
    logging.info("Inizio analisi del dizionario da controllare")
    for dn, attrs in dizionario.items():
        has_valid_passwordexpirationdate = True
        if 'passwordexpirationdate' in attrs:
            logging.debug("Recupero tutte le date del dizionario")
            for data_check in attrs['passwordexpirationdate']:
                # Assicurati che data_check sia una stringa prima di convertirla
                logging.debug("Controllo se la data è una stringa")
                if isinstance(data_check, str):  # Controlla se è una stringa
                    logging.debug("Converto la data in formato date")
                    data_check_dt = datetime.strptime(data_check, "%Y%m%d")  # Converte in datetime
                    if data_check_dt < data_rif:
                        logging.debug("la data è antecedente al giorno 01/01/2024")
                        has_valid_passwordexpirationdate = False
                        break  # Esci dal ciclo se trovi una data scaduta
        if has_valid_passwordexpirationdate:
                logging.debug(f"Inserisco nel dizionario da restituire l'utente che ha la data corretta: {dn}")
                diz_passwd_exp_delete[dn] = attrs
            
    logging.info("ritorno il dizionario con gli utenti che hanno data corretta")
    return diz_passwd_exp_delete
               

#Funzione che conta il numero di entry all'interno di un dizionario
def dictionaryCountEntity (dizionario):
    #print("Sono nella funzione dictionaryCountEntity")
    logging.debug("Sono nella funzione dictionaryCountEntity")
    return len(dizionario)
    
def write_lists_file (lista,nome_file):
    #print("Sono nella funzione write_lists_file")
    logging.debug("Sono nella funzione write_lists_file")
    with open(nome_file, 'w') as f:
        f.write(f"DN|DEALERNAME|PARENTUID\n")
        for row in lista:
            f.write(f"{row}\n")
    #print(f"Creato il file {nome_file}")
    logging.debug(f"Creato il file {nome_file}")

#Funzione che scrive in formato ldif il contenuto di un dizionario
def scrivi_ldif(dizionario, nome_file):
    #print("Sono nella funzione scrivi_ldif")
    logging.debug("Sono nella funzione scrivi_ldif")
    with open(nome_file, 'w') as f:
        for dn, attrs in dizionario.items():
            f.write(f"dn: {dn}\n")  # Scrivi il DN
            for key, values in attrs.items():
                if key != 'dn':  # Salta il DN poiché è già scritto
                    for value in values:
                        f.write(f"{key}: {value}\n")  # Scrivi ogni attributo
            f.write("\n")  # Aggiungi una riga vuota tra le entry
    
    #print(f"Creato il file {nome_file}")
    logging.debug(f"Creato il file {nome_file}")

#Funzione che estrae tutte le entity appartenenti ad un canale e le salva in un file ldif
def list_users_for_channel(diz_user_5_digit_dealer_name_removed,canale):
    #print("Sono nella funzione list_users_for_channel")
    logging.debug("Sono nella funzione list_users_for_channel")
    utenti_con_canale = {}
    for dn, attrs in diz_user_5_digit_dealer_name_removed.items():
        if 'canale' in attrs:
            # Controlla se uno dei valori dell'attributo 'canale' è uguale a canale
            if any(value == canale for value in attrs['canale']):
                utenti_con_canale[dn] = attrs
    
    return utenti_con_canale
            

# Funzione che elimina i dealername a 5 cifre dalla lista degli utenti totali
def remove_all_user_with_dealername_5_number(dizionarioLdapEntry,canale):
    dealernameCount=0
    diz_user_5_digit_dealer_name_removed = {}
    #print("Sono nella funzione di rimozione degli utenti aventi dealername a 5 cifre")
    logging.debug("Sono nella funzione di rimozione degli utenti aventi dealername a 5 cifre")
    for dn, attrs in dizionarioLdapEntry.items():
        has_valid_dealername = True
        if 'dealername' in attrs:
            for dealername in attrs['dealername']:
                if dealername.isdigit() and len(dealername) == 5:
                    dealernameCount+=1
                    has_valid_dealername = False
                    #print(f"Per il DN {dn} il dealername è: {dealername}")
        
        if has_valid_dealername:
                diz_user_5_digit_dealer_name_removed[dn] = attrs
                
                    
    #print(f"il numero di utenti che hanno dealername a 5 cifre è: {dealernameCount}")
    logging.debug(f"il numero di utenti che hanno dealername a 5 cifre è: {dealernameCount}")
    #print(f"Il numero di elementi nel dizionario aggiornato senza i dealername a 5 cifre è: {dictionaryCountEntity(diz_user_5_digit_dealer_name_removed)}")
    logging.debug(f"Il numero di elementi nel dizionario aggiornato senza i dealername a 5 cifre è: {dictionaryCountEntity(diz_user_5_digit_dealer_name_removed)}")
    return diz_user_5_digit_dealer_name_removed

#Funzione che effettua il parse del file di input contenenti tutte le entry ldap di OID
def parse_ldif(file_path):
    #print("Sono nella funzione parse_ldif")
    logging.debug("Sono nella funzione parse_ldif")
    dizionarioLdapEntry = {}  # Dizionario per memorizzare le entry
    with open(file_path, 'r') as f:
        entry = {}
        for line in f:
            line = line.strip()
            if line.startswith('dn:'):
                if entry:  # Se ci sono già dati salvati, aggiungi al dizionario
                    dizionarioLdapEntry[entry['dn']] = entry  # La chiave è il DN, il valore è l'intera entry
                entry = {'dn': line[4:].strip()}  # Inizia una nuova entry
            elif line and ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                entry.setdefault(key, []).append(value)
        if entry:  # Aggiungi l'ultima entry al dizionario
            dizionarioLdapEntry[entry['dn']] = entry
            #elementsNumber=len(dizionarioLdapEntry)
            #print(f"Il numero di elementi nel dizionario iniziale è: {dictionaryCountEntity(dizionarioLdapEntry)}")
            logging.debug(f"Il numero di elementi nel dizionario iniziale è: {dictionaryCountEntity(dizionarioLdapEntry)}")
    return dizionarioLdapEntry
    
    
def print_dictionary(dizionario):
    for dn, attrs in dizionario.items():
        for key, values in attrs.items():
            if key != 'dn':
                print(f'  {key}: {values}')

def activate_logging():
    logging.basicConfig(filename='/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_UserMigrationProcedure.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

activate_logging()
start_time = time.time() #Setto l'orario di start
logging.info("Inizio procedura di creazione file per migrazione utenti")

canale = "PP" #Assegno il canale da controllare

# Percorso del file LDIF
### STEP 0 - PARSO IL FILE DEGLI UTENTI ESTRATTO DA OID PER CONVERTIRLO IN UNA STRUTTURA DATI DA ANALIZZARE ###
print("STEP 0 - PARSO IL FILE DEGLI UTENTI ESTRATTO DA OID PER CONVERTIRLO IN UNA STRUTTURA DATI DA ANALIZZARE")
logging.info("STEP 0 - PARSO IL FILE DEGLI UTENTI ESTRATTO DA OID PER CONVERTIRLO IN UNA STRUTTURA DATI DA ANALIZZARE")
file_path = '/mnt/c/temporary/wind/migrationUsersProcedure/o=pos.wind.it.ldif' #File di input nel quale sono presenti tutti gli utenti esportati da OID
dizionarioUtenti = parse_ldif(file_path) #Creo un dizionario che contiene tutti gli utenti

### STEP 1 - Rimuovo tutte le entry che hanno il dealername di cinque cifre ###
print("STEP 1 - Rimuovo tutte le entry che hanno il dealername di cinque cifre")
logging.info("STEP 1: Rimuovo tutte le entry che hanno il dealername di cinque cifre")
diz_user_5_digit_dealer_name_removed=remove_all_user_with_dealername_5_number(dizionarioUtenti,canale) #Creo un dizionario senza gli utenti aventi dealername a 5 cifre

### STEP 2 - RECUPERO TUTTE LE ENTRY DEL CANALE DI INPUT ###
print("STEP 2 - RECUPERO TUTTE LE ENTRY DEL CANALE DI INPUT")
logging.info("STEP 2: RECUPERO TUTTE LE ENTRY DEL CANALE DI INPUT")
user_for_channel=list_users_for_channel(diz_user_5_digit_dealer_name_removed,canale) #creo il dizionario con gli utenti appartenenti al canale di input
#print(f"il numero di utenti appartenenti al canale {canale} è: {dictionaryCountEntity(user_for_channel)}")
logging.debug(f"il numero di utenti appartenenti al canale {canale} è: {dictionaryCountEntity(user_for_channel)}")

### STEP 3 - SALVO TUTTI GLI UTENTI APPARTENENTI AD UN CANALE ALL'INTERNO DI UN FILE .LDIF ###
print("STEP 3 - SALVO TUTTI GLI UTENTI APPARTENENTI AD UN CANALE ALL'INTERNO DI UN FILE .LDIF ")
logging.info("STEP 3: SALVO TUTTI GLI UTENTI APPARTENENTI AD UN CANALE ALL'INTERNO DI UN FILE .LDIF ")
file_name_users_channel = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_UsersForChannelWithPasswordExpirationToChange.ldif" #percorso del file che salva tutti gli utenti appartenenti ad un determinato canale
scrivi_ldif(user_for_channel, file_name_users_channel) # Scrivo il file in formato ldif, con tutti gli utenti appartenenti ad un canale

### STEP 4 - ELIMINO DAL FILE DEGLI UTENTI APPARTENENTI AL CANALE TUTTE LE ENTITY CHE HANNO PASSWORD EXPIRATION DATE VECCHIA ###
print("STEP 4 - ELIMINO DAL FILE DEGLI UTENTI APPARTENENTI AL CANALE TUTTE LE ENTITY CHE HANNO PASSWORD EXPIRATION DATE VECCHIA")
logging.info("STEP 4: ELIMINO DAL FILE DEGLI UTENTI APPARTENENTI AL CANALE TUTTE LE ENTITY CHE HANNO PASSWORD EXPIRATION DATE VECCHIA")
file_name_user_channel_without_password = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_UsersForChannelWithoutPasswordExpirationToChange.ldif"
diz_passwd_exp_delete=remove_passwordexpirationdate_user(user_for_channel,"20240101") # Creo il dizionario senza le passwordexpirationdate vecchie
scrivi_ldif(diz_passwd_exp_delete, file_name_user_channel_without_password) # Scrivo il file in formato ldif
#print(f"il numero di utenti appartenenti al canale {canale} dopo la rimozione delle entry con passwordexpirationdate vecchia è: è: {dictionaryCountEntity(diz_passwd_exp_delete)}")
logging.debug(f"il numero di utenti appartenenti al canale {canale} dopo la rimozione delle entry con passwordexpirationdate vecchia è: {dictionaryCountEntity(diz_passwd_exp_delete)}")

### STEP 5 - RECUPERO TUTTE LE ENTRY DI TIPO realm=SSO DAL FILE PRINCIPALE
print("STEP 5 - RECUPERO TUTTE LE ENTRY DI TIPO realm=SSO DAL FILE PRINCIPALE")
logging.info("STEP 5: RECUPERO TUTTE LE ENTRY DI TIPO realm=SSO DAL FILE PRINCIPALE")
dizionario_sso=searchEntrySSO(diz_passwd_exp_delete, dizionarioUtenti)
file_name_sso = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_UsersChannellSSOToParse.ldif"
scrivi_ldif(dizionario_sso, file_name_sso) # Scrivo il file in formato ldif

### STEP 6 - RIMUOVO LE ENTRY SSO E GLI UTENTI ASSOCIATI CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024
print("STEP 6 - RIMUOVO LE ENTRY SSO E GLI UTENTI ASSOCIATI CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024")
logging.info("STEP 6: RIMUOVO LE ENTRY SSO E GLI UTENTI ASSOCIATI CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024")
dizionario_utenti_sso_OK,dizionarioUtenti_OK=searchEntrySSOPasswordexpired(dizionario_sso,diz_passwd_exp_delete,"20240101")
file_name_dizionario_utenti_sso_OK = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_UtentiSSO_FINAL.ldif"
scrivi_ldif(dizionario_utenti_sso_OK, file_name_dizionario_utenti_sso_OK) # Scrivo il file in formato ldif
file_name_dizionario_utenti_OK = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_Utenti_FINAL.ldif"
scrivi_ldif(dizionarioUtenti_OK, file_name_dizionario_utenti_OK) # Scrivo il file in formato ldif

### STEP 7 - CERCO GLI UTENTI DI SECONDO LIVELLO PARTENDO DAI DEALERNAME ###
print("STEP 7 - CERCO GLI UTENTI DI SECONDO LIVELLO PARTENDO DAI DEALERNAME")
logging.info("STEP 7: CERCO GLI UTENTI DI SECONDO LIVELLO PARTENDO DAI DEALERNAME")
dizionario_utenti_secondo_livello_da_filtrare=find_second_level_user(dizionarioUtenti_OK,dizionarioUtenti)
file_name_dizionario_dizionario_utenti_secondo_livello_da_filtrare = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_Utenti_Secondo_Livello_Da_Filtrare.ldif"
scrivi_ldif(dizionario_utenti_secondo_livello_da_filtrare, file_name_dizionario_dizionario_utenti_secondo_livello_da_filtrare) # Scrivo il file in formato ldif

### STEP 8 - RIMUOVO LE ENTRY DI SECONDO LIVELLO CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024 ###
print("STEP 8 - RIMUOVO LE ENTRY DI SECONDO LIVELLO CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024")
logging.info("STEP 8: RIMUOVO LE ENTRY DI SECONDO LIVELLO CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024")
dizionario_utenti_secondo_livello_expiration_date_rimosse=remove_passwordexpirationdate_user(dizionario_utenti_secondo_livello_da_filtrare,"20240101")
file_name_dizionario_utenti_secondo_livello_expiration_date_rimosse=f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_Utenti_Secondo_Livello_No_Expiration_Date.ldif"
scrivi_ldif(dizionario_utenti_secondo_livello_expiration_date_rimosse, file_name_dizionario_utenti_secondo_livello_expiration_date_rimosse) # Scrivo il file in formato ldif

#### STEP 9 - RECUPERO TUTTE LE ENTRY DI TIPO REALM=SSO, PER GLI UTENTI DI SECONDO LIVELLO, DAL FILE PRINCIPALE ###
#print("STEP 9 - RECUPERO TUTTE LE ENTRY DI TIPO REALM=SSO, PER GLI UTENTI DI SECONDO LIVELLO, DAL FILE PRINCIPALE")
#logging.info("STEP 9: RECUPERO TUTTE LE ENTRY DI TIPO REALM=SSO, PER GLI UTENTI DI SECONDO LIVELLO, DAL FILE PRINCIPALE")
#dizionario_utenti_secondo_livello_sso=searchEntrySSO(dizionario_utenti_secondo_livello_expiration_date_rimosse, dizionarioUtenti)
#file_name_utenti_secondo_livello_sso = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_Utenti_Secondo_Livello_SSO_No_Expiration_Date.ldif"
#scrivi_ldif(dizionario_utenti_secondo_livello_sso, file_name_utenti_secondo_livello_sso) # Scrivo il file in formato ldif

### STEP 10 - RECUPERO LA LISTA DEI PARENT UID DEGLI UTENTI DI SECONDO LIVELLO ###
print("STEP 10 - RECUPERO LA LISTA DEI PARENT UID DEGLI UTENTI DI SECONDO LIVELLO")
logging.info("STEP 10: RECUPERO LA LISTA DEI PARENT UID DEGLI UTENTI DI SECONDO LIVELLO")
file_name_lista_parentuid_alessio=f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_parentuid_lists.txt"
parent_uid_list=search_parentuid_for_second_level_user(dizionario_utenti_secondo_livello_expiration_date_rimosse,dizionarioUtenti,file_name_lista_parentuid_alessio)

### STEP 11 - RECUPERO LE ENTRY DEI PARENTUID DAL FILE PRINCIPALE ###
print("STEP 11 - RECUPERO LE ENTRY DEI PARENTUID DAL FILE PRINCIPALE")
logging.info("STEP 11: RECUPERO LE ENTRY DEI PARENTUID DAL FILE PRINCIPALE")
file_name_parentuid_global=f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_parentuid_FINAL.txt"
dizionario_parentuid=search_parentuid_global(parent_uid_list,dizionarioUtenti,file_name_parentuid_global)
scrivi_ldif(dizionario_parentuid, file_name_parentuid_global) # Scrivo il file in formato ldif

### STEP 12 - RECUPERO LE ENTRY CHILD DEI PARENT UID ###
print("STEP 12: RECUPERO LE ENTRY CHILD DEI PARENT UID")
logging.info("STEP 12: RECUPERO LE ENTRY CHILD DEI PARENT UID")
file_name_parentuid_child=f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_parentuid_child_to_parse.txt"
dizionario_child_to_filter=search_child_for_parent_uid(parent_uid_list,dizionarioUtenti,dizionarioUtenti_OK,dizionario_utenti_secondo_livello_expiration_date_rimosse,file_name_parentuid_child)
scrivi_ldif(dizionario_child_to_filter, file_name_parentuid_child) # Scrivo il file in formato ldif

### STEP 13 - RIMUOVO LE ENTRY CHILD CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024 ###
print("STEP 13 - RIMUOVO LE ENTRY CHILD CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024")
logging.info("STEP 13: RIMUOVO LE ENTRY CHILD CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024")
dizionario_child_filtered_password_expirationdate=remove_passwordexpirationdate_user(dizionario_child_to_filter,"20240101")
file_name_dizionario_utenti_secondo_livello_expiration_date_rimosse=f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_parentuid_child_exiprationdate_removed.txt"
scrivi_ldif(dizionario_child_filtered_password_expirationdate, file_name_dizionario_utenti_secondo_livello_expiration_date_rimosse) # Scrivo il file in formato ldif

### STEP 14 - RECUPERO TUTTE LE ENTRY DI TIPO realm=SSO DAL FILE PRINCIPALE PER GLI UTENTI CHILD DEI PARENTUID
print("STEP 14 - RECUPERO TUTTE LE ENTRY DI TIPO realm=SSO DAL FILE PRINCIPALE PER GLI UTENTI CHILD DEI PARENTUID")
logging.info("STEP 14: RECUPERO TUTTE LE ENTRY DI TIPO realm=SSO DAL FILE PRINCIPALE PER GLI UTENTI CHILD DEI PARENTUID")
dizionario_child_sso=searchEntrySSO(dizionario_child_filtered_password_expirationdate, dizionarioUtenti)
file_name_child_sso = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_UserChildSSO_to_parse.ldif"
scrivi_ldif(dizionario_child_sso, file_name_child_sso) # Scrivo il file in formato ldif

### STEP 15 - RIMUOVO LE ENTRY SSO E GLI UTENTI ASSOCIATI CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024
print("STEP 15 - RIMUOVO LE ENTRY SSO E GLI UTENTI ASSOCIATI CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024")
logging.info("STEP 15: RIMUOVO LE ENTRY SSO E GLI UTENTI ASSOCIATI CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024")
dizionario_child_sso_OK,dizionario_child_OK=searchEntrySSOPasswordexpired(dizionario_child_sso,dizionario_child_filtered_password_expirationdate,"20240101")
file_name_dizionario_child_sso_OK = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_Utenti_child_SSO_FINAL.ldif"
scrivi_ldif(dizionario_child_sso_OK, file_name_dizionario_child_sso_OK) # Scrivo il file in formato ldif
file_name_child_OK = f"/mnt/c/temporary/wind/migrationUsersProcedure/{canale}_Utenti_child_FINAL.ldif"
scrivi_ldif(dizionario_child_OK, file_name_child_OK) # Scrivo il file in formato ldif

end_time = time.time() # Calcolo l'orario di fine
execution_time = end_time - start_time # Tempo di esecuzione totale
minutes = execution_time // 60  # Divisione intera per ottenere i minuti
seconds = execution_time % 60    # Resto della divisione per ottenere i secondi
print(f"Tempo di esecuzione: {int(minutes)} minuti e {int(seconds)} secondi")
logging.info(f"Tempo di esecuzione: {int(minutes)} minuti e {int(seconds)} secondi")
#print(f"Tempo di esecuzione: {int(minutes)} minuti e {seconds:.6f} secondi")