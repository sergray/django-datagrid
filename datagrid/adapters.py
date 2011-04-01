class ManagerAdapter(object):
    objects=None

class QuerySetAdapter(object):
    pass


class DjangoQuerySetAdapter(QuerySetAdapter):
    """Decorator to use django query sets"""

    def __init__( self, subject ):
        self.__subject = subject

    def __getattr__( self, name ):
        return getattr( self.__subject, name )

    def extra_sort(self, *field_names):
        if not field_names:
            return self
        field = field_names[0]
        if field.keys()[0].startswith("-"):
            f = field.keys()[0]
            select = {f[1:]:field[f]}
            self.__subject = self.__subject.extra(select=select)
        else:
            self.__subject = self.__subject.extra(select=field)

        self.__subject = self.__subject.extra(order_by=field.keys())
        return self.__subject


class DictionaryQuerySetAdapter(QuerySetAdapter):
    """Decorator to use datagrids with list of dictonaries"""
    def __init__(self, list):
        self.model = ManagerAdapter()
        self.model.objects = self
        self.list = list

    def __getitem__(self, items):
        if isinstance(items,int):
            i = self.list[items]
            return Struct(**i)
        self.list = self.list.__getitem__(items)
        return self

    def distinct(self, true_or_false=True):
        return self

    def count(self):
        return len(self.list)

    def filter(self, *args, **kwargs):
        return self

    def values_list(self, *fields, **kwargs):
        if fields:
            field = fields[0]
            if field == "pk":
                field = "id"
        else:
            return self
        list = [i[field] for i in self.list]
        return list

    def __len__(self):
        return len(self.list)

    def order_by(self, *field_names):
        if not field_names:
            return self
        index = field_names[0]
        reverse = False
        if index.startswith("-"):
            reverse = True
            index = index[1:]
        self.list = sorted(self.list,
                               key=lambda item : item[index],
                               reverse=reverse)
        return self

    def extra_sort(self, *field_names):
        return self

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)
