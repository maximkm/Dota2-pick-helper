from heroes import get_patch
import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from json import load as js_load, dump as js_dump
from time import sleep

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'}
PATCH = None


def load_data():
    try:
        with open('matches.json', 'r') as read_file:
            games = js_load(read_file)
    except FileNotFoundError:
        games = {}
    return games


def save_data():
    with open('matches.json', 'w') as write_file:
        js_dump(data, write_file)


def get_info(match):
    global PATCH
    res = match.contents
    info = {}
    game_id = str(res[0].next.contents[0])
    info['game_mode'] = res[1].contents[0]
    info['patch'] = PATCH
    info['win'] = res[2].next.contents[0].replace(' Victory', '')
    time = list(map(int, res[3].contents[0].split(':')))
    info['duration'] = {'m': time[0], 's': time[1]}
    for key, num in zip(['radiant', 'dire'], [4, 5]):
        info[key] = []
        for hero in res[num].contents:
            info[key].append(hero.next.contents[0].attrs['title'])
    return game_id, info


def update_data(patch=None):
    skill_bracket = ['normal_skill', 'high_skill', 'very_high_skill']
    regions = ['us_west', 'us_east', 'europe_west', 'south_korea', 'se_asia', 'chile', 'australia', 'russia', 'europe_east', 'south_america',
               'south_africa', 'china', 'dubai', 'peru', 'india']
    for skill in skill_bracket:
        for region in regions:
            with requests.Session() as session:
                URL = f'https://www.dotabuff.com/matches?game_mode=all_pick&lobby_type=ranked_matchmaking&region={region}&skill_bracket={skill}'
                soup = BeautifulSoup(session.get(URL, headers=headers).text, 'html.parser')
                table = soup.find('div', attrs={'class': "content-inner"}).find('tbody')
                if table.contents[0].text == 'No Matches':
                    continue
                for match in table.contents:
                    try:
                        game_id, info = get_info(match)
                        info['skill'] = skill
                        data[game_id] = info
                    except Exception as error:
                        logger.exception(error)


def get_time(form='%H:%M:%S>'):
    return datetime.today().strftime(form)


if __name__ == '__main__':
    # Create logger
    logger = logging.getLogger('parser')
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('parser.log')
    file_handler.setFormatter(logging.Formatter('%(filename)s[LINE:%(lineno)-3s]# %(levelname)-8s [%(asctime)s]  %(message)s'))
    logger.addHandler(file_handler)
    # data = {game_id: {radiant: [heroes], dire: [heroes], win: str(dire or radiant), duration: {min, sec}, game_mode: str, skill: str}}
    data = load_data()
    last_cnt = len(data)
    while True:
        try:
            logger.info('Апдейтим')
            print(f'{get_time()} Апдейтим')
            PATCH = get_patch()
            update_data()
        except Exception as error:
            logger.exception(f"Ошибка во время парсинга. {error}")
            print(f'{get_time()} Ошибка во время парсинга')
            sleep(120)
        if last_cnt != len(data):
            last_cnt = len(data)
            save_data()
            logger.info(f'{get_time()} Спарсили {len(data)} матчей')
            print(f'Спарсили {len(data)} матчей')
        sleep(60)
