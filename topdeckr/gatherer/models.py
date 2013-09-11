from django.db import models

class Card(models.Model):
    gatherer_id = models.IntegerField(null=True)
    name = models.CharField(max_length=50)
    power = models.CharField(max_length=10, null=True)
    toughness = models.CharField(max_length=10, null=True)
    type = models.CharField(max_length=60)
    sub_type = models.CharField(max_length=60, null=True)
    expansion = models.CharField(max_length=10, null=True)
    mana_cost = models.CharField(max_length=30, default=0)
    converted_mana_cost = models.SmallIntegerField(default=0)
    rarity = models.CharField(max_length=20, null=True)
    keyword_abilities = models.TextField(null=True)
    text = models.TextField(null=True)
    artist = models.CharField(max_length=50, null=True)
    flavor_text = models.TextField(null=True)
    loyalty = models.IntegerField(null=True)

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

class Set(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50)
    link = models.TextField()

# Create your models here.
