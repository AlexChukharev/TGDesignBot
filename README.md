# DisignBot
## Description
A python bot project capable of searching 
for presentations on disk, finding tagged slides in them, 
sending fonts to slides and presentations, and retrieving 
all fonts from the folder where the user is located

## How to install (Linux)
0. Python 3.10.12 + install ``` libgdiplus/mono-libgdiplus``` 
1. Clone the repository using `git clone`
2. Create a virtual environment near the repository folder using 
``` 
sudo python3 -m venv myenv
```
3. Activate the virtual environment
``` 
source myenv/bin/activate
```
4. Download the libraries
``` 
pip install -r TGDesignBot/requirements.txt
```
5. Create a docker container:
    1. Create a folder with the `docker-compose.yml` file in it
   2. Insert the following text into it:
   ```yaml
   version: "3.9"
   services:
      postgres:
        image: postgres:latest
        environment:
          POSTGRES_DB: "postgres"
          POSTGRES_USER: "postgres"
          POSTGRES_PASSWORD: "postgres"
          PGDATA: "/var/lib/postgresql/data/pgdata"
        volumes:
          - ./data:/var/lib/postgresql/data
        ports:
          - "5432:5432"
   ```
   3. Activate container using
   ``` 
   docker-compose up --build -d
   ```
6. In the `TGDesignBot` folder:
   1. Create file `.env`
   2. In `.env` add strings
   ``` 
   BOT_TOKEN = 'YOUR_BOT_TOKEN'
   YANDEX_DISK_TOKEN = 'YOUR_YDISK_TOKEN'
   ```
   Replace 'YOUR_BOT_TOKEN' with your bot token.
   Replace 'YOUR_YDISK_TOKEN' with your yandex disk token.
7. Complied! You can run `main.py`
## Technical information
### Components
The bot currently consists of 6 folders, each of which performs a different function
#### DBHandler
Here you can find scripts for interacting with the database and its initialization
#### pptxHandler
Everything for parsing slides is here
#### TelegramHandler
Everything for the telegram bot to work. It is in this part that various functions from the project are used, keyboards,
different handlers.
#### Tree
The folder tree that the user navigates through
#### utility
Various functions that use more complex logic
#### YandexDisk
It is used to work with yadisk and its parsing

