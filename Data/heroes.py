import requests
from bs4 import BeautifulSoup
from json import dump as js_dump
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'}
session = requests.Session()


def get_patch():
    soup = BeautifulSoup(session.get('https://www.dotabuff.com/heroes/impact', headers=headers).text, 'html.parser')
    patch = soup.find('select').contents
    for select in patch:
        if select != '\n':
            text = select.attrs['value']
            if 'patch_' in text:
                return text
    return None


# def debug():
#     soup = BeautifulSoup(session.get('https://www.dotabuff.com/heroes', headers=headers).text, 'html.parser')
#     heroes = soup.find('footer', attrs={'style': 'padding: 0'}).next.contents
#     links = []
#     for hero in heroes:
#         link = hero.attrs.get('href', '')
#         if link != '':
#             links.append(link)
#     for link in links:
#         soup = BeautifulSoup(session.get(f'https://www.dotabuff.com{link}', headers=headers).text, 'html.parser')
#         describe = soup.find('div', attrs={'class': 'header-content-title'}).next.contents
#         name = str(describe[0])
#         data[name] = dict()
#         data[name]['cnt_skills'] = {}


def get_skills_for_name(name, link):
    soup = BeautifulSoup(session.get(link, headers=headers).text, 'html.parser')
    items = soup.find_all('div', {'class': re.compile('skilllist skilllist-col2')})
    items = list(map(lambda x: x.contents[-1].next.contents[1::2], items))
    for num, section in enumerate(items):
        if isinstance(name, list):
            if num >= len(name):
                break
            name_col = name[num]
        else:
            name_col = name
        if name_col:
            for hero in data.keys():
                data[hero]['cnt_skills'][name_col] = data[hero]['cnt_skills'].get(name_col, 0)
        else:
            continue
        for item in section:
            if isinstance(item, str):
                continue
            hero, *act = item.text.replace(' - ', ' – ').split(' – ')
            if hero[0] == ' ':
                hero = hero[1:]
            if hero in data:
                data[hero]['cnt_skills'][name_col] = data[hero]['cnt_skills'][name_col] + 1


def cnt_skills():
    # TODO slow
    name_link = [['dispel', 'https://dota2.gamepedia.com/Dispel'],
                 ['silence', 'https://dota2.gamepedia.com/Silence'],
                 ['attributes', 'https://dota2.gamepedia.com/Attributes'],
                 [['heal', '', 'heal_setting', 'max_health', '', 'heal_manipulation', 'heal_freeze', 'healing_and_regeneration',
                   'based_on_max_health', 'based_on_current_health', 'other_health_based'], 'https://dota2.gamepedia.com/Health'],
                 [['magic_resist_inc', 'magic_resist_red'], 'https://dota2.gamepedia.com/Magic_resistance'],
                 [['mana_restoring', '', 'mana_removing', 'mana_setting', 'max_mana_altering', '', '', '', 'abilities_based_on_max_mana',
                   'abilities_based_on_current_mana', 'other_abilities_with_mana_based'], 'https://dota2.gamepedia.com/Mana'],
                 [['vision_inc', 'vision_red'], 'https://dota2.gamepedia.com/Vision'],
                 ['aura', 'https://dota2.gamepedia.com/Aura'],
                 ['damage_manipulation', 'https://dota2.gamepedia.com/Damage_manipulation'],
                 ['channeling', 'https://dota2.gamepedia.com/Channeling'],
                 ['damage_over_time', 'https://dota2.gamepedia.com/Damage_over_time'],
                 ['evasion', 'https://dota2.gamepedia.com/Evasion'],
                 ['teleport', 'https://dota2.gamepedia.com/Teleport'],
                 ['disarm', 'https://dota2.gamepedia.com/Disarm'],
                 ['forced_move', 'https://dota2.gamepedia.com/Forced_movement'],
                 ['hex', 'https://dota2.gamepedia.com/Hex'],
                 ['hide', 'https://dota2.gamepedia.com/Hide'],
                 ['invisibility', 'https://dota2.gamepedia.com/Invisibility'],
                 [['invulnerability', 'invulnerability_piercing'], 'https://dota2.gamepedia.com/Invulnerability'],
                 [['leash', 'disable_by_leash'], 'https://dota2.gamepedia.com/Leash'],
                 [['root', '', 'disable_by_root'], 'https://dota2.gamepedia.com/Root'],
                 ['sleep', 'https://dota2.gamepedia.com/Sleep'],
                 ['spell_immunity', 'https://dota2.gamepedia.com/Spell_immunity'],
                 ['stun', 'https://dota2.gamepedia.com/Stun'],
                 ['taunt', 'https://dota2.gamepedia.com/Taunt']]
    for name, link in name_link[::-1]:
        get_skills_for_name(name, link)


def upgrade_skill():
    soup = BeautifulSoup(session.get('https://www.dotabuff.com/heroes', headers=headers).text, 'html.parser')
    heroes = soup.find('footer', attrs={'style': 'padding: 0'}).next.contents
    links = []
    for hero in heroes:
        link = hero.attrs.get('href', '')
        if link != '':
            links.append(link)
    for link in links:
        value = dict()
        soup = BeautifulSoup(session.get(f'https://www.dotabuff.com{link}', headers=headers).text, 'html.parser')
        describe = soup.find('div', attrs={'class': 'header-content-title'}).next.contents
        name = str(describe[0])
        value['role'] = list(map(str, describe[1].contents[0].split(', ')))
        attribute = soup.find('tbody', attrs={'class': re.compile('primary')})
        value['main_attribute'] = str(attribute.attrs['class'][0].replace('primary-', ''))
        value['stats'] = dict()
        value['inc_stats'] = dict()
        for stat in attribute.contents[1].contents:
            fst, inc = stat.contents[0].split('+')
            value['stats'][stat.attrs['class'][0]] = int(fst)
            value['inc_stats'][stat.attrs['class'][0]] = float(inc)
        stats = soup.find('table', attrs={'class': 'other'}).contents[0].contents
        value['move_speed'] = int(stats[0].contents[1].text)
        value['sight_range'] = dict()
        sight_range_day, sight_range_night = map(int, stats[1].contents[1].text.split('/'))
        value['sight_range']['day'] = sight_range_day
        value['sight_range']['night'] = sight_range_night
        value['armor'] = float(stats[2].contents[1].text)
        value['attack_speed'] = float(stats[3].contents[1].text)
        value['attack_point'] = float(stats[5].contents[1].text)
        min_damage, max_damage = map(int, stats[4].contents[1].text.split('-'))
        value['damage'] = dict()
        value['damage']['min'] = min_damage
        value['damage']['max'] = max_damage
        soup = BeautifulSoup(session.get(f'https://www.dotabuff.com{link}/counters', headers=headers).text, 'html.parser')
        value['advantages'] = dict()
        for hero in soup.find('table', {'class': 'sortable'}).find('tbody'):
            hero_name = hero.contents[0].attrs['data-value']
            value['advantages'][hero_name] = float(hero.contents[2].attrs['data-value'])
        data[name] = value
    soup = BeautifulSoup(session.get('https://www.dotabuff.com/heroes/meta', headers=headers).text, 'html.parser')
    table = soup.find('table', {'class': 'sortable no-arrows r-tab-enabled'})
    ranks = list(map(lambda rank: rank.next.attrs['title'], table.find('tr', {'class': 'r-none-tablet'}).contents[1:]))
    ranks = list(map(lambda rank: re.search(r'[><]?\w+-?\w* MMR', rank).group(), ranks))
    heroes = table.find('tbody').contents
    for hero in heroes:
        name = hero.contents[0].attrs['data-value']
        data[name]['pickrate'] = dict()
        data[name]['winrate'] = dict()
        for rank, pick, win in zip(ranks, hero.contents[2::2], hero.contents[3::2]):
            data[name]['pickrate'][rank] = float(pick.attrs['data-value'])
            data[name]['winrate'][rank] = float(win.attrs['data-value'])
    soup = BeautifulSoup(session.get(f'https://www.dotabuff.com/heroes/impact?date={PATCH}', headers=headers).text, 'html.parser')
    table = soup.find('table', {'class': 'sortable'}).find('tbody').contents
    for hero in table:
        name = hero.contents[0].attrs['data-value']
        data[name]['kda'] = float(hero.contents[2].attrs['data-value'])
    soup = BeautifulSoup(session.get(f'https://www.dotabuff.com/heroes/economy?date={PATCH}', headers=headers).text, 'html.parser')
    table = soup.find('table', {'class': 'sortable'}).find('tbody').contents
    for hero in table:
        name = hero.contents[0].attrs['data-value']
        data[name]['gold_minute'] = float(hero.contents[2].attrs['data-value'])
        data[name]['exp_minute'] = float(hero.contents[3].attrs['data-value'])
    soup = BeautifulSoup(session.get(f'https://www.dotabuff.com/heroes/damage?date={PATCH}', headers=headers).text, 'html.parser')
    table = soup.find('table', {'class': 'sortable'}).find('tbody').contents
    for hero in table:
        name = hero.contents[0].attrs['data-value']
        data[name]['dmg_hero_minute'] = float(hero.contents[2].attrs['data-value'])
        data[name]['dmg_tower_minute'] = float(hero.contents[3].attrs['data-value'])
        data[name]['heal_minute'] = float(hero.contents[4].attrs['data-value'])
        data[name]['cnt_skills'] = {}
    cnt_skills()


def save_data():
    with open('heroes.json', 'w') as write_file:
        js_dump(data, write_file)


if __name__ == '__main__':
    '''
    data = {hero:
            {roles: [str], stats: {str: int, agi: int, int: int}, inc_stats: {str: float, agi: float, int: float},
            cnt_skills: [stun: float, save: float, heal: float, dispell: float, silence: float, armor: float, controll: float,
            mobility: float, global: float],
            advantages: {hero: float}, kda: float, dmg_hero_minute: float, dmg_tower_minute: float, heal_minute: float, gold_minute: float, 
            exp_minute: float, winrate: {rank: float}, pickrate: {rank: float}, move_speed: int, armor: float, sight_range: {day, night},
             damage: {min: int, max: int}, attack_time: float, main_attribute: str}
           }
    '''
    PATCH = get_patch()
    data = dict()
    upgrade_skill()
    save_data()
