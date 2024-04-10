import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler
from wagtail.core import hooks


@hooks.register('register_rich_text_features')
def register_bluehighlight_feature(features):
    feature_name = 'cm_blue'
    type_ = 'BLUE_HIGHLIGHT'
    tag = f'span'

    control = {
        'type': type_,
        'label': '🟦',
        'description': 'Blue gradient highlight',
        'style': {'color': '#337ab7'},
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(control)
    )

    db_conversion = {
        'from_database_format': {'span[class="text-primary"]': InlineStyleElementHandler(type_)},
        'to_database_format': {
            'style_map': {
                type_: {
                    'element': tag,
                    'props': {
                        'class': 'text-primary'
                    }
                }
            }
        },
    }

    features.register_converter_rule('contentstate', feature_name, db_conversion)


@hooks.register('register_rich_text_features')
def register_redhighlight_feature(features):
    feature_name = 'cm_red'
    type_ = 'RED_HIGHLIGHT'
    tag = f'span'

    control = {
        'type': type_,
        'label': '🟥',
        'description': 'Red gradient highlight',
        'style': {'color': '#ed1c24'},
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(control)
    )

    db_conversion = {
        'from_database_format': {'span[class="text-danger"]': InlineStyleElementHandler(type_)},
        'to_database_format': {
            'style_map': {
                type_: {
                    'element': tag,
                    'props': {
                        'class': 'text-danger'
                    }
                }
            }
        },
    }

    features.register_converter_rule('contentstate', feature_name, db_conversion)


@hooks.register('register_rich_text_features')
def register_orangehighlight_feature(features):
    feature_name = 'cm_orange'
    type_ = 'ORANGE_HIGHLIGHT'
    tag = f'span'

    control = {
        'type': type_,
        'label': '🟧',
        'description': 'Orange gradient highlight',
        'style': {'color': '#f28b1a'},
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(control)
    )

    db_conversion = {
        'from_database_format': {'span[class="text-orange"]': InlineStyleElementHandler(type_)},
        'to_database_format': {
            'style_map': {
                type_: {
                    'element': tag,
                    'props': {
                        'class': 'text-orange'
                    }
                }
            }
        },
    }

    features.register_converter_rule('contentstate', feature_name, db_conversion)


@hooks.register('register_rich_text_features')
def register_greenhighlight_feature(features):
    feature_name = 'cm_green'
    type_ = 'GREEN_HIGHLIGHT'
    tag = f'span'

    control = {
        'type': type_,
        'label': '🟩',
        'description': 'Green gradient highlight',
        'style': {'color': '#28a745'},
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(control)
    )

    db_conversion = {
        'from_database_format': {'span[class="text-success"]': InlineStyleElementHandler(type_)},
        'to_database_format': {
            'style_map': {
                type_: {
                    'element': tag,
                    'props': {
                        'id': type_,
                        'class': 'text-success'
                    }
                }
            }
        },
    }

    features.register_converter_rule('contentstate', feature_name, db_conversion)