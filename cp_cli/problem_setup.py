# cp4_problem_setup.py
"""This module helps set up file structue for practice problems."""

from typing import Optional


# -------------------- CUSTOM EXCEPTION CLASSES -------------------- #
def KattisWebAccessException(Exception):
    """An exception thrown when the Kattis website was not accessed
    successfully."""
    pass


def UVAWebAccessException(Exception):
    """An exception thrown when the UVA website was not accessed
    successfully."""
    pass


# -------------------- HELPER FUNCTIONS -------------------- #
def get_appropriate_extension(lang: str) -> str:
    """Get the appropriate file extension for a given programming language.

    Parameters:
        lang (str): The programming language

    Returns:
        str: The file extension (including the period) for files in that
            language
    """
    raise NotImplementedError("Error: get_appropriate_extension is not "
                              "implemented")


# -------------------- SINGLE PROBLEM SETUP FUNCTIONS -------------------- #
def setup_kattis_problem(root: str,
                         problem_id: str,
                         ext: Optional[str] = None):
    """Set up a directory/sample problem structure for a Kattis problem.

    The directory will be named after the problem_id, and will contain a
    sub-directory named 'test_cases'. If any sample test cases are provided,
    a sub-sub directory called 'sample_files with .txt files containing these
    sample inputs and outputs will also be created.

    Will also create a blank code file inside the newly-created directory
    with the given extension, if one is provided.

    Parameters:
        root (str): The root directory to work in
        problem_id (str): The Kattis problem id (found by looking at the
            problem's URL: 'open.kattis.com/problems/<problem_id>')
        ext (str): (Optional) The extension of the code file to create

    Raises:
        OSError: If there is a problem creating the directory/file structure
            for this problem.
        KattisWebAccessException: If there is a problem accessing the Kattis
            website during this process.
    """
    raise NotImplementedError("Error: setup_kattis_problem not implemented.")


def setup_uva_problem(root: str,
                      problem_id: str,
                      ext: Optional[str] = None):
    """Set up a directory/sample problem structure for a UVA problem.

    The directory will be named after the problem_id, and will contain a
    sub-directory named 'test_cases'. If any sample test cases are provided,
    a sub-sub directory called 'sample_files with .txt files containing these
    sample inputs and outputs will also be created.

    Will also create a blank code file inside the newly-created directory
    with the given extension, if one is provided.

    Parameters:
        root (str): The root directory to work in
        problem_id (str): The Kattis problem id (found by looking at the
            problem's URL: 'open.kattis.com/problems/<problem_id>')
        ext (str): (Optional) The extension of the code file to create

    Raises:
        OSError: If there is a problem creating the directory/file structure
            for this problem.
        UVAWebAccessException: If there is a problem accessing the UVA
            (OnlineJudge) website during this process
    """
    raise NotImplementedError("Error: setup_uva_problem not implemented.")


# -------------------- BOOK CHAPTER SETUP FUNCTIONS -------------------- #
def setup_cp4_chapter_problems(root: str, chapter: int):
    """Set up the file structure for a CP4 book chapter.

    Parameters:
        root (str): The root directory to work in
        chapter (int): The number of the chapter (1-9) to download practice
            problems for

    Raises:
        ValueError: If invalid directory is provided, or if chapter number
            is out of the range [1,9].
    """
    raise NotImplementedError("Error: setup_cp4_chapter_problems "
                              "not implemented.")


if __name__ == "__main__":
    pass
