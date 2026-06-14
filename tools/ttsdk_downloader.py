#!/usr/bin/env python3

import patoolib

import os
import platform
import shutil
import sys

path = os.path.dirname(os.path.realpath(__file__))
path = os.path.dirname(path)
sys.path.append(path)
import downloader


# Direct SDK URLs (v5.22a - Cloudflare blocks scraping)
SDK_URLS = {
    "win64": "https://www.bearware.dk/teamtalksdk/v5.22a/tt5prosdk_v5.22a_win64.7z",
    "win32": "https://www.bearware.dk/teamtalksdk/v5.22a/tt5prosdk_v5.22a_win32.7z",
    "ubuntu22_x86_64": "https://www.bearware.dk/teamtalksdk/v5.22a/tt5sdk_v5.22a_ubuntu22_x86_64.7z",
    "raspbian_armhf": "https://www.bearware.dk/teamtalksdk/v5.22a/tt5sdk_v5.22a_raspbian_armhf.7z",
}


def get_url_suffix_from_platform() -> str:
    machine = platform.machine()
    if sys.platform == "win32":
        architecture = platform.architecture()
        if machine == "AMD64" or machine == "x86":
            if architecture[0] == "64bit":
                return "win64"
            else:
                return "win32"
        else:
            sys.exit("Native Windows on ARM is not supported")
    elif sys.platform == "darwin":
        sys.exit("Darwin is not supported")
    else:
        if machine == "AMD64" or machine == "x86_64":
            return "ubuntu22_x86_64"
        elif "arm" in machine:
            return "raspbian_armhf"
        else:
            sys.exit("Your architecture is not supported")


def download() -> None:
    suffix = get_url_suffix_from_platform()
    download_url = SDK_URLS.get(suffix)

    if not download_url:
        sys.exit(f"No SDK URL available for platform: {suffix}")

    print(f"Downloading TeamTalk SDK v5.22a ({suffix})...")
    print(f"From: {download_url}")
    downloader.download_file(download_url, os.path.join(os.getcwd(), "ttsdk.7z"))


def extract() -> None:
    try:
        os.mkdir(os.path.join(os.getcwd(), "ttsdk"))
    except FileExistsError:
        shutil.rmtree(os.path.join(os.getcwd(), "ttsdk"))
        os.mkdir(os.path.join(os.getcwd(), "ttsdk"))
    patoolib.extract_archive(
        os.path.join(os.getcwd(), "ttsdk.7z"), outdir=os.path.join(os.getcwd(), "ttsdk")
    )


def move() -> None:
    path = os.path.join(os.getcwd(), "ttsdk", os.listdir(os.path.join(os.getcwd(), "ttsdk"))[0])
    libraries = ["TeamTalk_DLL", "TeamTalkPy"]
    dest_dir = os.path.join(os.getcwd(), os.pardir) if os.path.basename(os.getcwd()) == "tools" else os.getcwd()
    for library in libraries:
        try:
            os.rename(
                os.path.join(path, "Library", library), os.path.join(dest_dir, library)
            )
        except OSError:
            shutil.rmtree(os.path.join(dest_dir, library))
            os.rename(
                os.path.join(path, "Library", library), os.path.join(dest_dir, library)
            )
    try:
        os.rename(
            os.path.join(path, "License.txt"), os.path.join(dest_dir, "TTSDK_license.txt")
        )
    except FileExistsError:
        os.remove(os.path.join(dest_dir, "TTSDK_license.txt"))
        os.rename(
            os.path.join(path, "License.txt"), os.path.join(dest_dir, "TTSDK_license.txt")
        )


def clean() -> None:
    os.remove(os.path.join(os.getcwd(), "ttsdk.7z"))
    shutil.rmtree(os.path.join(os.getcwd(), "ttsdk"))


def install() -> None:
    print("Installing TeamTalk SDK components")
    print("Downloading latest SDK version...")
    download()
    print("Downloaded. Extracting...")
    extract()
    print("Extracted. Moving files...")
    move()
    print("Moved. Cleaning temporary files...")
    clean()
    print("Cleaned.")
    print("Installation complete.")


if __name__ == "__main__":
    install()
