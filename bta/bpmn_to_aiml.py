import xml.etree.ElementTree as ET
import os
import re


def get_next_vertice(bpmn_root, aresta):
    # verificar porque esta fazendo o loop em todos os elementos  ideal seria somente em tasks e gateway e talvez start_event
    for vertice in bpmn_root:
        if vertice.attrib['id'] == aresta.attrib['pos']:
            return vertice


def get_next_aresta(root_bpmn, vertice):
    for aresta in root_bpmn.findall("edge"):
        if vertice.attrib['id'] == aresta.attrib['ant']:
            return aresta


def get_ant_vertice(root_bpmn, aresta):
    for vertice in root_bpmn:
        if vertice.attrib['id'] == aresta.attrib['ant']:
            return vertice


def get_pos_vertice(root_bpmn, aresta):
    for vertice in root_bpmn:
        if vertice.attrib['id'] == aresta.attrib['pos']:
            return vertice


def get_node(root_bpmn, node_id):
    for node in root_bpmn:
        if node.attrib['id'] == node_id:
            return node
    return None


def get_association_node(root_bpmn, gateway):
    for node in root_bpmn:
        if node.tag == "association":
            if node.attrib['ant'] == gateway.attrib['id']:
                return node
    return None


def get_template_text_with_variable(phrase):
    matches = re.findall(r"[$]\w*\w", phrase)
    for match in matches:
         variavel = match.replace('_', '').replace('(', '').replace(')', '').replace('$', '')
         phrase = phrase.replace(match, '<get name="' + variavel + '" />')
    return phrase


def get_arestas_from_gateway(root_bpmn, gateway):
    arestas = []
    for aresta in root_bpmn.findall("edge"):
        if aresta.attrib["ant"] == gateway.attrib["id"]:
            arestas.append(aresta)
    return arestas


def is_phrase_only_with_variable(phrase):
    match = re.search(r"[$]\w*\w", phrase)
    return match


def get_end_out_topic(phrase):
    saida = '<think><set name="topic"></set></think>{}'.format(phrase)
    return saida


def get_condition(root_bpmn, pos):
    phrase = pos.attrib['name']
    variavel = phrase.replace('_', '').replace('(', '').replace(')', '').replace('$', '')
    arestas = get_arestas_from_gateway(root_bpmn, pos)
    condition_begin = '''<condition name="{}">'''.format(variavel)
    condition_li_values = ""
    for aresta in arestas:
        srai_name_task = aresta.attrib["name"].replace('_', '').replace('(', '').replace(')', '').replace('$', '')
        srai_redirect = aresta.attrib["id"].replace('_', '').replace('(', '').replace(')', '').replace('$', '')
        condition_li_values = condition_li_values + '<li value="{}"><srai>{}</srai></li>'.format(srai_name_task, srai_redirect)
    condition_end = '''</condition>'''
    new_phrase = condition_begin + condition_li_values + condition_end
    return new_phrase


def create_category(root_aiml, topic_name, pattern_text, template_text, that_text, srai_text, set_name, set_value):
    # if topic_name is not None:
    #     topic = ET.SubElement(root_aiml, 'topic')
    #     topic.set("name", topic_name)
    category = ET.SubElement(root_aiml, 'category')
    pattern = ET.SubElement(category, 'pattern')
    if pattern_text is not None:
        pattern.text = pattern_text.upper().replace('_', '').replace('(', '').replace(')', '')
    else:
        pattern.text = ''
    if that_text is not None:
        that = ET.SubElement(category, 'that')
        that.text = that_text.upper().replace('_', '').replace('(', '').replace(')', '').replace('-', '').replace('?', '').replace('!', '').replace('.', '').replace(',', '')
        # that.text = re.sub('[^a-zA-Z0-9*\^ \n\.]', '', that_text.upper())
    template = ET.SubElement(category, 'template')
    if template_text is not None:
        template.text = template_text.upper().replace('.', ',') + ' '
    else:
        template.text = ''
    if set_name is not None:
        think_tag = ET.SubElement(template, 'think')
        set_tag = ET.SubElement(think_tag, 'set')
        set_tag.set('name', set_name.upper().replace('_', '').replace('(', '').replace(')', '').replace('$', ''))
        set_tag.text = set_value.upper().replace('*', '<star />')
    if srai_text is not None:
        srai = ET.SubElement(template, 'srai')
        srai.text = srai_text.upper().replace('_', '').replace('(', '').replace(')', '')



def get_topic_id(root_bpmn):
    for child in root_bpmn:
        if child.tag == 'edge':
            ant = get_ant_vertice(root_bpmn, child)
            if ant.tag == 'start_event':  # testar depois task ou esclusive gateway
                return ant.attrib["id"].upper().replace('START','BEGINNING').replace('_', '').replace('(', '').replace(')', '') # pegar o id do start event
    return "ID_NAO_ENCONTRADO"


def convert_bpmn_to_aiml(root_bpmn, root_aiml):
    topic = ET.SubElement(root_aiml, 'topic')
    topic.set("name",get_topic_id(root_bpmn))
    that_text = None
    set_name = None
    set_value = None
    srai_text = None
    # identifica primeiro o start_event
    for aresta_inicial in root_bpmn.findall("edge"):
        ant = get_ant_vertice(root_bpmn, aresta_inicial)
        pos = get_pos_vertice(root_bpmn, aresta_inicial)
        if ant.tag == 'start_event':
            pattern_text = ant.attrib['name']
            topic_name = ant.attrib['id'].upper().replace('START','BEGINNING').replace('_', '').replace('(', '').replace(')', '')
            template_text = '<think><set name="topic">{}</set></think>{}'.format(topic_name, pos.attrib["name"])
            if pos.tag == 'task':
                srai_text = pos.attrib['id']
            create_category(root_aiml, topic_name, pattern_text, template_text, that_text, srai_text, set_name, set_value)
            break

    for aresta in root_bpmn.findall("edge"):
        srai_text = None
        that_text = None
        pattern_text = None
        template_text = None
        set_name = None
        set_value = None
        ant = get_ant_vertice(root_bpmn, aresta)
        pos = get_pos_vertice(root_bpmn, aresta)
        if ant.tag == 'start_event':
            continue
        elif pos.tag == 'end_event':
            pattern_text = ant.attrib['id']
            template_text = '<think><set name="topic"></set></think>{}'.format(pos.attrib['name'])
        elif ant.tag == 'task' and pos.tag == 'task':
            pattern_text = ant.attrib['id']
            template_text = get_template_text_with_variable(pos.attrib['name'])
            srai_text = pos.attrib['id']
        elif ant.tag == 'task' and pos.tag == 'exclusive_gateway':
            pattern_text = ant.attrib['id']
            gateway_has_only_variable_in_name = is_phrase_only_with_variable(pos.attrib['name']) # é um gateway que não para
            if gateway_has_only_variable_in_name:
                template_text = get_condition(root_bpmn, pos)
            else:
                template_text = pos.attrib['name']
        elif ant.tag == 'exclusive_gateway' and (pos.tag == 'task' or pos.tag == 'exclusive_gateway'):
            for aresta_atrib_name in aresta.attrib['name'].split(','):
                gateway_has_only_variable_in_name = is_phrase_only_with_variable(ant.attrib["name"])
                if gateway_has_only_variable_in_name:
                    pattern_text = aresta.attrib['id']
                else:
                    pattern_text = aresta_atrib_name
                    that_text = '* ' + ant.attrib['name']
                if pos.tag != 'exclusive_gateway':
                    srai_text = pos.attrib['id']
                template_text = pos.attrib['name']
                association_node = get_association_node(root_bpmn, ant)
                if association_node is not None:
                    text_association_node = get_node(root_bpmn, association_node.attrib['pos'])
                    set_name = text_association_node.attrib['name']
                    set_value = aresta_atrib_name
                root_aiml = topic
                create_category(root_aiml, topic_name, pattern_text, template_text, that_text, srai_text, set_name, set_value)
            continue
        root_aiml = topic
        create_category(root_aiml, topic_name, pattern_text, template_text, that_text, srai_text, set_name, set_value)


def lower_case_some_tags(input_file_name, output_file_name):
    file = open(input_file_name, 'r', encoding="utf-8")
    regexp = re.compile(r'(NAME|SET|GET|CONDITION|LI VALUE|SRAI|THINK|STAR|TOPIC|&lt;|&gt;|&lt;LI|LI&gt;)')
    replacement_map = {
                        'NAME': 'name',
                        'SET': 'set',
                        'GET': 'get',
                        'CONDITION': 'condition',
                        'LI VALUE': 'li value',
                        'SRAI': 'srai',
                        'THINK': 'think',
                        'STAR': 'star',
                        'TOPIC': 'topic',
                        '&lt;LI': '<li',
                        'LI&gt;': 'li>',
                        '&lt;': '<',
                        '&gt;': '>',
                       }  # a dict to map a character to the replacement value.
    text = regexp.sub(lambda match: replacement_map[match.group(0)], file.read())
    file = open(output_file_name, 'w', encoding="UTF-8")
    file.write(text)


def transform_bpmn_to_aiml(input_file_name):
    path = os.path.join(input_file_name)
    caminho_absoluto = os.path.abspath(path)

    tree_bpmn = ET.parse(caminho_absoluto, ET.XMLParser(encoding='utf-8'))
    root_bpmn = tree_bpmn.getroot()

    element_aiml = ET.Element('aiml')
    tree_aiml = ET.ElementTree(element_aiml)
    root_aiml = tree_aiml.getroot()

    convert_bpmn_to_aiml(root_bpmn, root_aiml)

    # get output file name
    list_file_name = input_file_name.split('/')
    only_last_name = list_file_name[-1]

    output_file_name_xml = os.path.join("categories/" + only_last_name.split(".")[0]  + '.xml')
    output_file_name_aiml = os.path.join("data/" + only_last_name.split(".")[0] + '.aiml')

    path_saida = os.path.join(output_file_name_xml)
    caminho_absoluto_saida = os.path.abspath(path_saida)

    tree_aiml.write(caminho_absoluto_saida, encoding="UTF-8",xml_declaration=True)
    lower_case_some_tags(output_file_name_xml, output_file_name_aiml)

    # faz uma copia para a pasta static
    output_file_static_name_aiml = os.path.join("static/diagram.aiml")
    tree_aiml.write(output_file_static_name_aiml, encoding="UTF-8",xml_declaration=True)
    lower_case_some_tags(output_file_static_name_aiml, output_file_name_aiml)



