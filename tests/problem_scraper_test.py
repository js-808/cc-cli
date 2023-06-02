from cp_cli import problem_scraper


def test_scraper_get_chapter_html():
    # Get sample HTML
    test_chapter = 'ch4'
    test_judge = 'uva'
    try:
        # Ensure output is of proper format
        output = problem_scraper.get_chapter_html(test_chapter, test_judge)
        assert type(output) is str
        assert output != ''
    except Exception:
        assert False
