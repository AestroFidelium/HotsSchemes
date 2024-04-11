import os
import bs4
import json
from collections import defaultdict
import sys
import yaml

def get_xml_files(directory):
    """Получить список XML файлов в директории."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.xml'):
            # if file.lower().endswith('.aitree'):
                yield os.path.join(root, file)

def parse_xml(file_path):
    """Разобрать XML файл и вернуть данные в виде словаря."""
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = bs4.BeautifulSoup(file, 'xml')
        return {child.name: parse_tag(child) for child in soup.find_all(recursive=False)}

def parse_tag(tag):
    """Рекурсивно разобрать тег и вернуть его данные."""
    if tag.find_all(recursive=False):
        # Если у тега есть дочерние элементы, обработаем их
        return {
            'attrs': tag.attrs,
            'children': {child.name: parse_tag(child) for child in tag.find_all(recursive=False)}
        }
    else:
        # Если дочерних элементов нет, вернем только атрибуты
        return tag.attrs

def merge_dicts(base_dict, new_data):
    """Объединить два словаря, добавляя уникальные значения из new_data в base_dict."""
    for key, value in new_data.items():
        if key in base_dict:
            if isinstance(base_dict[key], dict) and isinstance(value, dict):
                merge_dicts(base_dict[key], value)
            elif isinstance(base_dict[key], list) and isinstance(value, list):
                # Добавляем только уникальные элементы списка
                base_dict[key] = list(set(base_dict[key] + value))
            elif base_dict[key] != value:
                # Если значения различаются и не являются списками, создаем список из значений
                base_dict[key] = [base_dict[key], value] if base_dict[key] != value else base_dict[key]
        else:
            base_dict[key] = value

def flatten(nested_list):
    """Функция для распаковки вложенных списков и удаления дубликатов."""
    result = []
    unique_items = set()
    if isinstance(nested_list, list):
        for item in nested_list:
            flat_list = flatten(item)
            for element in flat_list:
                if element not in unique_items:
                    unique_items.add(element)
                    result.append(element)
    else:
        if nested_list not in unique_items:
            unique_items.add(nested_list)
            result.append(nested_list)
    return result


def looped_flatten(got_dict):
    """Рекурсивная функция для распаковки вложенных списков."""
    for key, value in got_dict.items():
        if isinstance(value, dict):
            looped_flatten(value)
        elif isinstance(value, list):
            got_dict[key] = flatten(value)


# Основной код
if __name__ == '__main__':
    sys.setrecursionlimit(20000000)
    directory = 'D:\\Projects\\HotsDeveloper\\mods'
    # directory = 'D:\\Projects\\HotsDeveloper\\SC2Extract'
    all_tags = defaultdict(dict)

    for xml_file in list(get_xml_files(directory)):
        tags = parse_xml(xml_file)
        for tag_name, tag_data in tags.items():
            merge_dicts(all_tags[tag_name], tag_data)

    # Распаковываем вложенные списки
    for tag, content in all_tags.items():
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, list):
                    content[key] = flatten(value)
                elif isinstance(value, dict):
                    looped_flatten(value)

    # Конвертировать в JSON
    with open('output.json', 'w', encoding='utf-8') as json_file:
        json.dump(all_tags, json_file, ensure_ascii=False, indent=4)
    
    # with open('output.yaml', 'w', encoding='utf-8') as yaml_file:
    #     yaml.dump(all_tags, yaml_file, allow_unicode=True, encoding='utf-8')
# 154721
    print(json.dumps(all_tags, ensure_ascii=False, indent=4))
