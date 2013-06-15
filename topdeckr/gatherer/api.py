import md5
import os
import urllib
import urllib2
import re
import lxml.etree
import BeautifulSoup
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

	def online_lookup(self, query):
		query = str(query)
		gatherer_id = re.compile(r'\d+')

		if not gatherer_id.match(query):
			if query.lower() in CardDatabase.LAND_TO_GATHERER_ID.keys():
				return self.online_lookup(CardDatabase.LAND_TO_GATHERER_ID[query.lower()])
			else:
				return self.online_lookup_by_name(query)
		else:
			return self.online_lookup_by_id(query)

	def _check_for_cached_query(self, query):
		cached_filename = query + repr(self)
		cached_filename = md5.new(cached_filename).hexdigest() + '.txt'

		global CACHE_PATH
		if not os.path.exists(CACHE_PATH):
			os.makedirs(CACHE_PATH)

		cached_file = os.path.join(CACHE_PATH, cached_filename)
		if cached_file in self.cache:
			return open(cached_file, 'r')
		return None

	def _get_response_object(self, url):
		request = urllib2.Request(url=url)
		request.add_header('user-agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-gb) AppleWebKit/528.16 (KHTML, like Gecko) Version/4.0 Safari/528.16')
		xml = urllib2.urlopen(request)

		return xml

	def online_lookup_by_name(self, name):
		cached_file = self._check_for_cached_query(name)
		if cached_file is None:
			url = "http://gatherer.wizards.com/pages/search/default.aspx?"
			url = url + urllib.urlencode([('name', '["' + name + '"]'),])

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
		tree = lxml.etree.parse(xml, parser)

		gatherer_id_regex = re.compile(r'\?multiverseid=(\d*)$')
		name_regex = re.compile(r'nameRow$')
		rarity_regex = re.compile(r'rarityRow$')
		current_set_regex = re.compile(r'currentSetSymbol$')
		text_regex = re.compile(r'textRow$')
		power_thoughness_regex = re.compile(r'ptRow$')
		type_regex = re.compile(r'typeRow$')
		mana_regex = re.compile(r'manaRow$')

		card_data = {}

		form = tree.findall("//{http://www.w3.org/1999/xhtml}form")[0]
		card_data['gatherer_id'] = gatherer_id_regex.search(form.get('action')).group(1)

		for div in tree.findall("//{http://www.w3.org/1999/xhtml}div"):
			div_id = div.get('id')

			if div_id is not None:
				if name_regex.search(div_id):
					card_data['name'] = div.getchildren()[1].text.strip()
				elif rarity_regex.search(div_id):
					card_data['rarity'] = div.getchildren()[1].getchildren()[0].text.lower()
				elif current_set_regex.search(div_id):
					card_data['expansion'] = div.getchildren()[1].text
				elif power_thoughness_regex.search(div_id):
					match = div.getchildren()[1].text.strip().split("/")
					card_data['power'] = match[0]
					card_data['thoughness'] = match[1]
				elif mana_regex.search(div_id):
					print div.getchildren()[1]
                                        card_data['mana_cost'] = self.processmana(lxml.etree.tostring(div.getchildren()[1]))
	
		return card_data

	def processmana(self, raw_html):
		print raw_html
		html = BeautifulSoup.BeautifulSoup(raw_html)
		#converted_mana_cost = None
		mana_cost = ''
		for img in html.findAll('img'):
			print "check_one"
			symbol = img.get('alt')
			
			#Colorless
			if self.represents_int(symbol):
				#coverted_mana_cost += int(img.get('alt'))
				mana_cost += img.get('alt')
			
			#Basics
			elif symbol == 'White':
				mana_cost += "W"
			elif symbol == 'Blue':
				mana_cost += "U"
			elif symbol == 'Green':
				mana_cost += "G"
			elif symbol == 'Black':
				mana_cost += "B"
			elif symbol == 'Red':
				mana_cost += "R"

			#I never hated hybrid mana until I had to write this block of code
			elif symbol == 'White or Blue':
				mana_cost += "W/U"
			elif symbol == 'White or Black':
				mana_cost += "W/B"
			elif symbol == 'Blue or Black':
				mana_cost += "U/R"
			elif symbol == 'Blue or Red':
				mana_cost += "U/R"
			elif symbol == 'Black or Green':
				mana_cost += "B/G"
			elif symbol == 'Black or Red':
				mana_cost += "B/R"
			elif symbol == 'Red or Green':
				mana_cost += "R/G"
			elif symbol == 'Red or White':
				mana_cost += "R/W"
			elif symbol == 'Green or White':
				mana_cost += "G/W"
			elif symbol == 'Green or Blue':
				mana_cost += "G/U"
			elif symbol == '2 or White':
				mana_cost += "2/W"
			elif symbol == '2 or Blue':
				mana_cost += "2/U"
			elif symbol == '2 or Black':
				mana_cost += "2/B"
			elif symbol == '2 or Red':
				mana_cost += "2/R"
			elif symbol == '2 or Green':
				mana_cost += "2/G"

			#Phyrexian Sacrificial Mana
			elif symbol == 'Phyrexian Red':
				mana_cost += "PR"
			elif symbol == 'Phyrexian Blue':
				mana_cost += "PU"
			elif symbol == 'Phyrexian Green':
				mana_cost += "PG"
			elif symbol == 'Phyrexian Black':
				mana_cost += "PB"
			elif symbol == 'Phyrexian White':
				mana_cost += "PW"
			mana_cost += " "
		return mana_cost.strip()
	
	#Helper function for the mana processor
	def represents_int(self, s):
		try: 
			int(s)
			return True
	    	except ValueError:
			return False
