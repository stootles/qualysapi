import unittest
import os
import sys
import requests_mock
import tests.fixtures_api_objects as fixtures
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from qualysapi.api_objects import *
import qualysapi.connector as qcconn

# TODO There is an argument to be made that many attributes should be read-only in the api_objects objects
# TODO There may be an opportuniry to create an refresh() method so these obejcts can refresh if needed


class TestAPIObjects(unittest.TestCase):
    def setUp(self):
        global qgc  # For access in tests
        global adapter  # For access in tests
        adapter = requests_mock.Adapter()
        qgc = qcconn.QGConnector(('Testing QualysAPI','secretpassword'), 'localhost')

        # Route all requests through mock here by default to limit potential leakage
        # Will throw NoMockAddress if we are not matching correctly in an actual test
        qgc.session.mount('http://', adapter)
        qgc.session.mount('https://', adapter)

    def test_host_object(self):
        host = Host('host.example.com', 12345678, '127.0.0.1', 'invalid_date', 'HOST', 'Windows 2012', 'IP')
        self.assertIsInstance(host,
                              Host,
                              'Should be instance of Host')
        self.assertEqual(repr(host),
                         'ip: 127.0.0.1, qualys_id: 12345678, dns: host.example.com',
                         'Host objects should have a reasonable __REPR__')
        self.assertEqual('never',
                         host.last_scan,
                         'Host with invalid date on generation should be considered "never" scanned')

        host = Host('host.example.com', 12345678, '127.0.0.1', '2018-10-22T00:09:09Z', 'HOST', 'Windows 2012', 'IP')

        self.assertIsInstance(host.last_scan, datetime.datetime, "Last Scan should be Date type for scanned hosts")

    def test_asset_group_object(self):
        asset_group = AssetGroup('4', 87654321, '2018-10-22T00:09:09Z',
                                 ['127.0.0.1', '127.0.0.2'], [''], ['Default Scanner'], 'A Simple Asset Group')
        self.assertIsInstance(asset_group, AssetGroup)
        self.assertEqual('qualys_id: 87654321, title: A Simple Asset Group',
                         repr(asset_group),
                         "Should have a reasonable __REPR__")

    def test_asset_group_addAsset(self):
        # TODO addAsset should test for success
        # TODO addAsset should test for failure
        # TODO addAsset should work for multiple ips in a List or as a comma separated list
        adapter.register_uri('POST', '/api/2.0/fo/asset/group/', text=fixtures.assetGroupAddAssetSuccessResponse)

        asset_group = AssetGroup('4', '87654321', '2018-10-22T00:09:09Z',
                                 ['127.0.0.1', '127.0.0.2'], '', ['Default Scanner'], 'A Simple Asset Group')

        asset_group.addAsset(qgc, '127.0.0.3')
        self.assertIn('127.0.0.3',
                      asset_group.scanips,
                      "Added Single IPv4 string should be in list of ips")

        self.assertIn('127.0.0.1',
                      asset_group.scanips,
                      "Should still have original members after changes")

        self.assertNotIn('127.0.0.6',
                         asset_group.scanips,
                         "Should not have unexpected members after changes")

    def test_asset_group_setAssets(self):
        # TODO setAsset should test for success
        # TODO setAsset should test for failure
        # TODO Should take comma seperate list OR a list of ip address
        # TODO Should update assets in AssetGroup or refresh AssetGroup
        adapter.register_uri('POST', '/api/2.0/fo/asset/group/', text=fixtures.assetGroupSetAssetSuccessResponse)

        asset_group = AssetGroup('4', 87654321, '2018-10-22T00:09:09Z',
                                 ['127.0.0.1', '127.0.0.2'], '', ['Default Scanner'], 'A Simple Asset Group')

        asset_group.setAssets(qgc, '127.0.0.3')

    def test_report_template_object(self):
        report_template = ReportTemplate(1, '96325874', '2017-08-30T00:34:16Z', 'Scan',
                                         'A report template', 'Auto', 'auserid')
        self.assertIsInstance(report_template, ReportTemplate, "Should be type ReportTemplate")

        self.assertEqual("qualys_id: 96325874, title: A report template",
                         repr(report_template),
                         'Should have a resonable __REPR__')

    def test_report_object(self):
        # TODO CHeck size format
        report = Report('2017-08-30T00:34:16Z', '1234567', '2017-08-23T00:34:16Z', 'PDF', '123', 'Finished', 'Scan',
                        'astry', 'A Report from Qualys')
        self.assertIsInstance(report, Report, "Should be type Report")
        self.assertEqual('qualys_id: 1234567, title: A Report from Qualys',
                         repr(report),
                         'Should have a reasonable __REPR__')

    def test_report_download(self):
        # TODO download should test for failure
        # TODO download should error if report not ready
        # TODO Should use fixtures to mock responses NEEDS A SAMPLE REPORT CREATED.
        # TODO For larger reports, would be nice to have a version that streams results
        # TODO For larger reports, would be nice to have a a progress callback loop
        report = Report('2017-08-30T00:34:16Z', '1234567', '2017-08-23T00:34:16Z', 'PDF', '123', 'Finished', 'Scan',
                        'astry', 'A Report from Qualys')

        adapter.register_uri('POST', '/api/2.0/fo/report/', text='resp')
        # TODO This is a little silly, mock needs to shape responses via fixtures
        self.assertEqual('resp',
                         report.download(qgc),
                         'Should return a report')

    def test_scan_object(self):
        # TODO Check formats of object args
        scan = Scan('', '', '2018-10-22T00:09:09Z', 'The Scan Profile', 1, 'scan/987654321', 'Finished',
                    'Target1,Target2', 'A scan', 'VM', 'astrew')

        self.assertIsInstance(scan, Scan, 'Scan objects should be of type Scan')
        self.assertEqual('qualys_ref: scan/987654321, title: A scan, option_profile: The Scan Profile',
                         repr(scan),
                         'Scan should a reasonable __REPR__')

    def test_scan_cancel(self):
        # TODO cancel should raise smart error if suitable (e.g. Cancel request not accepted)
        # TODO Should use fixtures to mock responses
        # TODO Scan object should be marked as stale if cancel request accepted
        scan = Scan('', '', '2018-10-22T00:09:09Z', 'The Scan Profile', 1, 'scan/987654321', 'Running',
                    'Target1,Target2', 'A scan', 'VM', 'astrew')
        adapter.register_uri('POST', '/api/2.0/fo/scan/', text='resp')

        # TODO These Exception tests should be DRYer
        try:
            scan.status = 'Finished'
            self.assertRaises(ValueError, scan.cancel(qgc), 'Should raise Value Error if Scan is Finished')
        except ValueError:
            pass

        try:
            scan.status = 'Cancelled'
            self.assertRaises(ValueError, scan.cancel(qgc), 'Should raise Value Error if Scan is Cancelled')
        except ValueError:
            pass

        try:
            scan.status = 'Error'
            self.assertRaises(ValueError, scan.cancel(qgc), 'Should raise Value Error if Scan is Error')
        except ValueError:
            pass

        scan.status = 'Running'
        # TODO FIXTURE Required to test response for scan.cancel()
        # scan.cancel(qgc)

    def test_scan_pause(self):
        # TODO pause should raise smart error if suitable (e.g. Pause request not accepted)
        # TODO Should use fixtures to mock responses
        # TODO Scan object should be marked as pause if cancel request accepted
        scan = Scan('', '', '2018-10-22T00:09:09Z', 'The Scan Profile', 1, 'scan/987654321', 'Running',
                    'Target1,Target2', 'A scan', 'VM', 'astrew')
        adapter.register_uri('POST', '/api/2.0/fo/scan/', text='resp')

        # TODO Identify if only raised if status not Running
        try:
            scan.status = 'Finished'
            self.assertRaises(ValueError, scan.cancel(qgc), 'Should raise Value Error if Scan is Finished')
        except ValueError:
            pass

        scan.status = "Running"
        # TODO FIXTURE Required to test response for scan.pause()
        # scan.pause(qgc)

    def test_scan_resume(self):
        # TODO resume should raise smart error if suitable (e.g. Resume request not accepted)
        # TODO Should use fixtures to mock responses
        # TODO Scan object should be marked as stale if resume request accepted
        scan = Scan('', '', '2018-10-22T00:09:09Z', 'The Scan Profile', 1, 'scan/987654321', 'Running',
                    'Target1,Target2', 'A scan', 'VM', 'astrew')
        adapter.register_uri('POST', '/api/2.0/fo/scan/', text='resp')

        # TODO Identify if only raised if not Paused
        try:
            scan.status = 'Finished'
            self.assertRaises(ValueError, scan.resume(qgc), 'Should raise Value Error if Scan is Finished')
        except ValueError:
            pass

        scan.status = "Running"
        # TODO FIXTURE Required to test response for scan.resume()
        # scan.resume(qgc)


if __name__ == '__main__':
    unittest.main()
