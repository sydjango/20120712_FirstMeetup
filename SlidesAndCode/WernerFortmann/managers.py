# Author: Werner Fortmann <werner.fortmann@gmail.com>
#

from django.db import models
from django.db.models.query import QuerySet
import pandas

class ForturusQuerySet(QuerySet):
	def to_df(self):
		field_names = [field.name for field in self.model._meta.fields]
		qs_values = self.values_list(*field_names)
		return pandas.DataFrame(list(qs_values), columns = field_names) if len(qs_values) else pandas.DataFrame(columns = field_names)

class ForturusManager(models.Manager):
	def get_query_set(self):
		return ForturusQuerySet(self.model, using=self._db)
