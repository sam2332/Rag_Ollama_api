import pytest
from Libs.EmbeddingsHelper import SoupToText
from bs4 import BeautifulSoup


def test_SoupToText_empty_soup():
    # Test with an empty soup
    soup = BeautifulSoup("", "html.parser")
    assert SoupToText(soup) == ""


def test_SoupToText_only_text():
    # Test with a soup containing only text
    soup = BeautifulSoup("Hello, world!", "html.parser")
    assert SoupToText(soup) == "Hello, world!"


def test_SoupToText_with_tags():
    # Test with a soup containing tags
    soup = BeautifulSoup("<p>Hello, <b>world!</b></p>", "html.parser")
    assert SoupToText(soup) == "Hello, world!"


def test_SoupToText_with_scripts_and_styles():
    # Test with a soup containing script and style elements
    soup = BeautifulSoup(
        "<p>Hello, <script>alert('world!');</script></p>", "html.parser"
    )
    assert SoupToText(soup) == "Hello, "


def test_SoupToText_with_other_elements():
    # Test with a soup containing other elements
    soup = BeautifulSoup("<p>Hello, <svg>world!</svg></p>", "html.parser")
    assert SoupToText(soup) == "Hello, "


def test_SoupToText_with_nested_elements():
    # Test with a soup containing nested elements
    soup = BeautifulSoup("<p>Hello, <b><i>world!</i></b></p>", "html.parser")
    assert SoupToText(soup) == "Hello, world!"


def test_SoupToText_svg_markdown():
    # Test with a soup containing text and multiple svg elements
    soup = BeautifulSoup(
        """
# Hello, world!


<svg><text>Hello, world!</text></svg>

<svg>

<text>
Hello, world!
</text>
</svg>
    Hey Whats up

    
    """,
        "html.parser",
    )

    print(SoupToText(soup))
    assert SoupToText(soup) == "# Hello, world!\n Hey Whats up"
