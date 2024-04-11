import os
import bs4
from collections import defaultdict
import json
import sys

def get_xml_files(directory):
    """Получить список XML файлов в директории."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().find("terrain") >= 0: continue
            elif file.lower().find("preload") >= 0: continue
            elif file.lower().find("waterdata") >= 0: continue
            elif file.lower().find("banklist") >= 0: continue
            elif file.lower().find("scorevaluedata") >= 0: continue
            elif file.lower().find("soundmixsnapshotdata") >= 0: continue
            elif file.lower().find("requirementnodedata") >= 0: continue
            elif file.lower().find("requirementdata") >= 0: continue
            elif file.lower().find("conversationdata") >= 0: continue
            elif file.lower().find("voiceoverdata") >= 0: continue
            elif file.lower().find("lightdata") >= 0: continue
            elif file.lower().find("cameradata") >= 0: continue
            elif file.lower().find("gameuidata") >= 0: continue
            elif file.lower().find("goaldata") >= 0: continue
            elif file.lower().find("pingdata") >= 0: continue
            elif file.lower().find("announcerpackdata") >= 0: continue
            elif file.lower().find("characterdata") >= 0: continue
            elif file.lower().find("userdata") >= 0: continue
            elif file.lower().find("payloadvodata") >= 0: continue
            elif file.lower().find("scbrawlvodata") >= 0: continue
            elif file.lower().find("scoreresultdata") >= 0: continue
            elif file.lower().find("doodadautodata") >= 0: continue
            elif file.lower().find("rewarddata") >= 0: continue
            elif file.lower().find("heroes_regions") >= 0: continue
            elif file.lower().find("achievementdata") >= 0: continue
            elif file.lower().find("achievementtermdata") >= 0: continue
            elif file.lower().find("actorsupportdata") >= 0: continue
            elif file.lower().find("alertdata") >= 0: continue
            elif file.lower().find("announcementdata") >= 0: continue
            elif file.lower().find("attachmethoddata") >= 0: continue
            elif file.lower().find("bannerdata") >= 0: continue
            elif file.lower().find("beamdata") >= 0: continue
            elif file.lower().find("boostdata") >= 0: continue
            elif file.lower().find("cliffdata") >= 0: continue
            elif file.lower().find("cliffmeshdata") >= 0: continue
            elif file.lower().find("collectioncategorydata") >= 0: continue
            elif file.lower().find("dspdata") >= 0: continue
            elif file.lower().find("configdata") >= 0: continue
            elif file.lower().find("colorspecdata") >= 0: continue
            elif file.lower().find("colorstyledata") >= 0: continue
            elif file.lower().find("emoticondata") >= 0: continue
            elif file.lower().find("emoticonpackdata") >= 0: continue
            elif file.lower().find("errordata") >= 0: continue
            elif file.lower().find("fowdata") >= 0: continue
            elif file.lower().find("footprintdata") >= 0: continue
            elif file.lower().find("gamequestuidata") >= 0: continue
            elif file.lower().find("gempackdata") >= 0: continue
            elif file.lower().find("heromasterydata") >= 0: continue
            elif file.lower().find("itemclassdata") >= 0: continue
            elif file.lower().find("itemcontainerdata") >= 0: continue
            elif file.lower().find("lensflaresetdata") >= 0: continue
            elif file.lower().find("lootchestdata") >= 0: continue
            elif file.lower().find("mapdata") >= 0: continue
            elif file.lower().find("physicsmaterialdata") >= 0: continue
            elif file.lower().find("portraitpackdata") >= 0: continue
            elif file.lower().find("productsetdata") >= 0: continue
            elif file.lower().find("racedata") >= 0: continue
            elif file.lower().find("reverbdata") >= 0: continue
            elif file.lower().find("shapedata") >= 0: continue
            elif file.lower().find("soundexclusivitydata") >= 0: continue
            elif file.lower().find("statdata") >= 0: continue
            elif file.lower().find("spraydata") >= 0: continue
            elif file.lower().find("credits") >= 0: continue
            elif file.lower().find("lootchest") >= 0: continue
            elif file.lower().find("includes") >= 0: continue
            elif file.lower().find("standardinfo") >= 0: continue
            elif file.lower().find("librarylist") >= 0: continue
            elif file.lower().find("bundledata") >= 0: continue
            elif file.lower().find("conversationstatedata") >= 0: continue
            elif file.lower().find("mountdata") >= 0: continue
            elif file.lower().find("skindata") >= 0: continue
            elif file.lower().find("talentdata") >= 0: continue
            elif file.lower().find("talentprofiledata") >= 0: continue
            elif file.lower().find("texturedata") >= 0: continue
            elif file.lower().find("texturesheetdata") >= 0: continue
            elif file.lower().find("tiledata") >= 0: continue
            elif file.lower().find("trophydata") >= 0: continue
            elif file.lower().find("typedescriptiondata") >= 0: continue
            elif file.lower().find("upgradedata") >= 0: continue
            elif file.lower().find("vodefinitiondata") >= 0: continue
            elif file.lower().find("voicelinedata") >= 0: continue
            elif file.lower().find("brawldata") >= 0: continue
            elif file.lower().find("itemdata") >= 0: continue
            elif file.lower().find("shardbundledata") >= 0: continue
            if file.lower().endswith('.xml'):
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

def merge_dicts2(d1, d2):
    """Объединить два словаря, добавляя уникальные значения из d2 в d1."""
    for key, value in d2.items():
        if key in d1:
            if isinstance(value, dict):
                merge_dicts(d1[key], value)
            elif isinstance(value, list):
                d1[key].extend(x for x in value if x not in d1[key])
            else:
                if value != d1[key]:
                    d1[key] = [d1[key], value]
        else:
            d1[key] = value
            
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



# Основной код
if __name__ == '__main__':
    # sys.setrecursionlimit(200000)
    # print(sys.getrecursionlimit())
    directory = 'D:\\Projects\\HotsDeveloper\\mods'
    # directory = 'D:\\Projects\\HotsMakeEasy\\'
    all_tags = defaultdict(dict)
    
    # names = []
    # for i in list(get_xml_files(directory))[:350]:
    #     name = i.split("\\")[-1].split(".")[0]
    #     if name not in names:
    #         names.append(name)
    # for name in names:
    #     print(name)

    for xml_file in list(get_xml_files(directory))[:1000]:
        tags = parse_xml(xml_file)
        for tag_name, tag_data in tags.items():
            merge_dicts(all_tags[tag_name], tag_data)

    # Конвертировать в JSON
    with open('output.json', 'w', encoding='utf-8') as json_file:
        json.dump(all_tags, json_file, ensure_ascii=False, indent=4)

    # Конвертировать в YAML (если нужно)
    # with open('output.yaml', 'w', encoding='utf-8') as yaml_file:
    #     yaml.dump(all_tags, yaml_file, allow_unicode=True)

    # print(json.dumps(all_tags, ensure_ascii=False, indent=4))
