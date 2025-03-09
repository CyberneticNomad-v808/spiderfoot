import pytest
import unittest

from modules.sfp_wikileaks import sfp_wikileaks
from sflib import SpiderFoot
from test.unit.modules.test_module_base import SpiderFootModuleTestCase


@pytest.mark.usefixtures
class TestModulewikileaks(SpiderFootModuleTestCase):

    def test_opts(self):
        module = sfp_wikileaks()
        self.assertEqual(len(module.opts), len(module.optdescs))

    def test_setup(self):
        sf = SpiderFoot(self.default_options)
        module = sfp_wikileaks()
        module.setup(sf, dict())

    def test_watchedEvents_should_return_list(self):
        module = sfp_wikileaks()
        self.assertIsInstance(module.watchedEvents(), list)

    def test_producedEvents_should_return_list(self):
        module = sfp_wikileaks()
        self.assertIsInstance(module.producedEvents(), list)
