from datetime import datetime
import time
import logging
import sys

# Procedura che recupera tutti i child dei parentuid
# Dizionario 1: Dizionario globale
# Dizionario 2: Dizionario finale degli utenti
# Dizionario 3: Dizionario finale degli utenti di secondo livello
def search_child_for_parent_uid(listParentuidSecondoLivello,dizionario1,dizionario2,dizionario3,file_name_parentuid_child):
    #print("Sono nella funzione search_parentuid_for_second_level_user")
    logging.debug("Sono nella funzione search_child_for_parent_uid")
    
    dizionario_child_to_filter = {}
    
    logging.debug("Inizio la ricerca dei child nel dizionario che contiene tutti gli utenti")
    for dn, attrs in dizionario1.items():
        logging.debug(f"Controllo se la entry {dn} contiene il parentuid")
        if 'parentuid' in attrs:
            logging.debug(f"la entry {dn} contiene il parentuid")
            logging.debug(f"Verifico se il parentuid {attrs['parentuid']} è presente nella lista dei parentuid")
            if attrs['parentuid'] in listParentuidSecondoLivello:
                logging.debug(f"Il parent uid {attrs['parentuid']} è presente nella lista dei parent uid")
                logging.debug(f"Verifico se il parent uid {attrs['parentuid']} è già presente nel file degli utenti finale")
                for dn2, attrs2 in dizionario2.items():
                    trovato=False
                    if 'parentuid' in attrs:
                        if dn2 == dn:
                            if attrs2['parentuid'] in listParentuidSecondoLivello:
                                trovato=True
                                logging.debug(f"L'utente child {dn} già esiste nel file degli utenti finali da importare")
                if trovato == False:
                    for dn3, attrs3 in dizionario3.items():
                        trovato=False
                        if 'parentuid' in attrs:
                            if dn3 == dn:
                                if attrs3['parentuid'] in listParentuidSecondoLivello:
                                    trovato=True
                                    logging.debug(f"L'utente child {dn} già esiste nel file degli utenti di secondo livello")
                if trovato == False:
                    logging.debug(f"Trovato child da aggiungere al dizionario")
                    dizionario_child_to_filter[dn] = attrs
                    
    logging.debug(f"il numero di child recuperati è {dictionaryCountEntity(dizionario_child_to_filter)}")
    return dizionario_child_to_filter
    
    
    
# Procedura che recupera tutte le entry parentuid
def search_parentuid_global(listParentuidSecondoLivello,dizionario1):
    #print("Sono nella funzione search_parentuid_global")
    logging.debug("Sono nella funzione search_parentuid_global")
    dizionario_parent_uid = {}
    for dn, attrs in dizionario1.items():
        if 'uid' in attrs:
            if attrs['uid'] in listParentuidSecondoLivello:
                #print(f"trovato il parentuid: {attrs['uid']}")
                logging.debug(f"trovato il parentuid: {attrs['uid']}")
                dizionario_parent_uid[dn] = attrs
                
    return dizionario_parent_uid
    
# Procedura che recupera la lista di parentuid da ricercare nel dizionario globale
def search_parentuid_for_second_level_user(dizionario1,dizionario2):
    #print("Sono nella funzione search_parentuid_for_second_level_user")
    logging.debug("Sono nella funzione search_parentuid_for_second_level_user")
    listParentuidSecondoLivello = []
    for dn, attrs in dizionario1.items():
        if 'dealername' in attrs and 'parentuid' in attrs:
            if attrs['dealername'] != attrs['parentuid']:
                if attrs['parentuid'] not in listParentuidSecondoLivello:
                    listParentuidSecondoLivello.append(attrs['parentuid'])   
                        
    return listParentuidSecondoLivello
    
# procedura che cerca gli utenti di secondo livello #
# dizionario 1: lista degli utenti da importare OK: dizionarioUtentiCanaleFinal
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
    logging.info("Sono nella funzione searchEntrySSO")
    for dn, attrs in dizionario.items():
        dnSSO="realm=SSO,"+dn
        dnSSO_lower="realm=sso,"+dn
        for dn2, attrs2 in dizionarioGlobale.items():
            has_valid_sso=False
            if dnSSO == dn2:
                has_valid_sso = True
            else:
                if dnSSO_lower == dn2:
                    has_valid_sso = True
            if has_valid_sso:
                diz_sso_entry[dnSSO] = attrs2
        
    
    return diz_sso_entry
    
#Funzione che elimina gli utenti con passwordexpirationdate
def remove_passwordexpirationdate_user(dizionario,data):
    logging.info("Sono nella funzione remove_passwordexpirationdate_user")
    
    logging.info("Inizializzo il dizionario che sarà ritornato dalla funzione")
    dizionarioUtentiCanaleNoPasswordExpirationDate = {}
    
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
                dizionarioUtentiCanaleNoPasswordExpirationDate[dn] = attrs
            
    logging.info("ritorno il dizionario con gli utenti che hanno data corretta")
    return dizionarioUtentiCanaleNoPasswordExpirationDate
               

#Funzione che conta il numero di entry all'interno di un dizionario
def dictionaryCountEntity (dizionario):
    logging.debug("Sono nella funzione dictionaryCountEntity")
    return len(dizionario)
    
def write_lists_file (lista,nome_file):
    #print("Sono nella funzione write_lists_file")
    logging.debug("Sono nella funzione write_lists_file")
    with open(nome_file, 'w') as f:
        f.write(f"DN|DEALERNAME|PARENTUID\n")
        for row in lista:
            f.write(f"{row}\n")
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
def searchUserForChannel(diz_user_5_digit_dealer_name_removed,canale):
    #print("Sono nella funzione searchUserForChannel")
    logging.info("Sono nella funzione searchUserForChannel")
    utenti_con_canale = {}
    for dn, attrs in diz_user_5_digit_dealer_name_removed.items():
        if 'canale' in attrs:
            # Controlla se uno dei valori dell'attributo 'canale' è uguale a canale
            if any(value == canale for value in attrs['canale']):
                utenti_con_canale[dn] = attrs
    
    return utenti_con_canale
            

# Funzione che elimina i dealername a 5 cifre dalla lista degli utenti totali
def removeAllUserWithDealername5Digit(dizionarioUtenti,canale):
    logging.info("Sono nella funzione removeAllUserWithDealername5Digit")
    dealernameCount=0
    dizionarioUtentiNoDealername5Digit = {}
    logging.debug("Sono nella funzione di rimozione degli utenti aventi dealername a 5 cifre")
    for dn, attrs in dizionarioUtenti.items():
        has_valid_dealername = True
        if 'dealername' in attrs:
            for dealername in attrs['dealername']:
                if dealername.isdigit() and len(dealername) == 5:
                    logging.debug(f"il dealername: {dealername} ha cinque cifre")
                    dealernameCount+=1
                    has_valid_dealername = False
        
        if has_valid_dealername:
                dizionarioUtentiNoDealername5Digit[dn] = attrs
                
    logging.info(f"il numero di utenti che hanno dealername a 5 cifre è: {dealernameCount}")
    logging.info(f"Il numero di elementi nel dizionario aggiornato senza i dealername a 5 cifre è: {dictionaryCountEntity(dizionarioUtentiNoDealername5Digit)}")
    return dizionarioUtentiNoDealername5Digit

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

def activate_logging(canale):
    logging.basicConfig(filename=f'{pathExportFile}/{canale}_UserMigrationProcedure.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

if len(sys.argv) > 3:
    canale = sys.argv[1] #Assegno il canale da controllare
    pathExportFile = sys.argv[2] # Assegno il percorso dove salvare i file di output
    pathImportFile = sys.argv[3] # Assegno il percorso del file di input dal quale leggere gli utenti

activate_logging(canale)
start_time = time.time() #Setto l'orario di start
logging.info("Inizio procedura di creazione file per migrazione utenti")



# Percorso del file LDIF
### STEP 0 - PARSO IL FILE DEGLI UTENTI ESTRATTO DA OID PER CONVERTIRLO IN UNA STRUTTURA DATI DA ANALIZZARE ###
logging.info("STEP 0 - PARSO IL FILE DEGLI UTENTI ESTRATTO DA OID PER CONVERTIRLO IN UNA STRUTTURA DATI DA ANALIZZARE")
file_path = pathImportFile #File di input nel quale sono presenti tutti gli utenti esportati da OID
dizionarioUtenti = parse_ldif(file_path) #Creo un dizionario che contiene tutti gli utenti

### STEP 1 - Rimuovo tutte le entry che hanno il dealername di cinque cifre ###
logging.info("STEP 1: Rimuovo tutte le entry che hanno il dealername di cinque cifre")
dizionarioUtentiNoDealername5Digit=removeAllUserWithDealername5Digit(dizionarioUtenti,canale) #Creo un dizionario senza gli utenti aventi dealername a 5 cifre

### STEP 2 - RECUPERO TUTTE LE ENTRY DEL CANALE DI INPUT ###
logging.info("STEP 2: RECUPERO TUTTE LE ENTRY DEL CANALE DI INPUT")
dizionarioUtentiCanale=searchUserForChannel(dizionarioUtentiNoDealername5Digit,canale) #creo il dizionario con gli utenti appartenenti al canale di input
logging.info(f"il numero di utenti appartenenti al canale {canale} è: {dictionaryCountEntity(dizionarioUtentiCanale)}")

### STEP 3 - SALVO TUTTI GLI UTENTI APPARTENENTI AD UN CANALE ALL'INTERNO DI UN FILE .LDIF ###
logging.info("STEP 3: SALVO TUTTI GLI UTENTI APPARTENENTI AD UN CANALE ALL'INTERNO DI UN FILE .LDIF ")
fileNameUtentiCanalePasswordExpirationDate = f"{pathExportFile}/{canale}_UtentiCanalePasswordExpiration.ldif" #percorso del file che salva tutti gli utenti appartenenti ad un determinato canale
scrivi_ldif(dizionarioUtentiCanale, fileNameUtentiCanalePasswordExpirationDate) # Scrivo il file in formato ldif, con tutti gli utenti appartenenti ad un canale
logging.info(f"E' stato creato il file {fileNameUtentiCanalePasswordExpirationDate}")

### STEP 4 - ELIMINO DAL FILE DEGLI UTENTI APPARTENENTI AL CANALE TUTTE LE ENTITY CHE HANNO PASSWORD EXPIRATION DATE VECCHIA ###
logging.info("STEP 4: ELIMINO DAL FILE DEGLI UTENTI APPARTENENTI AL CANALE TUTTE LE ENTITY CHE HANNO PASSWORD EXPIRATION DATE VECCHIA")
fileNameUtentiCanaleNoPasswordExpirationDate = f"{pathExportFile}/{canale}_UtentiCanaleNoPasswordExpiration.ldif"
dizionarioUtentiCanaleNoPasswordExpirationDate=remove_passwordexpirationdate_user(dizionarioUtentiCanale,"20240101") # Creo il dizionario senza le passwordexpirationdate vecchie
scrivi_ldif(dizionarioUtentiCanaleNoPasswordExpirationDate, fileNameUtentiCanaleNoPasswordExpirationDate) # Scrivo il file in formato ldif
logging.info(f"il numero di utenti appartenenti al canale {canale} dopo la rimozione delle entry con passwordexpirationdate vecchia è: {dictionaryCountEntity(dizionarioUtentiCanaleNoPasswordExpirationDate)}")

### STEP 5 - RECUPERO TUTTE LE ENTRY DI TIPO realm=SSO DAL FILE PRINCIPALE
logging.info("STEP 5: RECUPERO TUTTE LE ENTRY DI TIPO realm=SSO DAL FILE PRINCIPALE")
dizionarioUtentiCanaleSSO=searchEntrySSO(dizionarioUtentiCanaleNoPasswordExpirationDate, dizionarioUtenti)
fileNameUtentiCanaleSSO = f"{pathExportFile}/{canale}_UtentiCanaleSSOPasswordExpirationDate.ldif.ldif"
scrivi_ldif(dizionarioUtentiCanaleSSO, fileNameUtentiCanaleSSO) # Scrivo il file in formato ldif

### STEP 6 - RIMUOVO LE ENTRY SSO E GLI UTENTI ASSOCIATI CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024
logging.info("STEP 6: RIMUOVO LE ENTRY SSO E GLI UTENTI ASSOCIATI CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024")
dizionarioUtentiCanaleSSOFinal,dizionarioUtentiCanaleFinal=searchEntrySSOPasswordexpired(dizionarioUtentiCanaleSSO,dizionarioUtentiCanaleNoPasswordExpirationDate,"20240101")
fileNamedizionarioUtentiCanaleSSOFinal = f"{pathExportFile}/{canale}_02_UtentiCanaleSSO_FINAL.ldif"
scrivi_ldif(dizionarioUtentiCanaleSSOFinal, fileNamedizionarioUtentiCanaleSSOFinal) # Scrivo il file in formato ldif
fileNameDizionarioUtentiCanaleFinal = f"{pathExportFile}/{canale}_01_UtentiCanale_FINAL.ldif"
scrivi_ldif(dizionarioUtentiCanaleFinal, fileNameDizionarioUtentiCanaleFinal) # Scrivo il file in formato ldif

### STEP 7 - CERCO GLI UTENTI DI SECONDO LIVELLO PARTENDO DAI DEALERNAME ###
logging.info("STEP 7: CERCO GLI UTENTI DI SECONDO LIVELLO PARTENDO DAI DEALERNAME")
dizionarioUtentiSecondoLivelloPasswordExpirationDate=find_second_level_user(dizionarioUtentiCanaleFinal,dizionarioUtenti)
fileNameDizionarioUtentiSecondoLivelloPasswordExpirationDate = f"{pathExportFile}/{canale}_Utenti_Secondo_Livello_Da_Filtrare.ldif"
scrivi_ldif(dizionarioUtentiSecondoLivelloPasswordExpirationDate, fileNameDizionarioUtentiSecondoLivelloPasswordExpirationDate) # Scrivo il file in formato ldif

### STEP 8 - RIMUOVO LE ENTRY DI SECONDO LIVELLO CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024 ###
logging.info("STEP 8: RIMUOVO LE ENTRY DI SECONDO LIVELLO CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024")
dizionarioUtentiSecondoLivelloFinal=remove_passwordexpirationdate_user(dizionarioUtentiSecondoLivelloPasswordExpirationDate,"20240101")
fileNameDizionarioUtentiSecondoLivelloFinal=f"{pathExportFile}/{canale}_03_UtentiSecondoLivello_FINAL.ldif"
scrivi_ldif(dizionarioUtentiSecondoLivelloFinal, fileNameDizionarioUtentiSecondoLivelloFinal) # Scrivo il file in formato ldif

#### STEP 9 - RECUPERO TUTTE LE ENTRY DI TIPO REALM=SSO, PER GLI UTENTI DI SECONDO LIVELLO, DAL FILE PRINCIPALE ###
#print("STEP 9 - RECUPERO TUTTE LE ENTRY DI TIPO REALM=SSO, PER GLI UTENTI DI SECONDO LIVELLO, DAL FILE PRINCIPALE")
#logging.info("STEP 9: RECUPERO TUTTE LE ENTRY DI TIPO REALM=SSO, PER GLI UTENTI DI SECONDO LIVELLO, DAL FILE PRINCIPALE")
#dizionario_utenti_secondo_livello_sso=searchEntrySSO(dizionarioUtentiSecondoLivelloFinal, dizionarioUtenti)
#file_name_utenti_secondo_livello_sso = f"{pathExportFile}/{canale}_Utenti_Secondo_Livello_SSO_No_Expiration_Date.ldif"
#scrivi_ldif(dizionario_utenti_secondo_livello_sso, file_name_utenti_secondo_livello_sso) # Scrivo il file in formato ldif

### STEP 9 - RECUPERO LA LISTA DEI PARENT UID DEGLI UTENTI DI SECONDO LIVELLO ###
logging.info("STEP 9: RECUPERO LA LISTA DEI PARENT UID DEGLI UTENTI DI SECONDO LIVELLO")
listParentuidSecondoLivello=search_parentuid_for_second_level_user(dizionarioUtentiSecondoLivelloFinal,dizionarioUtenti)

### STEP 10 - RECUPERO LA LISTA DEI PARENT UID DEGLI UTENTI APPARTENENTI AL CANALE ###
logging.info("STEP 10: RECUPERO LA LISTA DEI PARENT UID DEGLI UTENTI APPARTENENTI AL CANALE")
listParentuidCanale=search_parentuid_for_second_level_user(dizionarioUtentiCanaleFinal,dizionarioUtenti)

### STEP 11 - Unisco le liste dei parentuid degli utenti di secondo livello e degli utenti del canale
logging.info("STEP 11: Unisco le liste dei parentuid degli utenti di secondo livello e degli utenti del canale")
listParentuidFinal = []
for item in listParentuidSecondoLivello + listParentuidCanale:
    if item not in listParentuidFinal:
        listParentuidFinal.append(item)

### STEP 12 - RECUPERO LE ENTRY DEI PARENTUID DAL FILE PRINCIPALE ###
logging.info("STEP 12: RECUPERO LE ENTRY DEI PARENTUID DAL FILE PRINCIPALE")
fileNameParentuidNoSSO=f"{pathExportFile}/{canale}_parentuid_no_sso.txt"
dizionario_parentuid=search_parentuid_global(listParentuidFinal,dizionarioUtenti)
scrivi_ldif(dizionario_parentuid, fileNameParentuidNoSSO) # Scrivo il file in formato ldif

### STEP 13 - RECUPERO TUTTE LE ENTRY DI TIPO realm=SSO DAL FILE PRINCIPALE PER GLI UTENTI PARENT
logging.info("STEP 13: RECUPERO TUTTE LE ENTRY DI TIPO realm=SSO DAL FILE PRINCIPALE PER GLI UTENTI CHILD DEI PARENTUID")
dizionarioParentuidSSO=searchEntrySSO(dizionario_parentuid, dizionarioUtenti)
fileNameDizionarioParentuidSSO = f"{pathExportFile}/{canale}_UserChildSSO_to_parse.ldif"
scrivi_ldif(dizionarioParentuidSSO, fileNameDizionarioParentuidSSO) # Scrivo il file in formato ldif

### STEP 14 - RIMUOVO LE ENTRY SSO E GLI UTENTI ASSOCIATI CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024
logging.info("STEP 14: RIMUOVO LE ENTRY SSO E GLI UTENTI ASSOCIATI CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024")
dizionarioParentuidSSO_OK,dizionarioParentuid_OK=searchEntrySSOPasswordexpired(dizionarioParentuidSSO,dizionario_parentuid,"20240101")
fileNameDizionarioParentuidSSO_OK = f"{pathExportFile}/{canale}_05_Parentuid_SSO_FINAL.ldif"
scrivi_ldif(dizionarioParentuidSSO_OK, fileNameDizionarioParentuidSSO_OK) # Scrivo il file in formato ldif
fileNameDizionarioParentuid_OK = f"{pathExportFile}/{canale}_04_Parentuid_FINAL.ldif"
scrivi_ldif(dizionarioParentuid_OK, fileNameDizionarioParentuid_OK) # Scrivo il file in formato ldif

### STEP 15 - RECUPERO LE ENTRY CHILD DEI PARENT UID ###
logging.info("STEP 15: RECUPERO LE ENTRY CHILD DEI PARENT UID")
file_name_parentuid_child=f"{pathExportFile}/{canale}_parentuid_child_to_parse.txt"
dizionario_child_to_filter=search_child_for_parent_uid(listParentuidSecondoLivello,dizionarioUtenti,dizionarioUtentiCanaleFinal,dizionarioUtentiSecondoLivelloFinal,file_name_parentuid_child)
scrivi_ldif(dizionario_child_to_filter, file_name_parentuid_child) # Scrivo il file in formato ldif

### STEP 16 - RIMUOVO LE ENTRY CHILD CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024 ###
logging.info("STEP 16: RIMUOVO LE ENTRY CHILD CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024")
dizionario_child_filtered_password_expirationdate=remove_passwordexpirationdate_user(dizionario_child_to_filter,"20240101")
fileNameDizionarioUtentiSecondoLivelloFinal=f"{pathExportFile}/{canale}_parentuid_child_exiprationdate_removed.txt"
scrivi_ldif(dizionario_child_filtered_password_expirationdate, fileNameDizionarioUtentiSecondoLivelloFinal) # Scrivo il file in formato ldif

### STEP 17 - RECUPERO TUTTE LE ENTRY DI TIPO realm=SSO DAL FILE PRINCIPALE PER GLI UTENTI CHILD DEI PARENTUID
logging.info("STEP 17: RECUPERO TUTTE LE ENTRY DI TIPO realm=SSO DAL FILE PRINCIPALE PER GLI UTENTI CHILD DEI PARENTUID")
dizionario_child_sso=searchEntrySSO(dizionario_child_filtered_password_expirationdate, dizionarioUtenti)
file_name_child_sso = f"{pathExportFile}/{canale}_UserChildSSO_to_parse.ldif"
scrivi_ldif(dizionario_child_sso, file_name_child_sso) # Scrivo il file in formato ldif

### STEP 18 - RIMUOVO LE ENTRY SSO E GLI UTENTI ASSOCIATI CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024
logging.info("STEP 18: RIMUOVO LE ENTRY SSO E GLI UTENTI ASSOCIATI CHE HANNO PASSWORD EXPIRATION DATE ANTECEDENTE AL GIORNO 01/01/2024")
dizionario_child_sso_OK,dizionario_child_OK=searchEntrySSOPasswordexpired(dizionario_child_sso,dizionario_child_filtered_password_expirationdate,"20240101")
file_name_dizionario_child_sso_OK = f"{pathExportFile}/{canale}_06_Utenti_child_SSO_FINAL.ldif"
scrivi_ldif(dizionario_child_sso_OK, file_name_dizionario_child_sso_OK) # Scrivo il file in formato ldif
file_name_child_OK = f"{pathExportFile}/{canale}_07_Utenti_child_FINAL.ldif"
scrivi_ldif(dizionario_child_OK, file_name_child_OK) # Scrivo il file in formato ldif

end_time = time.time() # Calcolo l'orario di fine
execution_time = end_time - start_time # Tempo di esecuzione totale
minutes = execution_time // 60  # Divisione intera per ottenere i minuti
seconds = execution_time % 60    # Resto della divisione per ottenere i secondi
logging.info(f"Tempo di esecuzione: {int(minutes)} minuti e {int(seconds)} secondi")
#print(f"Tempo di esecuzione: {int(minutes)} minuti e {seconds:.6f} secondi")