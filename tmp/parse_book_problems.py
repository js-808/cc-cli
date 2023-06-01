from bs4 import BeautifulSoup
from bs4.element import Tag 
from typing import *
import json
import requests 
import time

CPBOOK_PROBLEMS_URL = 'https://cpbook.net/methodstosolve'

class InvalidRequestException(Exception):
    """An exception raised if a HTTP request is returned with a 400-level response."""
    pass

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
        if is_starred(row):
            problems[fully_qual_sect][fully_qual_subsect]['probs']['starred'].append(problem_id)
        else:
            problems[fully_qual_sect][fully_qual_subsect]['probs']['extra'].append(problem_id)
    
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
        msg = f"Error: Bad response from {response.url}. Info: {response.status_code}: {response.reason}"
        raise InvalidRequestException(msg)

    return response.text 

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

    return book_problem_json

if __name__ == "__main__":
    book_json = get_book_json()
    out_json_file = 'book_problems_basic.json'
    with open(out_json_file, 'w') as outfile:
        json.dump(book_json, outfile, indent=4)
    print(f"Output written to {out_json_file}")



