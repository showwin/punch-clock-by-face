import subprocess


def say(message):
    subprocess.run(["./jsay.sh", message])
