"""
Query can be like this:
[
('wgt', '800px', '320px'),
('vlt', '321px', '100%'),
(None, None, '1px')
]
"""

def parsed_media_query_to_str(media_query:list) -> str:
    result = ''
    for type_name, type_details, size in media_query:
        if type_name is not None and type_name != '':
            result += f'({type_name}: {type_details}) {size}, '
        else:
            result += f'{size}, '
    return result[:-2]
