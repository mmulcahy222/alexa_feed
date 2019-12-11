
import urllib2
import re
import json
import os, sys
import xml.etree.ElementTree as et
import newspaper


def lambda_handler(event, context):
    # if (event["session"]["application"]["applicationId"] != "amzn1.ask.skill.17266258-eecf-42a5-a328-b235199a76ef"):
    #     raise ValueError("Invalid Application ID")
     #give value if doesn't exist for the future
    
    #expected to have an exception in the first go.
    try:
        intro_text = ''
        #session attributes
        request_session_attributes = event["session"]["attributes"]
        list_of_links = request_session_attributes['list_of_links']
        list_of_links = json.loads(list_of_links)
        link_location = request_session_attributes['link_location']
        continue_variable = request_session_attributes['continue_variable']
        location = request_session_attributes['location']
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print str(exc_type) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno)
        link_location = 0
        list_of_links = []
        location = 'edmonton'
        continue_variable = 0
   
   
    
    #only do if there's no links already or first time
    intent_name = event["request"]["intent"]["name"]
    
    if intent_name != 'AMAZON.NextIntent' and intent_name != 'AMAZON.PreviousIntent' and intent_name != 'ContinueIntent':
        link_location = 0
        if intent_name == "GetArticleByNumber":
            link_location = get_slot_value('number',event)
        #get rss link from new paltz artist
        rss_json_link = 'http://newpaltzartist.com/delphium/rss.txt'
        npa_delphium_response = urllib2.urlopen(rss_json_link).read().replace('\n','').replace('\t','')
        dict_of_rss = json.loads(npa_delphium_response)
        location = get_slot_value('query',event).lower().replace(' ','_')
        intro_text += location
        rss_link = str(dict_of_rss[location])
        #get rss
        req = urllib2.Request(rss_link)
        req.add_header('Upgrade-Insecure-Requests',1)
        req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36')
        req.add_header('Referer','https://www.google.com')
        req.add_header('Accept','application/atom+xml,application/rdf+xml,application/rss+xml,application/xml,text/xml')
        rss_response = urllib2.urlopen(req).read().replace('\n',' ').replace('\t',' ')
        #get links from rss
        tree = et.fromstring(rss_response)
        list_of_links = tree.findall('./channel/item/link')
        list_of_links = [link.text for link in list_of_links]
    number_of_links = len(list_of_links)
    
    #handle continue variable behavior
    if intent_name == 'ContinueIntent':
        continue_variable += 1
    else:
        continue_variable = 0

    #response_session_attributes (will never be called on first go)
    if intent_name == 'AMAZON.NextIntent':
        if link_location < number_of_links:
            link_location += 1
    if intent_name == 'AMAZON.PreviousIntent':
        if link_location > 0:
            link_location -= 1
    
            
    try:
        article_link = list_of_links[link_location]
    except:
        link_location = 0
        article_link = 'http://abcnews.go.com/Lifestyle/inside-santa-claus-cozy-north-pole-home-valued/story?id=44008417'
   
    intro_text = (location.replace('_',' ') + " Enjoy article " + str(link_location) + " in " + str(number_of_links) + " total links. ")
    
    #response session attributes
    response_session_attributes = {'list_of_links':json.dumps(list_of_links),'link_location':link_location, 'location':location, 'article_link':article_link, "continue_variable": continue_variable}
        
    if event["session"]["new"]:
        print "Starting new session."
    if event["request"]["type"] == "LaunchRequest":
        return build_response('wa' * 30, 0, list, response_session_attributes)
    elif event["request"]["type"] == "IntentRequest": 
        if intent_name == "GetTest":
            return build_response('wa' * 30, 0, response_session_attributes)
        elif intent_name == "GetFeed":
            link_location = 0
            return build_response(intro_text + newspaper_read(article_link,continue_variable), 0, response_session_attributes)
        elif intent_name == "GetArticleByNumber":
            return build_response(intro_text + newspaper_read(article_link,continue_variable), 0, response_session_attributes)
        elif intent_name == "AMAZON.HelpIntent":
            return build_response('You Want Help', 0)
        elif intent_name == "ContinueIntent":
             return build_response(intro_text + newspaper_read(article_link,continue_variable), 0, response_session_attributes)
        elif intent_name == "AMAZON.NextIntent":
            return build_response(intro_text + newspaper_read(article_link,continue_variable), 0, response_session_attributes)
        elif intent_name == "AMAZON.PreviousIntent":
            return build_response(intro_text + newspaper_read(article_link,continue_variable), 0, response_session_attributes)
        elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
             return build_response('Thank you for using Goon. See you next time!', 1,response_session_attributes)


def newspaper_read(article_link,continue_var=0):
    #continue variables
    max_allowed = 7999
    start_character = max_allowed * continue_var
    end_character = start_character + max_allowed
    text = ''
    n_entity = newspaper.Article(article_link)
    n_entity.download()
    n_entity.parse()
    text += (n_entity.text.encode('ascii',errors='ignore').replace('\n','').replace('\t',''))[start_character:end_character]
    return text

def get_slot_value(name, event):
    print name
    slot = event.get('request').get('intent').get('slots').get(name)
    if slot is not None:
        slot_value = slot.get('value')
        if slot_value is not None:
            if slot_value.isdigit() is True:
                return int(slot_value)
            else:
                return str(slot_value)
        else:
            return 0
    else:
        return 0

def build_response(speech_output, should_end_session, session_attributes = {}):
    
    #response
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": speech_output[:7999]
            }, 
            "shouldEndSession": should_end_session
        }
    }