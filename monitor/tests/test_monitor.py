#!/usr/bin/env python

# test_monitor.py
#
# Copyright (C) 2019 Kano Computing Ltd.
# License:   http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import unittest
import os

class TestMonitor(unittest.TestCase):

    def _set_command_line(self, logfile, samples, threshold):
        return 'python ../drfeedback-monitor.py process --logfile={} ' \
            '--samples={} --threshold={}'.format(logfile, samples, threshold)

    def test_spike_two_days(self):
        rc = os.system(self._set_command_line('../log_sample_spike.txt', 2, 1.5))
        assert (os.WEXITSTATUS(rc) == 1)

    def test_spike_three_days(self):
        rc = os.system(self._set_command_line('../log_sample_spike.txt', 3, 1.5))
        assert (os.WEXITSTATUS(rc) == 1)

    def test_spike_five_days(self):
        rc = os.system(self._set_command_line('../log_sample_spike.txt', 5, 1.1))
        assert (os.WEXITSTATUS(rc) == 1)

    def test_steady_two_days(self):
        rc = os.system(self._set_command_line('../log_sample_steady.txt', 2, 1.5))
        assert (os.WEXITSTATUS(rc) == 0)

    def test_steady_three_days(self):
        rc = os.system(self._set_command_line('../log_sample_steady.txt', 3, 1.5))
        assert (os.WEXITSTATUS(rc) == 0)

    def test_steady_five_days(self):
        rc = os.system(self._set_command_line('../log_sample_steady.txt', 3, 1.5))
        assert (os.WEXITSTATUS(rc) == 0)


        
if __name__ == '__main__':
    unittest.main()
