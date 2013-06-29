# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Card'
        db.create_table(u'gatherer_card', (
            ('gatherer_id', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
            ('power', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
            ('toughness', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('sub_type', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('expansion', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('mana_cost', self.gf('django.db.models.fields.CharField')(default=0, max_length=30)),
            ('converted_mana_cost', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('rarity', self.gf('django.db.models.fields.CharField')(max_length=11, null=True)),
            ('keyword_abilities', self.gf('django.db.models.fields.TextField')(null=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal(u'gatherer', ['Card'])


    def backwards(self, orm):
        # Deleting model 'Card'
        db.delete_table(u'gatherer_card')


    models = {
        u'gatherer.card': {
            'Meta': {'object_name': 'Card'},
            'converted_mana_cost': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'expansion': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'gatherer_id': ('django.db.models.fields.IntegerField', [], {}),
            'keyword_abilities': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'mana_cost': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '30'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'power': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'rarity': ('django.db.models.fields.CharField', [], {'max_length': '11', 'null': 'True'}),
            'sub_type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'toughness': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['gatherer']