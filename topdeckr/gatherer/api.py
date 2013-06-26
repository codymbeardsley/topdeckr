# -*- coding: utf-8 -*-
import md5
import os
import urllib
import urllib2
import re
import lxml.etree
import BeautifulSoup
from topdeckr.settings import ACCEPTED_KEYWORD_ABILITIES
from gatherer.search import get_query
from gatherer.models import Card
CACHE_PATH = os.path.join(os.path.dirname(__file__), 'cache')

class CardDatabase(object):
    LAND_TO_GATHERER_ID = {
        'forest': '174928',
        'swamp': '197258',
        'island': '190588',
        'plains': '197255',
        'mountain': '190586',
    }

    def __init__(self, *kwargs):
        self.cache = []

    def __del__(self):
        import os

        for path in self.cache:
            os.remove(path)

    def online_lookup(self, query, only_return_name=False):
        self.only_return_name = only_return_name
        query = str(query)
        self.query = query
        gatherer_id = re.compile(r'\d+')
        if not gatherer_id.match(query):
            if query.lower() in CardDatabase.LAND_TO_GATHERER_ID.keys():
                return self.online_lookup(CardDatabase.LAND_TO_GATHERER_ID[query.lower()])
            else:
                return self.online_lookup_by_name(query)
        else:
            return self.online_lookup_by_id(query)

    def _check_for_cached_query(self, query_string):
        found_entries = None
        try:
            entry_query = get_query(query_string, ['name'])
            found_entries = Card.objects.filter(entry_query).order_by('-name')
            print found_entries
            return found_entries[0]
        except:
            return None

    def _get_response_object(self, url):
        request = urllib2.Request(url=url)
        request.add_header('user-agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-gb) AppleWebKit/528.16 (KHTML, like Gecko) Version/4.0 Safari/528.16')
        xml = urllib2.urlopen(request)

        return xml

    def online_lookup_by_name(self, name):
        cached_card = self._check_for_cached_query(name)
        if cached_card is None:
            url = "http://gatherer.wizards.com/pages/search/default.aspx?"
            url = url + urllib.urlencode([('name', '["' + name + '"]'),])
            xml = self._get_response_object(url)
            cached_card = Card(**self._parse_gatherer_xml(xml.read()))
            cached_card.save()
            cached_card = cached_card.toDict()
            if self.only_return_name:
                return {'name': cached_card['name']}
            else:
                return cached_card
        else:
            cached_card = cached_card.toDict()
            if self.only_return_name:
                 return {'name': cached_card['name']}
            else:
                 return cached_card


    def online_lookup_by_id(self, gatherer_id):
        cached_file = self._check_for_cached_query(gatherer_id)
        if cached_file is None:
            url = "http://gatherer.wizards.com/Pages/Card/Details.aspx?"
            url = url + urllib.urlencode([('multiverseid', gatherer_id),])

            xml = self._get_response_object(url)
            cached_filename = name + repr(self)
            cached_filename = md5.new(cached_filename).hexdigest() + '.txt'

            cached_filename = os.path.join(CACHE_PATH, cached_filename)
            f = open(cached_filename, 'w')
            f.write(xml.read())
            f.close()

            self.cache.append(cached_filename)

            cached_file = open(cached_filename, 'r')

        return self._parse_gatherer_xml(cached_file)

    def _parse_gatherer_xml(self, xml):
        parser = lxml.etree.XMLParser(recover=True)
        tree = lxml.etree.fromstring(xml, parser)
        
        gatherer_id_regex = re.compile(r'\?multiverseid=(\d*)$')
        name_regex = re.compile(r'nameRow$')
        rarity_regex = re.compile(r'rarityRow$')
        current_set_regex = re.compile(r'currentSetSymbol$')
        text_regex = re.compile(r'textRow$')
        power_toughness_regex = re.compile(r'ptRow$')
        type_regex = re.compile(r'typeRow$')
        mana_regex = re.compile(r'manaRow$')

        card_data = {}

        form = tree.findall(".//{http://www.w3.org/1999/xhtml}form")[0]
        card_data['gatherer_id'] = gatherer_id_regex.search(form.get('action')).group(1)

        for div in tree.findall(".//{http://www.w3.org/1999/xhtml}div"):
            div_id = div.get('id')

            if div_id is not None:
                if name_regex.search(div_id):
                    card_data['name'] = div.getchildren()[1].text.strip()
                elif type_regex.search(div_id):
                    try:
                        #Gotta' love Wizards' use of non-ascii characters
                        match = re.split(u'\xe2\x80\x94', div.getchildren()[1].text.strip().encode('utf-8'))
                        card_data['type'] = match[0].strip()
                        card_data['sub_type'] = match[1].strip()
                    except:
                        pass
                elif current_set_regex.search(div_id):
                    card_data['expansion'] = div.getchildren()[1].text
                elif power_toughness_regex.search(div_id):
                    match = div.getchildren()[1].text.split("/")
                    card_data['power'] = match[0].strip() 
                    card_data['toughness'] = match[1].strip()
                elif mana_regex.search(div_id):
                    processed_mana = self.process_mana(lxml.etree.tostring(div.getchildren()[1]))
                    card_data['mana_cost'] = processed_mana['mana_cost']
                    card_data['converted_mana_cost'] = processed_mana['converted_mana_cost']
                elif text_regex.search(div_id):
                    match = self.process_text(lxml.etree.tostring(div.getchildren()[1]))
                    card_data['keyword_abilities'] = match['keywords']
                    card_data['text'] = match['text']
                elif rarity_regex.search(div_id):
                    card_data['rarity'] = div.getchildren()[1].getchildren()[0].text.lower()
                    #Whichever cardfield is parsed last MUST have this
                    #clause, it is to deal with flip-cards
                    if not re.search(self.query, card_data['name'].lower()):
                        card_data = {}
                        card_data['gatherer_id'] = gatherer_id_regex.search(form.get('action')).group(1)
                        continue
                    else:
                        break

        return card_data

    def process_mana(self, raw_html):
        html = BeautifulSoup.BeautifulSoup(raw_html)
        converted_mana_cost = 0
        mana_cost = ''
        for img in html.findAll('img'):
            symbol = self.process_symbol(img.get('alt'))
            if self.represents_int(symbol):
                converted_mana_cost += int(symbol)
            else:
                converted_mana_cost += 1
            mana_cost += symbol + " "
        return {'mana_cost' : mana_cost.strip(), 'converted_mana_cost' : converted_mana_cost}

    #Helper function for the mana processor
    def represents_int(self, possible_integer):
        try:
            int(possible_integer)
            return True
        except ValueError:
            return False

    #Search through cardtext and return the keyword abilities
    def process_text(self, raw_html):
        html = BeautifulSoup.BeautifulSoup(raw_html)
        text_areas = html.findAll("div", { "class" : "cardtextbox" })#Get the cardtext elements out of the html
        #Only use the first cardtextbox(as that is where the keywords are) and split them into an array
        keyword_abilities = []
        card_text = ''
        for text_area in text_areas:
            for img in text_area.findAll("img"):
                symbol = self.process_symbol(img.get('alt'))
                img.replaceWith(symbol + ' ')
            card_text += text_area.renderContents() + '\n'
            keyword_abilities_preprocessed = text_area.renderContents().split(',')
            #Compare the Keywords in the settings file to cleaned Keywords we have here
            for keyword in keyword_abilities_preprocessed:
                keyword = keyword.split("<")[0]#Clean helper text from keywords
                keyword = keyword.strip().lower().capitalize()
                if keyword in ACCEPTED_KEYWORD_ABILITIES:
                    keyword_abilities.append(keyword)
        return {'keywords': keyword_abilities, 'text': card_text}

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
