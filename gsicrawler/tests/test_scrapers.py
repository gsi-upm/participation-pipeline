from unittest import TestCase

from gsicrawler.scrapers.tripadvisor import retrieveTripadvisorReviews

from gsicrawler.scrapers.facebook import getFBPageFeedData


class ScraperTest(TestCase):


    def test_tripadvisor(self):
        reviews = retrieveTripadvisorReviews('lateral madrid arturo soria', 10)
        assert reviews
        assert len(reviews) == 10

    def test_facebook(self):
        getFBPageFeedData('restauranteslateral', 10)

