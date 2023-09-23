import requests                                                                                                                                                                                                                                                                                                                   
from colorama import Fore, Style
import os
import concurrent.futures
token_file_path = "tokens.txt"

class Log:
    @staticmethod
    def err(msg):
        print(f'{Fore.RESET}{Style.BRIGHT}[{Fore.LIGHTRED_EX}-{Fore.RESET}] {msg}')

    @staticmethod
    def succ(msg):
        print(f'{Fore.RESET}{Style.BRIGHT}[{Fore.LIGHTMAGENTA_EX}+{Fore.LIGHTMAGENTA_EX}{Fore.RESET}] {msg}') 

    @staticmethod
    def console(msg):
        print(f'{Fore.RESET}{Style.BRIGHT}[{Fore.LIGHTMAGENTA_EX}-{Fore.RESET}] {msg}')


mail = 0
phone = 0
unclaimed = 0
full = 0
inv = 0

def read_tokens_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return []
def check_token_verification(token):
    global mail
    global phone
    global unclaimed
    global full
    global inv
    headers = {
        'Authorization': token
    }

    response = requests.get('https://discord.com/api/v10/users/@me', headers=headers)

    if response.status_code == 200:
        data = response.json()
        email_verification = data.get('verified', False)
        phone_verification = bool(data.get('phone'))

        if email_verification and phone_verification:
            full += 1
            token_display = f"{token[:24]}{'*' * (len(token) - 24)}"
            return f"{token_display}: {Fore.LIGHTMAGENTA_EX}fully verified{Fore.RESET}"
        elif email_verification:
            mail += 1
            token_display = f"{token[:24]}{'*' * (len(token) - 24)}"
            return f"{token_display}: {Fore.LIGHTMAGENTA_EX}email verified{Fore.RESET}"
        elif phone_verification:
            phone += 1
            token_display = f"{token[:24]}{'*' * (len(token) - 24)}"
            return f"{token_display}: {Fore.LIGHTMAGENTA_EX}phone verified{Fore.RESET}"
        else:
            unclaimed += 1
            token_display = f"{token[:24]}{'*' * (len(token) - 24)}"
            return f"{token_display}: {Fore.LIGHTMAGENTA_EX}unclaimed{Fore.RESET}"
    elif response.status_code == 401:
        inv += 1
        token_display = f"{token[:24]}{'*' * (len(token) - 24)}"
        return f"{token_display}: {Fore.LIGHTMAGENTA_EX}Invalid token.{Fore.RESET}"
    else:
        token_display = f"{token[:24]}{'*' * (len(token) - 24)}"
        return f"{token_display}: {Fore.LIGHTMAGENTA_EX}An error occurred while checking the token.{Fore.RESET}"

def save_tokens_to_file(file_path, tokens):
    with open(file_path, 'w') as file:
        for token_display, full_token in tokens:
            file.write(f"{full_token}\n")

def process_tokens(discord_tokens):
    email_verified_tokens = []
    fully_verified_tokens = []
    not_verified_tokens = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(check_token_verification, token) for token in discord_tokens]
        for future, token in zip(concurrent.futures.as_completed(futures), discord_tokens):
            verification_status = future.result()
            if "fully verified" in verification_status:
                fully_verified_tokens.append((f"{token[:24]}{'*' * (len(token) - 24)}", token))
            elif "email verified" in verification_status:
                email_verified_tokens.append((f"{token[:24]}{'*' * (len(token) - 24)}", token))
            elif "unclaimed" in verification_status:
                not_verified_tokens.append((f"{token[:24]}{'*' * (len(token) - 24)}", token))

            if "Invalid token" in verification_status:
                Log.err(verification_status)
            elif "An error occurred while checking the token." in verification_status:
                Log.err(verification_status)
            else:
                Log.succ(verification_status)

    save_tokens_to_file("output/email_verified_tokens.txt", email_verified_tokens)
    save_tokens_to_file("output/fully_verified_tokens.txt", fully_verified_tokens)
    save_tokens_to_file("output/unclaimed_tokens.txt", not_verified_tokens)

def results():
    Log.console(f"mail verified tokens: {Fore.LIGHTMAGENTA_EX}{mail}{Fore.RESET}")
    Log.console(f"phone verified tokens: {Fore.LIGHTMAGENTA_EX}{phone}{Fore.RESET}")
    Log.console(f"full verified tokens: {Fore.LIGHTMAGENTA_EX}{full}{Fore.RESET}")
    Log.console(f"unclaimed tokens: {Fore.LIGHTMAGENTA_EX}{unclaimed}{Fore.RESET}")
    Log.console(f"Invalid tokens: {Fore.LIGHTMAGENTA_EX}{inv}{Fore.RESET}")
    Log.console(f"Total Tokens Checked: {Fore.LIGHTMAGENTA_EX}{mail + phone + full + unclaimed + inv}{Fore.RESET}")

def main():
    os.system("title discord.gg/nexustools")
    print(f"""{Fore.LIGHTMAGENTA_EX}
                    ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗   ████████╗ ██████╗  ██████╗ ██╗     ███████╗
                    ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝   ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
                    ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗█████╗██║   ██║   ██║██║   ██║██║     ███████╗
                    ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║╚════╝██║   ██║   ██║██║   ██║██║     ╚════██║
                    ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║      ██║   ╚██████╔╝╚██████╔╝███████╗███████║
                    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝      ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
                                                discord.gg/nexus-tools
""")
    input("Press any key to start.")
    discord_tokens = read_tokens_from_file(token_file_path)

    if discord_tokens:
        process_tokens(discord_tokens)
    else:
        print("No Discord tokens found in the file.")



if __name__ == '__main__':
    main()
    Log.console("Tokens Saved in Files.")
    results()
    input("")
