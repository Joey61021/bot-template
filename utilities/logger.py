import time

from colorama import Fore

time_format = '%H:%M:%S'


def log(output):
    print(f"[{time.strftime(time_format)}] {output}")


def info(output):
    print(f"{Fore.LIGHTBLUE_EX}{output}{Fore.RESET}")


def success(output):
    print(f"[{time.strftime(time_format)}] {Fore.LIGHTGREEN_EX}{output}{Fore.RESET}")


def connection(output):
    print(f"[{time.strftime(time_format)}] {Fore.MAGENTA}[CONNECTION] {output}{Fore.RESET}")


def warn(output):
    print(f"[{time.strftime(time_format)}]{Fore.YELLOW} [WARN] {output}{Fore.RESET}")


def critical(output):
    print(f"{Fore.RED}[{time.strftime(time_format)}] [CRITICAL] {output}{Fore.RESET}")


def debug(output):
    print(f"{Fore.LIGHTYELLOW_EX}[{time.strftime(time_format)}] [DEBUG] {output}{Fore.RESET}")
