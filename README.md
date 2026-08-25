# Play Along App
Simple Web App built with Python where the main function is to download any audio track of a song from Youtube and add loop points to help you practise!

# Main Frameworks/Packages
- Flask
- yt-dlp
- SQLite (TODO)

# Pre-requisites
- Python (Version 3.13)

# Getting Started in Development
To ensure a stable development environment, I recommend setting up a virtual environment with the required python version and installing all packages in the **requirements.txt** file.

**(Ubuntu 22.04)**
1. Install python version using deadsnakes PPA

```
sudo add-apt-repository ppa:deadsnakes/ppa 
sudo apt update 
sudo apt install python3.13 python3.13-venv
```

2. Create virtual environment

```
python3.13 -m venv .venv
```

3. Activate virtual environment. Normally, VS Code will detect the creation of a new environment and ask you if you want to use it. Next, if you open a new terminal, you'll see that it's using the '.venv' virtual environment.
In case this doesn't happen, here's how you normally activate a virtual environment:

```
source .venv/bin/activate
```

4. Install required packages (Make sure you are in the same dir as the requirements.txt file). In my case I also had to install these development headers beforehand:

```
sudo apt update
sudo apt install python3.13-dev pkg-config libltdl7 libkrb5-3 libgssapi-krb5-2
```
```
pip install -r requirements.txt
```

5. With all this set, you are ready to start the Flask app! 
```flask --app project run```

# Initialize DB

If you wish so and if you have admin permissions for Azure SQL Server, you can initialize fresh new tables in play_along_app_db using the following command. Make sure you are in the same dir as the `project.py` file.

```flask --app project init-db```