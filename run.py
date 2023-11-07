import os



for directory in os.listdir("ChromeData"):
    if "@" in directory:
        print(directory)