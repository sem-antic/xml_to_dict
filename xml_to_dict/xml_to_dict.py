import xml.etree.ElementTree as ET, re
from collections import defaultdict
from collections.abc import Callable
from typing import Union


class XMLtoDict(object):

    """
    Parameters
    ----------
    key_formatter : Callable[[str], str], default=None
        Callback for formatting tag names into resulting dictionary keys
    """
    def __init__(self, key_formatter: Callable[[str], str] = None):
        self.key_formatter = key_formatter

    def parse(self, xml: str, ):
        return self.__to_dict(ET.fromstring(xml))
    
    def value_from_nest(self, pattern: str, nest: Union[dict, str]):
        nest = nest if type(nest) is dict else self.parse(nest)
        for k, v in nest.items():
            match = re.search(pattern, k)
            if match:
                return v
            if type(v) is dict:
                return self.value_from_nest(pattern, v)

    def __to_dict(self, t: ET.Element):
        key = t.tag
        if self.key_formatter:
            key = self.key_formatter(key)

        d = {key: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(self.__to_dict, children):
                for k, v in dc.items():
                    dd[k].append(v)
            d = {key: {
                    k:v[0] if len(v) == 1 \
                        else v for k, v in dd.items()
            }}
        if t.attrib:
            d[key].update(('@' + k, v) for k, v in t.attrib.items())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                    d[key]['#text'] = text
            else:
                d[key] = text
        return d
