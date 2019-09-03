this.Urls=(function(){"use strict";var data={"urls":[["api:get_lesson_content",[["api/get_lesson_content/%(n)s/%(render_pdf)s/",["n","render_pdf"]]]],["notifications:check_list",[["api/check_notifications/",[]]]],["notifications:check_pk",[["api/check_notification/%(pk)s/",["pk"]]]],["notifications:get",[["api/get_notifications/",[]]]],["notifications:get_drop_content_html",[["api/get_drop_content_html/",[]]]],["notifications:get_new",[["api/get_new_notifications/",[]]]],["notifications:get_new_count",[["api/get_new_notifications_count/",[]]]]],"prefix":"/"};function factory(d){var url_patterns=d.urls;var url_prefix=d.prefix;var Urls={};var self_url_patterns={};var _get_url=function(url_pattern){return function(){var _arguments,index,url,url_arg,url_args,_i,_len,_ref,_ref_list,match_ref,provided_keys,build_kwargs;_arguments=arguments;_ref_list=self_url_patterns[url_pattern];if(arguments.length==1&&typeof(arguments[0])=="object"){var provided_keys_list=Object.keys(arguments[0]);provided_keys={};for(_i=0;_i<provided_keys_list.length;_i++)
provided_keys[provided_keys_list[_i]]=1;match_ref=function(ref)
{var _i;if(ref[1].length!=provided_keys_list.length)
return false;for(_i=0;_i<ref[1].length&&ref[1][_i]in provided_keys;_i++);return _i==ref[1].length;}
build_kwargs=function(keys){return _arguments[0];}}else{match_ref=function(ref)
{return ref[1].length==_arguments.length;}
build_kwargs=function(keys){var kwargs={};for(var i=0;i<keys.length;i++){kwargs[keys[i]]=_arguments[i];}
return kwargs;}}
for(_i=0;_i<_ref_list.length&&!match_ref(_ref_list[_i]);_i++);if(_i==_ref_list.length)
return null;_ref=_ref_list[_i];url=_ref[0],url_args=build_kwargs(_ref[1]);for(url_arg in url_args){var url_arg_value=url_args[url_arg];if(url_arg_value===undefined||url_arg_value===null){url_arg_value='';}else{url_arg_value=url_arg_value.toString();}
url=url.replace("%("+url_arg+")s",url_arg_value);}
return url_prefix+url;};};var name,pattern,url,_i,_len,_ref;for(_i=0,_len=url_patterns.length;_i<_len;_i++){_ref=url_patterns[_i],name=_ref[0],pattern=_ref[1];self_url_patterns[name]=pattern;url=_get_url(name);Urls[name.replace(/[-_]+(.)/g,function(_m,p1){return p1.toUpperCase();})]=url;Urls[name.replace(/-/g,'_')]=url;Urls[name]=url;}
return Urls;}
return data?factory(data):factory;})();