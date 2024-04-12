import os
import bs4
import json
from collections import Counter
import sys
import lxml.etree as etree
from alive_progress import alive_it

def format_xml_lxml(filename):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(filename, parser)
    tree.write(filename, pretty_print=True, encoding='utf-8')

class Attr:
    def __init__(self, name, value):
        self.name = name
        if isinstance(value, list):
            self.value = value
        else:
            self.value = [(value, 1)]
        self.is_optional = False

    
    @property
    def get_only_values(self):
        return [val for val, _ in self.value]

    @property
    def value_type(self):

        def determine_type(value):
            if str(value).lower() in ['true', 'false']:
                return "xs:boolean"
            if str(value).lower() in ['1', '0']:
                return "xs:boolean2"
            elif isinstance(value, (int, float)) or (isinstance(value, str) and value.replace('.', '', 1).isdigit()):
                value = float(value)
                if value.is_integer():
                    return "xs:int"
                    if 0 <= value < 2**64:
                        return "xs:unsignedLong"
                    elif value >= 0:
                        return "xs:nonNegativeInteger"
                    elif value <= 0:
                        return "xs:nonPositiveInteger"
                    elif value < 0:
                        return "xs:negativeInteger"
                    elif value < 2**32:
                        return "xs:unsignedInt"
                    elif value < 2**16:
                        return "xs:unsignedShort"
                    else:
                        return "xs:int"
                else:
                    return "xs:float"
                    if 'e' in str(value).lower() or '.' in str(value):
                        return "xs:double"
                    else:
                        return "xs:decimal"
            else:
                return "xs:string"

        highest_priority_type = []
        for value in self.get_only_values:
            highest_priority_type.append(determine_type(value))
        highest_priority_type, _ = Counter(highest_priority_type).most_common(1)[0]

        return highest_priority_type



    @property
    def description(self):
        return "Not Implemented"
    
    def __eq__(self, value: object) -> bool:
        if isinstance(value, Attr):
            is_the_same_values = True
            target_value = value.get_only_values
            for val in self.get_only_values:
                if val not in target_value:
                    is_the_same_values = False
                    break
            return self.name == value.name and is_the_same_values
        return False

    def __ne__(self, value: object) -> bool:
        if isinstance(value, Attr):
            is_the_same_values = True
            target_value = value.get_only_values
            for val in self.get_only_values:
                if val not in target_value:
                    is_the_same_values = False
                    break
                
            return self.name != value.name or is_the_same_values == False
        return False

    def to_json(self):
        return {self.name: self.get_unique_values, "is_optional": self.is_optional}
    
    
    @property
    def get_unique_values(self):
        if isinstance(self.value, list) == False:
            return self.value
        
        value_type = self.value_type
        if value_type == "xs:int":
            return ["Any Integer"]
        elif value_type == "xs:float":
            return ["Any Float"]
        elif value_type == "xs:decimal":
            return ["Any decimal"]
        elif value_type == "xs:unsignedInt":
            return ["Any unsignedInt"]
        elif value_type == "xs:nonNegativeInteger":
            return ["Any nonNegativeInteger"]
        elif value_type == "xs:nonPositiveInteger":
            return ["Any nonPositiveInteger"]
        elif value_type == "xs:negativeInteger":
            return ["Any negativeInteger"]
        elif value_type == "xs:unsignedShort":
            return ["Any unsignedShort"]
        elif value_type == "xs:unsignedLong":
            return ["Any unsignedLong"]
        elif value_type == "xs:boolean":
            return ["True", "False"]
        elif value_type == "xs:boolean2":
            return ["1", "0"]

        save_values = 150 if (self.name != "id" and self.name != "path") else 35
        counter = Counter(self.value)
        
        if len(counter) <= 10:
            return [val for (val, _), _ in counter.most_common()]
        _, count = counter.most_common(10)[-1]
        if count < 10:
            output = ["UniqueValue"]
            output.extend([val for (val, _), _ in counter.most_common()[:150]])
            return output
        else:
            return [val for (val, _), _ in counter.most_common()]
        

    def get_xsd(self):
        enumerations = "".join(
            [
                '<xs:enumeration value="{0}" />\n'.format(
                    a.replace("<", "").replace(">", "").replace("&", "").replace('"',"")
                )
                for a in self.get_unique_values
            ]
        )

        is_value_array = (
            """<xs:simpleType>
    <xs:union memberTypes="xs:string">
        <xs:simpleType>
            <xs:restriction base="xs:string">
                %ENUMERATIONS%
            </xs:restriction>
        </xs:simpleType>
    </xs:union>
    </xs:simpleType>""".replace(
                "%ENUMERATIONS%", enumerations
            )
            if isinstance(self.value, list)
            else ""
        )
        use = "optional" if self.is_optional else "required"
        return (
            """<xs:attribute name="%NAME%" use="%USE%">
    %IS_VALUE_ARRAY%
    </xs:attribute>""".replace(
                "%NAME%", self.name
            )
            .replace("%USE%", use)
            .replace("%IS_VALUE_ARRAY%", is_value_array)
        )

    def add_new_values(self, new_attr):
        if isinstance(new_attr.value, list):
            for value in new_attr.value:
                if value not in self.value:
                    self.value.append(value)
        else:
            if isinstance(self.value, list):
                if new_attr.value not in self.value:
                    self.value.append((new_attr.value, 1))
                else:
                    val, count = self.value[self.value.index(new_attr.value)]
                    self.value[self.value.index(new_attr.value)] = (val, count + 1)
            else:
                self.value = [(self.value, 1), (new_attr.value, 1)]


class Tag:
    
    def __init__(self, name, attrs: dict, children, is_first_tag = False):
        self.name = name
        self.attrs = []
        for name, value in attrs.items():
            self.attrs.append(Attr(name, value))
        self.attrs = self.merge_myself_attrs(self.attrs)
        self.children = self.merge_myself_children(children)
        self.is_optional = False
        self.is_first_tag = is_first_tag
        
    def to_json(self):
        return {
            "name": self.name,
            "attrs": list(map(lambda attr: attr.to_json(), self.attrs)),
            "children": list(map(lambda tag: tag.to_json(), self.children)),
            "is_optional": self.is_optional,
        }

    @property
    def description(self):
        return "Not Implemented"

    def to_xsd(self):
        
        attrs = "".join(map(lambda attr: attr.get_xsd(), self.attrs))
        childrens = "".join(map(lambda tag: tag.to_xsd(), self.children))
        
        # sequence usually named but lets try rename to choice
        sequence = """<xs:choice minOccurs="0" maxOccurs="unbounded">
                %CHILDRENS%
            </xs:choice>""".replace(
            "%CHILDRENS%", childrens
        ) if len(self.children) > 0 else ""
            
        # mixed="true"
        complexType = """<xs:complexType>
        %SEQUENCE%
        %ATTRS%
        </xs:complexType>
        """.replace(
            "%SEQUENCE%", sequence
        ).replace(
            "%ATTRS%", attrs
        )
        
        output = """<xs:element name="%NAME%" %OCCURS%>
    %COMPLEXTYPE%
    </xs:element>""".replace(
            "%NAME%", self.name
        ).replace(
            "%COMPLEXTYPE%", complexType
        )
        
        
        if self.is_first_tag == False:
            output = output.replace("%OCCURS%", " minOccurs=\"0\" maxOccurs=\"unbounded\"")
        else:
            output = output.replace("%OCCURS%", "")

        return output

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Tag):
            return (
                self.name == value.name
                and self.attrs == value.attrs
                and self.children == value.children
            )
        return False

    def __ne__(self, value: object) -> bool:
        if isinstance(value, Tag):
            return (
                self.name != value.name
                or self.attrs != value.attrs
                or self.children != value.children
            )
        return True

    def merge_attr(self, new_tag):
        
        
        
        for my_attr in self.attrs:
            is_attr_exits = False
            for attr in new_tag.attrs:
                if my_attr.name == attr.name:
                    is_attr_exits = True
                    break
            if is_attr_exits == False:
                my_attr.is_optional = True
            
        
        for attr in new_tag.attrs:
            is_attr_exits = False
            for my_attr in self.attrs:
                if my_attr.name == attr.name:
                    is_attr_exits = True
                    my_attr.add_new_values(attr)
                    break
            
            if is_attr_exits == False:
                attr.is_optional = True
                self.attrs.append(attr)
    

    def merge_children(self, new_tag):
        for another_tag in new_tag.children:
            if another_tag in self.children:
                continue
            is_children_exits = False
            for my_children in self.children:
                if my_children.name == another_tag.name:
                    is_children_exits = True
                    my_children.merge_tag(another_tag)
                    break
            if is_children_exits == False:
                another_tag.is_optional = True
                self.children.append(another_tag)

    def merge_myself_attrs(self, attrs):
        fixed_attrs = []
        for attr in attrs:
            is_attr_exits = False
            for my_attr in fixed_attrs:
                if my_attr.name == attr.name:
                    is_attr_exits = True
                    my_attr.add_new_values(attr)
                    break
            if not is_attr_exits:
                fixed_attrs.append(attr)
        
        return fixed_attrs
    def merge_myself_children(self, children):
        fixed_childrens = []
        for child in children:
            is_children_exits = False
            for fixed_children in fixed_childrens:
                if child.name == fixed_children.name:
                    is_children_exits = True
                    fixed_children.merge_tag(child)
                    break
            if is_children_exits == False:
                fixed_childrens.append(child)
        
        return fixed_childrens
        
    def merge_tag(self, new_tag):
        self.merge_attr(new_tag)
        self.merge_children(new_tag)


def get_xml_files(directory, endswith):
    """Получить список XML файлов в директории."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(endswith):
                yield os.path.join(root, file)


def parse_xml(file_path):
    """Разобрать XML файл и вернуть данные в виде словаря."""
    with open(file_path, "r", encoding="utf-8") as file:
        soup = bs4.BeautifulSoup(file, "xml")
        return [parse_tag(child, is_first_tag=True) for child in soup.find_all(recursive=False)]



def parse_tag(tag, is_first_tag = False):
    """Рекурсивно разобрать тег и вернуть его данные."""
    if tag.find_all(recursive=False):
        return Tag(
            is_first_tag=is_first_tag,
            name=tag.name,
            attrs=tag.attrs,
            children=[parse_tag(child) for child in tag.find_all(recursive=False)],
        )
    else:
        return Tag(tag.name, tag.attrs, [], is_first_tag)


def merge_tags(old_tags, new_tags):
    """Объединить два словаря, добавляя уникальные значения из new_data в base_dict."""
    for new_tag in new_tags:
        is_tag_exits = False
        for old_tag in old_tags:
            if old_tag.name == new_tag.name:
                is_tag_exits = True
                old_tag.merge_tag(new_tag)
                break
        if not is_tag_exits:
            old_tags.append(new_tag)


def format_out():
    with open("./output.xsd", "r", encoding="utf-8") as xsd:
        soup = bs4.BeautifulSoup(xsd.read(), "xml")
        soup.setup()


def output_xsd(filename = "output.xsd"):
    with open(filename, "w", encoding="utf-8") as xsd:
        text = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" elementFormDefault="qualified">"""
        for tag in all_tags:
            text += tag.to_xsd()
        text += "\n</xs:schema>"
        xsd.write(text)
    format_xml_lxml(filename)
    
def output_json(filename = "output.json"):
    with open("output.json", "w", encoding="utf-8") as json_file:
        json.dump(
            list(map(lambda tag: tag.to_json(), all_tags)),
            json_file,
            ensure_ascii=False,
            indent=4,
        )

if __name__ == "__main__":
    sys.setrecursionlimit(20000000)
    universal = list(get_xml_files("D:\\Projects\\HotsDeveloper\\mods", ".xml"))
    universal.extend(list(get_xml_files("D:\\Projects\\HotsDeveloper\\mods", ".aitree")))
    universal.extend(list(get_xml_files("D:\\Projects\\HotsDeveloper\\mods", ".stormlayout")))
    
    # Plus StarCraft II
    # universal.extend(get_xml_files("D:\\Projects\\HotsDeveloper\\SC2Extract", ".xml"))
    # universal.extend(list(get_xml_files("D:\\Projects\\HotsDeveloper\\SC2Extract", ".sc2layout")))
    
    all_tags = []
    # for xml_file in alive_it(list(get_xml_files("D:\\Projects\\HotsDeveloper\\mods", ".xml"))), title="Working"):
    # for xml_file in alive_it(list(get_xml_files("D:\\Projects\\HotsDeveloper\\mods", ".aitree")), title="Working"):
    # for xml_file in alive_it(list(get_xml_files("D:\\Projects\\HotsDeveloper\\mods", ".stormlayout")), title="Working"):
    for xml_file in alive_it(universal, title="Working"):
        merge_tags(all_tags, parse_xml(xml_file))
    output_json()
    output_xsd()