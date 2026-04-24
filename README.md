# Virtual Microphone For Voice Chat

>By Cheng-Yu, Hsu\
>Vibe coding using claude\
>IMPORTANT: This program use gtts, if you are holding private conversation, you may need to check the gtts privacy policy.

# How to Use

## Install Virtual Cable

Go to following page to manually install.
Install the zip file, unzip it, and install virtual cable using the installer inside.

```text
https://vb-audio.com/Cable/ 
```

## ffmpeg Installation

Win+R and type `cmd`

* Windows:

```commandline
winget install ffmpeg
```

* Linux:

```commandline
sudo apt install ffmpeg
```

## Discord Microphone Setup

Make sure you change to virtual microphone.

<img width="671" height="382" alt="image" src="https://github.com/user-attachments/assets/57b11007-1506-4f1c-9304-2f934630f4e2" />


## Run The Program

Now you can double the exe file `main.exe` from release to execute.

---

# Build From Source Code

>You may skip this part. If you are not trying to modify the source code.

## Install Virtual Cable

Go to following page to manually install.
Install the zip file, unzip it, and install virtual cable using the installer inside.

```text
https://vb-audio.com/Cable/ 
```

## ffmpeg installation

```commandline
sudo apt install ffmpeg
```

## Create Virtual Environment

> I recommend you to use python3.12 to avoid any incompatible issue.

```commandline
python3.12 -m venv .venv
source .venv/bin/activate
```

## Package Installation

```commandline
pip install sounddevice numpy gtts pydub
```

## Run Program

```commandline
python main.py
```
