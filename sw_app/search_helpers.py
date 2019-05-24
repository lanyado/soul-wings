import json
import requests
import secrets


def perform_search(search_term):
    """
    Perform search with Azure Search API and return formatted results
    """

    url = "https://soulwings.search.windows.net/indexes/azureblob-index-last/docs"
    headers = {
      "api-key": secrets.AZ_SEARCH_API_KEY,
      "Content-Type": "application/json"
    }
    params = {
      "api-version": "2019-05-06",
      "search": search_term
    }
    response_json = requests.get(url, params=params, headers=headers).json()
    res = response_json['value']

    return format_search_res(search_term, res)


def format_search_res(search_term, res):
    """
    Format results for UI
    """

    frmt_res = []

    for obj in res:
        frmt_obj = {}
        for k, v in obj.get('user_fields', {}).iteritems():
            frmt_obj[k] = v

        frmt_obj['url'] = gen_url(obj)
        contents = format_contents(search_term, obj.get('results', []))
        frmt_obj['contents'] = contents
        frmt_res.append(frmt_obj)

    return frmt_res


def gen_url(obj):
    """
    Generate URL based on filename
    """

    url_prefix = "https://soulwings.blob.core.windows.net/videos/"

    obj_file_name = obj['metadata_storage_name']
    vid_file_name = obj_file_name.split(".")[0] + '.mp4'

    return url_prefix + vid_file_name


def format_contents(search_term, res):
    """
    Format Google STT API result for UI
    """

    contents = []
    words_def = [{'endTime': "5.9s",
                 'word': 'def',
                 'startTime': '5.3s'}]

    for phrase_obj in res:
        alternatives = phrase_obj.get('alternatives')
        for alt in alternatives:
            transcript = alt.get('transcript', '').encode('utf-8')
            words = alt.get('words', words_def)
            if search_term in transcript:
                match = {'text': transcript,
                         'timing': words[0].get('startTime', '')}
                contents.append(match)
                continue

    return contents
