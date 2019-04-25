#
#  drfeedback-monitor.py
#
#  Copyright (C) 2019 Kano Computing Ltd.
#  License:   http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#  This module keeps track of DrFeedback alerts received from end users,
#  and raises an alert to the Kano Team in case a spike is detected,
#  suggesting that a major problem might have raised, and detailed look should be addressed.
#
#  The functionality is divided in two steps:
#
#   1) Collect and save a historic log with number of alerts received to the server
#   2) Read and process this log to detect any spike overtime, send and alert in such cases
#
#  The "process" command will return a1 if a spike is detected.
#

"""
DRFeedback-monitor keeps track and alerts the Kano Team about potential Kano OS customer troubles

Usage:
  drfeedback-monitor collect --logfile=<filename> --directory=<pathname> [--commit]
  drfeedback-monitor process --logfile=<filename> [--alert] [--samples=<n>] [--threshold=<factor>] [--verbose]

Options:
   -h, --help                   Show this message.
   -c, --commit                 Write the new collected counter to the logfile
   -a, --alert                  Send a slack alert if spike is detected
   -V, --verbose                Explain the steps taken during the process
   -l, --logfile=<filename>     Name of logfile to collect data into or process
   -d, --directory=<pathname>   Directory to check for numbers of files and collect counter
   -s, --samples=<n>            Number of samples to group for computing average
   -t, --threshold=<factor>     Threshold multitplier for the last average, if above then spike is raised

"""

LOGFILE = 'drfeedback-numbers.txt'
DRFEEDBACK_DIRECTORY = '/var/cache'
SAMPLES = 5
THRESHOLD = 1.5

import os
import sys
from time import gmtime, strftime
import docopt


class Collect():
    '''
    Collects the current number of Dr Feedback alerts and saves it into a logfile
    '''
    def __init__(self, args):
        self.args = args
        self.collect_command = 'ls -l {} | wc -l'.format(self.args['--directory'])

    def vprint(self, args):
        if self.args['--verbose']:
            print args
        
    def _collect_counter_(self):
        '''
        Obtains the number of drfeedback alerts
        '''
        log_count = os.popen(self.collect_command).read().strip()
        return 'date={} total-logs={}'.format(strftime("%d-%m-%Y", gmtime()), log_count)

    def _save_log_(self, entry):
        '''
        Appends the @entry string log message to the log file
        '''
        with open(self.args['--logfile'], 'a') as f:
            f.write('{}\n'.format(entry))

    def run(self):
        '''
        Run is the main entry point to put this class task to work
        '''
        log_entry=self._collect_counter_()
        self.vprint ('Collected counter: {}'.format(log_entry))

        if self.args['--commit']:
            self._save_log_(log_entry)
            self.vprint ('Commited counter to logfile: {}'.format(self.args['--logfile']))

        return 0


class Process():
    '''
    Reads and processes a logfile, sends an alert if a spike is detected.
    '''
    def __init__(self, args):
        self.args = args
        self.url_simulate = 'http://127.0.0.1:9000'
        self.url_slack = 'https://hooks.slack.com/services/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'

    def vprint(self, literal):
        if self.args['--verbose']:
            print literal

    def _get_log_counters_(self):
        '''
        Reads the logfile and returns a list of integers
        with all collected counters in chronological order
        '''
        counters = []
        self.vprint('reading logfile {}'.format(self.args['--logfile']))
        with open (self.args['--logfile'], 'r') as f:
            logdata = f.readlines()

        for l in logdata:
            counters.append (int(l.split('=')[2]))

        self.vprint ('collected {} drfeedback alerts'.format(len(counters)))
        return counters

    def _compute_(self, numbers):
        '''
        Reads a list of counters obtained from the logfile, and detects a spike,
        given the number of samples to average, and a threshold to compute the maximum deviation allowed

        Returns True if a spike is detected, False otherwise
        '''
        samples = []
        last_average_value = 0
        last_counter = 0
        
        for index, counter in enumerate(reversed(numbers)):

            #self.vprint ('>>> {} {}'.format(counter, index))
            if not last_counter:
                last_counter = counter
                continue

            samples.append(last_counter - counter)
            last_counter = counter

            if (index + 1) % self.args['--samples'] == 0:

                average_alerts = sum(samples) / len(samples)
                self.vprint ('Average number of drfeedback alerts is {} over last {} samples'.format(
                    average_alerts, self.args['--samples']))

                if not last_average_value:
                    last_average_value = average_alerts
                else:

                    if self._detect_spike(average_alerts, last_average_value):
                        self.vprint ('A spike was detected! current-average={} last-average={} ' \
                                     'threshold={} max-permitted-average={}'.format(
                                         average_alerts, last_average_value,
                                         self.args['--threshold'], average_alerts * self.args['--threshold']))
                        return True
                    else:
                        last_average_value = average_alerts

        self.vprint('no spike detected')
        return False

    def _detect_spike(self, average_alerts, last_average):
        '''
        Returns True if spike is detected
        '''
        self.vprint ('Spike check: current-average={} last-average={} threshold={} max-permitted-average={}'.format(
                        average_alerts, last_average, self.args['--threshold'], average_alerts * self.args['--threshold']))
        
        is_spike = average_alerts * self.args['--threshold'] < last_average
        if is_spike:
            self.vprint ('Spike was detected! {} * {} < {}'.format(average_alerts, self.args['--threshold'], last_average))

        return is_spike

    def slack_alert(self, simulate):
        '''
        Sends a network slack alert to the Dev Team to bring attentio to DrFeedback logs
        '''

        url = self.url_simulate if simulate else self.url_slack
        self.vprint('Slack alert signal requested, simulate={} url={}'.format(simulate, url))

        command = 'curl -X POST --data-urlencode \'payload=' \
                  '{"channel": "#team-os", "username": "drfeedback", ' \
                  '"text": "DrFeedback Monitor detected a spike: ' \
                  'https://kanocomputing.atlassian.net/wiki/spaces/OS/pages/422150149/Dr+Feedback+Architecture", ' \
                  '"icon_emoji": ":face_with_monocle:"}\' ' + url

        self.vprint(command)

        # FIXME: Find a reliable way to test it in simulation mode
        if not simulate:
            os.system(command)

        return

    def run(self):
        '''
        Run is the main entry point to put this class task to work
        '''
        counters = self._get_log_counters_()
        return self._compute_(counters)

        



if __name__ == '__main__':

    args = docopt.docopt(__doc__)
    rc = 0

    if args['--verbose']:
        print args
    
    # Provide default values when not specified
    if not args['--directory']:
        args['--directory'] = DRFEEDBACK_DIRECTORY

    if not args['--logfile']:
        args['--logfile'] = LOGFILE

    if not args['--samples']:
        args['--samples'] = int(SAMPLES)
    else:
        args['--samples'] = int(args['--samples'])

    if not args['--threshold']:
        args['--threshold'] = float(THRESHOLD)
    else:
        args['--threshold'] = float(args['--threshold'])

    if args['process']:
        processor = Process(args)
        rc = processor.run()
        if rc:
            processor.slack_alert(simulate = not args['--alert'])

    elif args['collect']:
        rc = Collect(args).run()

    sys.exit(rc)
