import pytest
from playwright.sync_api import Page, expect

class TestExample:
    def test_example(self, page: Page):
        """Test example to demonstrate review criteria."""
        page.goto('https://example.com')
        expect(page).to_have_title('Example Domain')
        expect(page.locator('h1')).to_have_text('Example Domain')