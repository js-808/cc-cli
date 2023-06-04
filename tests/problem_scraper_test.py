from cp_cli import problem_scraper
import pytest
from bs4 import BeautifulSoup
import os


@pytest.mark.vcr
class TestProblemHTMLScraper:
    """A class to test all helper functions that parse HTML
    about CP4 book problems directly from the book website."""

    @pytest.fixture
    def vcr_cassette_name(self):
        parent_dir = os.path.dirname(__file__)
        return os.path.join(parent_dir, 'cassettes', 'ch4_probs')

    def test_parse_problem_description(self):
        """Test to ensure problem descriptions are parsed appropriately."""
        # Set up a sample problem description
        chapter_num = 5
        section_num = 4
        subsection_letter = 'a'
        subsection_title = 'Test Subsection Title'
        full_desc = (f'{chapter_num}.{section_num}{subsection_letter}, '
                     f'{subsection_title}')

        # Test parsing this sample description. Ensure length and type of
        # output is correct
        res = problem_scraper.parse_problem_description(full_desc)
        assert len(res) == 3
        for r in res:
            assert type(r) is str

        # Assert format of output is correct
        assert res[0] == f'{chapter_num}.{section_num}'
        assert res[1] == f'{chapter_num}.{section_num}{subsection_letter}'
        assert res[2] == subsection_title.strip()

    def test_scraper_get_valid_chapter_html(self):
        """Test that the web scraper can get a webpage from valid parameters"""
        # Get sample HTML (ensure no exception is thrown)
        test_chapter = 'ch4'
        test_judge_1 = 'uva'
        test_judge_2 = 'kattis'
        try:
            # Ensure output is of proper format (nonempty string)
            output = problem_scraper.get_chapter_html(test_chapter,
                                                      test_judge_1)
            assert type(output) is str
            assert output != ''
            output = problem_scraper.get_chapter_html(test_chapter,
                                                      test_judge_2)
            assert type(output) is str
            assert output != ''
        except problem_scraper.InvalidRequestException:
            assert False

    def test_parse_all_problems(self):
        """Test that the scraper can get lists of all problems correctly from
        the given webpage"""
        # Get HTML pages and put them in beautiful soup objects
        test_chapter = 'ch4'
        uva_html = problem_scraper.get_chapter_html(test_chapter, 'uva')
        uva_soup = BeautifulSoup(uva_html, 'html.parser')
        kattis_html = problem_scraper.get_chapter_html(test_chapter, 'kattis')
        kattis_soup = BeautifulSoup(kattis_html, 'html.parser')

        # Parse the problems from this soup
        uva_problems = problem_scraper.parse_all_problems(uva_soup)
        kattis_problems = problem_scraper.parse_all_problems(kattis_soup)

        # Test that both of these dictionaries is formatted correctly
        for problems in [uva_problems, kattis_problems]:
            for key in ['4.2', '4.3', '4.4', '4.5', '4.6']:
                assert key in problems
                if key == '4.2':
                    for sub_key in ['4.2a', '4.2b', '4.2c', '4.2d', '4.2e',
                                    '4.2f', '4.2g', '4.2h']:
                        assert sub_key in problems[key]
                        if sub_key == '4.2a':
                            assert 'title' in problems[key][sub_key]
                            assert 'probs' in problems[key][sub_key]
                            sub_dict = problems[key][sub_key]
                            assert type(sub_dict['probs']) is dict
                            assert 'starred' in sub_dict['probs']
                            assert 'extra' in sub_dict['probs']
                            assert type(sub_dict['probs']['starred']) is list
                            assert type(sub_dict['probs']['extra']) is list

    def test_is_starred(self):
        """Test to ensure a given problem is starred or not."""
        # Get soup representation of chapter 4 uva problems
        uva_html = problem_scraper.get_chapter_html('ch4', 'uva')
        uva_soup = BeautifulSoup(uva_html, 'html.parser')
        kattis_html = problem_scraper.get_chapter_html('ch4', 'kattis')
        kattis_soup = BeautifulSoup(kattis_html, 'html.parser')

        # Check that appropriate problems are starred/non-starred
        for soup in [uva_soup, kattis_soup]:
            table = soup.find("table", {'id': 'problemtable'})
            body = table.find('tbody')
            rows = body.findAll('tr')

            for row in rows:
                if 'class' not in row.attrs:
                    assert not problem_scraper.is_starred(row)
                elif 'starred' in row['class']:
                    assert problem_scraper.is_starred(row)
                else:
                    assert not problem_scraper.is_starred(row)


class TestReformatJSON:
    """Tests all classes that reformat web-parsed JSON to a nicer format."""

    @pytest.fixture
    def sample_json(self):
        return {
            "ch4": {
                "4.5": {
                    "4.5a": {
                        "title": "APSP, Standard",
                        "uva": {
                            "starred": [
                                "00821",
                                "01247",
                                "10354",
                                "11463"
                            ],
                            "extra": [
                                "00341",
                                "00567",
                                "01233",
                                "10171",
                                "10525",
                                "10724",
                                "10793",
                                "10803",
                                "10947",
                                "11015",
                                "12319",
                                "13249"
                            ]
                        },
                        "kattis": {
                            "starred": [
                                "allpairspath",
                                "importspaghetti",
                                "transportationplanning"
                            ],
                            "extra": [
                                "slowleak"
                            ]
                        }
                    },
                    "4.5b": {
                        "title": "APSP, Variants",
                        "uva": {
                            "starred": [
                                "00869",
                                "01056",
                                "10342",
                                "10987"
                            ],
                            "extra": [
                                "00104",
                                "00125",
                                "00186",
                                "00274",
                                "00334",
                                "00436",
                                "00925",
                                "01198",
                                "01757",
                                "10246",
                                "10331",
                                "10436",
                                "11047"
                            ]
                        },
                        "kattis": {
                            "starred": [
                                "arbitrage",
                                "kastenlauf",
                                "secretchamber"
                            ],
                            "extra": [
                                "assembly",
                                "isahasa"
                            ]
                        }
                    }
                }
            }
        }

    @pytest.mark.parametrize("s", [
        "my_test",
        "my test",
        "my/test",
        "my  test",
        "my & test",
        "my \n test",
        "my\\test",
        "my: test"
    ])
    def test_validify(self, s):
        """Test that the validify() function gets correct underscores/empty
        strings for invalid characters."""
        assert problem_scraper.validify(s) == 'my_test'

    def test_get_formatted_problem_info(self, sample_json):
        sample_section = sample_json['ch4']['4.5']
        reformat = problem_scraper.get_formatted_problem_info(sample_section)
        for title in ['4_5a_APSP_Standard', '4_5b_APSP_Variants']:
            assert title in reformat
        subsect = reformat['4_5a_APSP_Standard']
        assert 'uva' in subsect
        assert 'kattis' in subsect
        uva = subsect['uva']
        assert 'starred' in uva
        assert 'extra' in uva
        assert type(uva['starred']) is list
        assert type(uva['extra']) is list

    def test_reformat_book_json(self, sample_json):
        reformatted = problem_scraper.reformat_book_json(sample_json)
        assert 'ch4_Graph' in reformatted
        assert '4_5_All_Pairs_Shortest_Paths_APSP' in reformatted['ch4_Graph']
