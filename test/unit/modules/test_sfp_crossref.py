import pytest
import unittest

from modules.sfp_crossref import sfp_crossref
from sflib import SpiderFoot
from test.unit.modules.test_module_base import SpiderFootModuleTestCase


@pytest.mark.usefixtures
class TestModuleCrossref(SpiderFootModuleTestCase):

    def test_opts(self):
        module = sfp_crossref()
        self.assertEqual(len(module.opts), len(module.optdescs))

    def test_setup(self):
        sf = SpiderFoot(self.default_options)
        module = sfp_crossref()
        module.setup(sf, dict())

    def test_watchedEvents_should_return_list(self):
        module = sfp_crossref()
        self.assertIsInstance(module.watchedEvents(), list)

    def test_producedEvents_should_return_list(self):
        module = sfp_crossref()
        self.assertIsInstance(module.producedEvents(), list)
