from bs4 import BeautifulSoup
from bs4.element import Tag 
from typing import *
import json
import requests 
import time
import os

CPBOOK_PROBLEMS_URL = 'https://cpbook.net/methodstosolve'

class InvalidRequestException(Exception):
    """An exception raised if a HTTP request is returned with a 400-level response."""
    pass


# --------------------- WEB SCRAPING HELPER FUNCTIONS ---------------------
def is_starred(row: Tag) -> bool:
    """Return whether or not a problem is starred in the CP4 book.
    
    Parmaeters:
        problem_class (Tag): The Tag representing the <tr> HTML tag for a problem
    
    Return:
        bool: Whether or not the problem is starred.
    """
    return 'class' in row.attrs and 'starred' in row.attrs['class']


def parse_problem_description(desc_str: str) -> Union[str, str, str]:
    """Parse the problem description to get the section, subsection, and subsection title.
    
    Parameters:
        desc_str (str): A string of the form '{chapter_no}.{section_no}{subsection_letter}, {Subsection Title}'
    
    Returns:
        str: Fully qualified section '{chapter_no}.{section_no}'
        str: Fully qualified subsection '{chapter_no}.{section_no}{subsection_letter}`
        str: Subsection title  
    """
    # Split off the subsection title and everything else 
    comma_split = desc_str.split(',') 
    section_stuff = comma_split[0]
    subsection_title = ','.join(comma_split[1:]).strip()
    
    # Split off the chapter number and everything else 
    chapter_no, subsection_stuff = tuple(section_stuff.split('.')) 

    # Get the section number and subsection letter 
    # by iterating until there is no more numeric characters
    i = 1
    while subsection_stuff[:i].isdigit():    # Will always execute at least once
        i += 1 
    section_no = subsection_stuff[:i-1]
    subsection_letter = subsection_stuff[i-1:]

    # Get fully qualified return items 
    fully_qual_sect = f'{chapter_no}.{section_no}'
    fully_qual_subsect = f'{chapter_no}.{section_no}{subsection_letter}'

    return fully_qual_sect, fully_qual_subsect, subsection_title


def parse_all_problems(soup: BeautifulSoup) -> Dict:
    """Get a list of all of the problems on a given cpbook.net webpage.
    
    Parameters:
        soup (BeautifulSoup): A soup representation of the webpage.
    """
    # Get all rows from the 'problemtable' <table> tag
    table = soup.find("table", {'id':'problemtable'})
    body = table.find('tbody')
    rows = body.findAll('tr') 

    # Parse out each problem individually
    problems = dict()
    for row in rows:
        problem = row.findAll('td')

        # Get the problem id (for either Kattis or UVa)
        problem_id = problem[0].text 

        # Parse the problem description to get the section, subsection, and subection title
        # of the problem. Create JSON structure if needed.
        problem_info = problem[2].text
        fully_qual_sect, fully_qual_subsect, subsection_title = parse_problem_description(problem_info)
        if fully_qual_sect not in problems:
            problems[fully_qual_sect] = dict()
        if fully_qual_subsect not in problems[fully_qual_sect]:
            problems[fully_qual_sect][fully_qual_subsect] = {
                'title': subsection_title,
                'probs': {
                    'starred': [],
                    'extra': []
                }
            } 
        
        # Add this problem to the JSON.
        probs = problems[fully_qual_sect][fully_qual_subsect]['probs']
        if is_starred(row):
            probs['starred'].append(problem_id)
        else:
            probs['extra'].append(problem_id)
    
    return problems 


def get_chapter_html(chapter: str, online_judge: str) -> str:
    """Get a JSON representation of CP4 problems in a given chapter.
    
    Parameters:
        chapter (int): The chapter string to query
        online_judge (str): The online judge to query
        
    Returns:
        str: The HTML of the corresponding chapter's problems

    Raises:
        InvalidRequestException: If a non-200 response is given by cpbook.net
    """
    params = {
        'oj': online_judge,
        'topic': chapter,
        'quality': 'all'
    }

    # Get the webpage corresponding to this chapter and online judge.
    response = requests.get(CPBOOK_PROBLEMS_URL, params=params) 
    if not response.ok:
        msg = f"Error: Bad response from {response.url}."
        msg += f" Info: {response.status_code}: {response.reason}"
        raise InvalidRequestException(msg)

    return response.text 



# --------------------- JSON FORMATTING HELPER FUNCTIONS ----------------------
def validify(s: str) -> str:
    """Replaces invalid characters for filepath names with either empty 
    strings or spaces (for readability).
    
    Parameters:
        s (str): The string to edit.
        
    Returns:
        str: s with all invalid characters replaced/removed.
    """
    # Replace all invalid characters with appropriate replacements
    replacements = {
        '/': '_', 
        '\\': '_',
        '.': '_', 
        '\'': '',
        ' ': '_',
        ',': '_',
        '\n': '_', 
        '&': '',
        '+': '',
        '(': '',
        ')': '',
        '~': '',
        '*': '',
        ':': '_',
        '-': '_'
    }
    for c, repl in replacements.items():
        if c in s:
            s = s.replace(c, repl)
    
    # Get rid of too many underscores (if needed)
    while '__' in s:
        s = s.replace('__', '_')

    # Return the resulting valid string
    return s 


def get_formatted_problem_info(section_root: dict) -> dict:
    """Format a section's title, kattis, and uva problem information.
    
    Parameters:
        section_root (dict): A dictionary. Should have key 'title', and 
            might have keys 'kattis' or 'uva' with appropriate sub-dictionaries
            if appropriate.
    
    Returns: 
        dict: An output dictionary with formatted section titles.
    """
    output = dict()
    for section, section_stuff in section_root.items():
        section_title = section_stuff['title']
        new_section_title = validify(" ".join([section, section_title]))
        output[new_section_title] = dict() 
        if 'uva' in section_stuff:
            output[new_section_title]['uva'] = section_stuff['uva']
        if 'kattis' in section_stuff:
            output[new_section_title]['kattis'] = section_stuff['kattis']
    return output


def reformat_book_json(book_json: Dict) -> Dict:
    """Reformat the book JSON for easier use in creating file structures."""

    # Get chapter information from book 
    script_folder = os.path.dirname(os.path.abspath(__file__))
    book_section_names = os.path.join(script_folder, 'book_section_names.json')
    with open(book_section_names, 'r') as infile:
        chapter_info = json.load(infile)
    
    # Chapter 9: Remove extraneous layer created by different HTML class setup
    ch_9_sections = book_json['ch9']['9.']
    book_json['ch9'] = ch_9_sections

    # Chapter 9: Rename each of the sections to be numeric rather than alphabetic
    for section in list(book_json['ch9']):
        section_info = book_json['ch9'].pop(section)
        new_section_name = chapter_info['ch9']['sections'][section]
        book_json['ch9'][new_section_name] = section_info 
    
    # All chapters: Reformat chapter and section names 
    new_book_json = dict() 
    for chapter in book_json:
        ch_stuff = chapter_info[chapter]
        ch_title = ch_stuff['title']
        ch_sections = ch_stuff['sections']

        # Get valid chapter full name 
        chapter_full_name = validify(" ".join([chapter, ch_title]))
        new_book_json[chapter_full_name] = dict() 

        if chapter == 'ch9':
            # Chapter 9 had weird stuff going on since its the "rare problems" chapter
            # so we have one less layer. We parse it appropriately.
            new_book_json[chapter_full_name] = get_formatted_problem_info(book_json[chapter])
        else:
            for section, section_stuff in book_json[chapter].items():
                new_section_title = validify(ch_sections[section])
                new_book_json[chapter_full_name][new_section_title] = get_formatted_problem_info(section_stuff)
    
    return new_book_json



# ------------------- MAIN FUNCTION FOR GETTING PROBLEM JSON ------------------
def get_book_json() -> Dict:
    """Get a JSON representation for all problems in the CP4 Book.
    
    Returns:
        Dict: A dictionary/JSON representation of all the problems in CP4.
    """
    print("Getting CP4 book problem JSON.")
    book_problem_json = dict()
    for chapter in range(1,10):
        chapter_str = f'ch{chapter}'    # In the format needed for query URL string
        print(f"Getting JSON for {chapter_str}")

        # Get the BeautifulSoup representation of this chapter's problems
        # for the corresponding online judges
        uva_html = get_chapter_html(chapter_str, 'uva')
        uva_soup = BeautifulSoup(uva_html, 'html.parser')
        kattis_html = get_chapter_html(chapter_str, 'kattis')
        kattis_soup = BeautifulSoup(kattis_html, 'html.parser')

        # Parse all of the problems for each online judge in this chapter
        uva_problems = parse_all_problems(uva_soup)
        kattis_problems = parse_all_problems(kattis_soup)

        # Formulate the book problem JSON for this chapter
        book_problem_json[chapter_str] = dict() 
        for section in set(uva_problems).union(set(kattis_problems)):
            book_problem_json[chapter_str][section] = dict()
            for subsection in set(uva_problems[section]).union(set(kattis_problems[section])):
                if subsection not in uva_problems[section]:
                    book_problem_json[chapter_str][section][subsection] = {
                        'title': kattis_problems[section][subsection]['title'], 
                        'kattis': kattis_problems[section][subsection]['probs']
                    }
                elif subsection not in kattis_problems[section]:
                    book_problem_json[chapter_str][section][subsection] = {
                        'title': uva_problems[section][subsection]['title'], 
                        'uva': uva_problems[section][subsection]['probs']
                    }
                else:
                    book_problem_json[chapter_str][section][subsection] = {
                        'title': uva_problems[section][subsection]['title'], 
                        'uva': uva_problems[section][subsection]['probs'],
                        'kattis': kattis_problems[section][subsection]['probs']
                    }

        # Rate limit a bit after each chapter (maybe unneccessary,
        # but I don't want to overload their servers in any case)
        time.sleep(3)
    
    # Reformat the book JSON to have a nicer ability to use with file names 
    print("Formatting JSON . . .")
    formatted_book_json = reformat_book_json(book_problem_json)
    return formatted_book_json


# ------------------- DRIVER (Runs when .py file is called) -------------------
if __name__ == "__main__":
    book_json = get_book_json()
    script_folder = os.path.dirname(os.path.abspath(__file__))
    out_json_file = os.path.join(script_folder, 'problems.json')
    with open(out_json_file, 'w') as outfile:
        json.dump(book_json, outfile, indent=4)
    print(f"Output written to {out_json_file}")



