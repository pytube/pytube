import ast
import json
import re
from pytube.exceptions import HTMLParseError


def parse_for_all_objects(html, preceding_regex):
    """Parses input html to find all matches for the input starting point.

    :param str html:
        HTML to be parsed for an object.
    :param str preceding_regex:
        Regex to find the string preceding the object.
    :rtype list:
    :returns:
        A list of dicts created from parsing the objects.
    """
    result = []
    regex = re.compile(preceding_regex)
    match_iter = regex.finditer(html)
    for match in match_iter:
        if match:
            start_index = match.end()
            try:
                obj = parse_for_object_from_startpoint(html, start_index)
            except HTMLParseError:
                # Some of the instances might fail because set is technically
                # a method of the ytcfg object. We'll skip these since they
                # don't seem relevant at the moment.
                continue
            else:
                result.append(obj)

    if len(result) == 0:
        raise HTMLParseError(f'No matches for regex {preceding_regex}')

    return result


def parse_for_object(html, preceding_regex):
    """Parses input html to find the end of a JavaScript object.

    :param str html:
        HTML to be parsed for an object.
    :param str preceding_regex:
        Regex to find the string preceding the object.
    :rtype dict:
    :returns:
        A dict created from parsing the object.
    """
    regex = re.compile(preceding_regex)
    result = regex.search(html)
    if not result:
        raise HTMLParseError(f'No matches for regex {preceding_regex}')

    start_index = result.end()
    return parse_for_object_from_startpoint(html, start_index)


def find_object_from_startpoint(html, start_point):
    """Parses input html to find the end of a JavaScript object.

    :param str html:
        HTML to be parsed for an object.
    :param int start_point:
        Index of where the object starts.
    :rtype dict:
    :returns:
        A dict created from parsing the object.
    """
    html = html[start_point:]
    if html[0] not in ['{','[']:
        raise HTMLParseError(f'Invalid start point. Start of HTML:\n{html[:20]}')

    # First letter MUST be a open brace, so we put that in the stack,
    # and skip the first character.
    last_char = '{'
    curr_char = None
    stack = [html[0]]
    i = 1

    context_closers = {
        '{': '}',
        '[': ']',
        '"': '"',
        '/': '/' # javascript regex
    }

    while i < len(html):
        if len(stack) == 0:
            break
        if curr_char not in [' ', '\n']:
            last_char = curr_char
        curr_char = html[i]
        curr_context = stack[-1]

        # If we've reached a context closer, we can remove an element off the stack
        if curr_char == context_closers[curr_context]:
            stack.pop()
            i += 1
            continue

        # Strings and regex expressions require special context handling because they can contain
        #  context openers *and* closers
        if curr_context in ['"', '/']:
            # If there's a backslash in a string or regex expression, we skip a character
            if curr_char == '\\':
                i += 2
                continue
        else:
            # Non-string contexts are when we need to look for context openers.
            if curr_char in context_closers.keys():
                # Slash starts a regular expression depending on context
                if not (curr_char == '/' and last_char not in ['(', ',', '=', ':', '[', '!', '&', '|', '?', '{', '}', ';']): 
                    stack.append(curr_char)

        i += 1

    full_obj = html[:i]
    return full_obj  # noqa: R504


def parse_for_object_from_startpoint(html, start_point):
    """JSONifies an object parsed from HTML.

    :param str html:
        HTML to be parsed for an object.
    :param int start_point:
        Index of where the object starts.
    :rtype dict:
    :returns:
        A dict created from parsing the object.
    """
    full_obj = find_object_from_startpoint(html, start_point)
    try:
        return json.loads(full_obj)
    except json.decoder.JSONDecodeError:
        try:
            return ast.literal_eval(full_obj)
        except (ValueError, SyntaxError):
            raise HTMLParseError('Could not parse object.')


def throttling_array_split(js_array):
    """Parses the throttling array into a python list of strings.

    Expects input to begin with `[` and close with `]`.

    :param str js_array:
        The javascript array, as a string.
    :rtype: list:
    :returns:
        A list of strings representing splits on `,` in the throttling array.
    """
    results = []
    curr_substring = js_array[1:]

    comma_regex = re.compile(r",")
    func_regex = re.compile(r"function\([^)]*\)")

    while len(curr_substring) > 0:
        if curr_substring.startswith('function'):
            # Handle functions separately. These can contain commas
            match = func_regex.search(curr_substring)
            match_start, match_end = match.span()

            function_text = find_object_from_startpoint(curr_substring, match.span()[1])
            full_function_def = curr_substring[:match_end + len(function_text)]
            results.append(full_function_def)
            curr_substring = curr_substring[len(full_function_def) + 1:]
        else:
            match = comma_regex.search(curr_substring)

            # Try-catch to capture end of array
            try:
                match_start, match_end = match.span()
            except AttributeError:
                match_start = len(curr_substring) - 1
                match_end = match_start + 1

            curr_el = curr_substring[:match_start]
            results.append(curr_el)
            curr_substring = curr_substring[match_end:]

    return results
