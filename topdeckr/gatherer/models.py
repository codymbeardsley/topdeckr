from django.db import models

class Card(models.Model):
	gatherer_id = models.IntegerField()
	name = models.CharField(max_length=50, primary_key=True)
	power = models.CharField(max_length=10, null=True)
	toughness = models.CharField(max_length=10, null=True)
	type = models.CharField(max_length=30)
	sub_type = models.CharField(max_length=30, null=True)
	expansion = models.CharField(max_length=40)
	mana_cost = models.CharField(max_length=30, default=0)
	converted_mana_cost = models.SmallIntegerField(default=0)
	rarity = models.CharField(max_length=11, null=True)
	keyword_abilities = models.TextField(null=True)
	text = models.TextField(null=True)
	
	def toDict(self):
		return {'gid': self.gatherer_id, 
			'name': self.name,
			'power': self.power,
			'toughness': self.toughness,
			'type': self.type,
			'subtype': self.sub_type,
			'expansion': self.expansion, 
			'mana cost': self.mana_cost,
			'cmc': self.converted_mana_cost,
			'rarity': self.rarity,
			'abilities': self.keyword_abilities,
			'text': self.text,} 

# Create your models here.
