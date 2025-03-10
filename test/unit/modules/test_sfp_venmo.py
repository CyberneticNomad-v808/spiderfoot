import pytest
import unittest

from modules.sfp_venmo import sfp_venmo
from sflib import SpiderFoot
from test.unit.modules.test_module_base import SpiderFootModuleTestCase

@pytest.mark.usefixtures
class TestModuleVenmo(SpiderFootModuleTestCase):

    def test_opts(self):
        module = sfp_venmo()
        self.assertEqual(len(module.opts), len(module.optdescs))

    def test_setup(self):
        sf = SpiderFoot(self.default_options)
        module = sfp_venmo()
        module.setup(sf, dict())

    def test_watchedEvents_should_return_list(self):
        module = sfp_venmo()
        self.assertIsInstance(module.watchedEvents(), list)

    def test_producedEvents_should_return_list(self):
        module = sfp_venmo()
        self.assertIsInstance(module.producedEvents(), list)
