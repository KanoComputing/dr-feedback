#!/usr/bin/env python

#
# test_monitor.py - pytest module
#
# Copyright (C) 2019 Kano Computing Ltd.
# License:   http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Run with:
#
#  $ sudo apt-get install python-pytest
#  $ python -m pytest
#

import os


def cmdline(logfile, samples, threshold):
    return 'python ../drfeedback-monitor.py process --logfile=data/{} ' \
        '--samples={} --threshold={}'.format(logfile, samples, threshold)

def test_spike_two_days():
    rc = os.system(cmdline('log_sample_spike.txt', 2, 1.5))
    assert os.WEXITSTATUS(rc) == 1

def test_spike_three_days():
    rc = os.system(cmdline('log_sample_spike.txt', 3, 1.5))
    assert os.WEXITSTATUS(rc) == 1

def test_spike_five_days():
    rc = os.system(cmdline('log_sample_spike.txt', 5, 1.1))
    assert os.WEXITSTATUS(rc) == 1

def test_steady_two_days():
    rc = os.system(cmdline('log_sample_steady.txt', 2, 1.5))
    assert os.WEXITSTATUS(rc) == 0

def test_steady_three_days():
    rc = os.system(cmdline('log_sample_steady.txt', 3, 1.5))
    assert os.WEXITSTATUS(rc) == 0

def test_steady_five_days():
    rc = os.system(cmdline('log_sample_steady.txt', 5, 1.5))
    assert os.WEXITSTATUS(rc) == 0

def test_spike_real_log():
    rc = os.system(cmdline('log_real_data.txt', 2, 1.5))
    assert os.WEXITSTATUS(rc) == 1

def test_alert():
    alert_message = 'Slack alert signal requested, simulate=True'
    command_line = cmdline('log_sample_spike.txt', 5, 1.1)
    command_line += ' --verbose'

    output = os.popen(command_line).read()
    assert output.find(alert_message) != -1
    assert output.find('curl') != -1
