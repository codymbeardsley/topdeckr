# -*- coding: utf-8 -*-
import urllib
import requests
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import NavigableString
from topdeckr.settings import ACCEPTED_KEYWORD_ABILITIES
from gatherer.models import Card, Set


class CardDatabase(object):
    URL_BASE = 'http://magiccards.info'
    TEST_MODE = False

    def get_card(self, id):
        try:
            return Card.objects.get(id=id[0]).to_dict()
        except Card.DoesNotExist:
            return {'status': 'NOT_FOUND'}

    def get_all_cards(self):
        set_list = self.get_all_sets()
        for set in set_list:
            try:
                self.get_all_cards_in_set(set['code'])
            except:
                print("Error encountered while processing: " + set['code'])
                pass

    def get_all_sets(self):
        print('Retrieving Card Sets...')
        req = requests.get(self.URL_BASE + '/sitemap.html')
        soup = BeautifulSoup(req.content)
        en_anchor = soup.find('a', {'name': 'en'})
        en_table = en_anchor.findNext('table')
        en_set_html = en_table.findAll('a')
        sets = []
        for card_set in en_set_html:
            set_data = {
                'name': card_set.text,
                'code': card_set.parent.find('small').text,
                'link': card_set['href']}
            set_object = Set(**set_data)
            if not self.TEST_MODE:
                set_object.save()
            sets.append(set_data)
            print('Added ' + set_object.name)
        return sets

    def get_all_cards_in_set(self, set_code):
        query_parameters = {'q': '++e:' + set_code + '/en',
                            'v': 'spoiler',
                            's': 'issue'}
        query = '/query?' + urllib.urlencode(query_parameters)
        request = requests.get(self.URL_BASE + query)
        soup = BeautifulSoup(request.content)
        cards_raw_data = soup.findAll('span')
        set_entry = Set.objects.get(code=set_code)
        for card_raw_data in cards_raw_data:
            card_data = {}
            card_data['name'] = card_raw_data.text
            card_text_line = card_raw_data.findNextSibling('p', {'class': 'ctext'})
            card_type_and_cost_line = card_text_line.findPreviousSibling('p')
            card_rarity_line = card_type_and_cost_line.findPreviousSibling('p')
            card_flavor_text_line = card_text_line.findNextSibling('p')
            card_art_line = card_flavor_text_line.findNextSibling('p')
            card_data['rarity'] = unicode(card_rarity_line.findNext('i').text) if card_rarity_line else u'Special'
            card_data['flavor_text'] = unicode(card_flavor_text_line.text)
            card_data['artist'] = unicode(card_art_line.text).replace('Illus. ', '')
            card_data['text'] = [rl for rl in card_text_line.find('b').contents if isinstance(rl, NavigableString)]
            card_data['set'] = set_entry
            card_keyword_abilities = []
            for card_text_area in card_data['text']:
                keyword_abilities_preprocessed = card_text_area.split(',')
                for keyword in keyword_abilities_preprocessed:
                    keyword = keyword.strip().lower().capitalize()
                    if keyword in ACCEPTED_KEYWORD_ABILITIES:
                        card_keyword_abilities.append(keyword)
            card_data['keyword_abilities'] = card_keyword_abilities

            card_type_line, card_cost_line = [l.strip() for l in
                                              card_type_and_cost_line.text.split(',')]
            card_types = card_type_line.split()
            if '/' in card_types[-1]:
                card_data['power'], card_data['toughness'] = card_types[-1].split('/')
                card_types = card_types[:-1]
            if card_data['name'] == u'1996 World Champion':
                card_data['type'] = [u'Legendary', u'Creature']
                card_data['sub_type'] = []
            elif card_data['name'] == u'Shichifukujin Dragon':
                card_data['type'] = [u'Creature']
                card_data['sub_type'] = [u'Dragon']
            elif card_data['name'] == u'Old Fogey':
                card_data['type'] = ['Creature']
                card_data['sub_type'] = ['Dinosaur']
            elif u'Enchant' in card_types:
                card_data['type'] = [u'Enchantment']
                card_data['sub_type'] = [u'Aura']
            elif u'\u2014' in card_types:
                i = card_types.index(u'\u2014')
                card_data['type'] = card_types[:i]
                card_data['sub_type'] = card_types[i + 1:]            
            else:
                card_data['type'] = card_types
            if 'card_type' in card_data:
                if u'Legend' in card_data['sub_type']:
                    card_data['sub_type'].remove(u'Legend')
                    card_data['type'].append(u'Legendary')
                if u'(Loyalty:' in card_data['sub_type']:
                    i = card_data['sub_type'].index(u'(Loyalty:')
                    card_data['loyalty'] = int(card_data['sub_type'][i + 1].strip(')'))
                    card_data['sub_type'] = card_data['sub_type'][:i]
            if 'type' in card_data:
                card_data['type'] = " ".join(card_data['type'])
            if 'sub_type' in card_data:
                card_data['sub_type'] = " ".join(card_data['sub_type'])
            if card_cost_line == u'':
                card_data['mana_cost'], card_data['converted_mana_cost'] = ('', 0)
            elif '(' in card_cost_line:
                card_data['mana_cost'], card_data['converted_mana_cost'] = card_cost_line.split()
                card_data['converted_mana_cost'] = int(card_data['converted_mana_cost'].strip('()'))
            else:
                card_data['mana_cost'], card_data['converted_mana_cost'] = (card_cost_line, 0)
            if card_data:
                card_object = Card(**card_data)
                print('Processed ' + card_object.name)
                if not self.TEST_MODE:
                    card_object.save()
        return None
    def process_symbol(self, symbol):
            shorthand_cost = None
            if self.represents_int(symbol):
                shorthand_cost = symbol
            else:
                #Basics
                if symbol == 'White':
                    shorthand_cost = "W"
                elif symbol == 'Blue':
                    shorthand_cost = "U"
                elif symbol == 'Green':
                    shorthand_cost = "G"
                elif symbol == 'Black':
                    shorthand_cost = "B"
                elif symbol == 'Red':
                    shorthand_cost = "R"
                elif symbol == 'Variable Colorless':
                    shorthand_cost = "X"

                elif symbol == "Tap":
                    shorthand_cost = "T"
                elif symbol == "Untap":
                    shorthand_cost = "UT"

                #I never hated hybrid mana until I had to write this block of code
                elif symbol == 'White or Blue':
                    shorthand_cost = "W/U"
                elif symbol == 'White or Black':
                    shorthand_cost = "W/B"
                elif symbol == 'Blue or Black':
                    shorthand_cost = "U/R"
                elif symbol == 'Blue or Red':
                    shorthand_cost = "U/R"
                elif symbol == 'Black or Green':
                    shorthand_cost = "B/G"
                elif symbol == 'Black or Red':
                    shorthand_cost = "B/R"
                elif symbol == 'Red or Green':
                    shorthand_cost = "R/G"
                elif symbol == 'Red or White':
                    shorthand_cost = "R/W"
                elif symbol == 'Green or White':
                    shorthand_cost = "G/W"
                elif symbol == 'Green or Blue':
                    shorthand_cost = "G/U"
                elif symbol == '2 or White':
                    shorthand_cost = "2/W"
                elif symbol == '2 or Blue':
                    shorthand_cost = "2/U"
                elif symbol == '2 or Black':
                    shorthand_cost = "2/B"
                elif symbol == '2 or Red':
                    shorthand_cost = "2/R"
                elif symbol == '2 or Green':
                    shorthand_cost = "2/G"

                #Phyrexian Sacrificial Mana
                elif symbol == 'Phyrexian Red':
                    shorthand_cost = "PR"
                elif symbol == 'Phyrexian Blue':
                    shorthand_cost = "PU"
                elif symbol == 'Phyrexian Green':
                    shorthand_cost = "PG"
                elif symbol == 'Phyrexian Black':
                    shorthand_cost = "PB"
                elif symbol == 'Phyrexian White':
                    shorthand_cost = "PW"
            return shorthand_cost
