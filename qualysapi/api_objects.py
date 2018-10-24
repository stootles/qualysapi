from __future__ import absolute_import
import datetime
from lxml import objectify


class Host(object):
    def __init__(self, dns, id, ip, last_scan, netbios, os, tracking_method):
        """Qualys Host Object


                      Args:
                          dns (str): FQDN hostname
                          id (int): Qualys assigned ID number
                          last_scan (str): Last Scan date/time format is 2018-10-22T00:09:09Z
                          netbios (str): NETBIOS name
                          os (str): OS String
                          tracking_method (str): IP/DNS etc
        """
        self.dns = str(dns)
        self.id = int(id)
        self.ip = str(ip)
        try:
            last_scan = str(last_scan).replace('T', ' ').replace('Z', '').split(' ')
            date = last_scan[0].split('-')
            time = last_scan[1].split(':')
            self.last_scan = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]),
                                               int(time[2]))
        except IndexError:
            self.last_scan = 'never'
        self.netbios = str(netbios)
        self.os = str(os)
        self.tracking_method = str(tracking_method)

    def __repr__(self):
        return f"ip: {self.ip}, qualys_id: {self.id}, dns: {self.dns}"


class AssetGroup(object):
    def __init__(self, business_impact, id, last_update, scanips, scandns, scanner_appliances, title):
        """Qualys Host Object

            Args:
              business_impact (str): Business impact level (e.g. 4)
              id (int): Qualys assigned ID number
              last_update (str): Last Updated format is 2018-10-22T00:09:09Z
              scanips (list of str): list of IP addresses
              scandns (list of str): list of DNS names
              scanner_appliances (list of str): Scan Appliance names
              title (str): Asset Group Title
        """
        self.business_impact = str(business_impact)
        self.id = int(id)
        self.last_update = str(last_update)
        self.scanips = scanips
        self.scandns = scandns
        self.scanner_appliances = scanner_appliances
        self.title = str(title)

    def addAsset(self, conn, ip):
        """Adds a single IP address to the AssetGroup

            Args:
                ip (str): IPv4 Address to add
        """
        call = '/api/2.0/fo/asset/group/'
        parameters = {'action': 'edit', 'id': self.id, 'add_ips': ip}
        conn.request(call, parameters)
        self.scanips.append(ip)

    def setAssets(self, conn, ips):
        """Replaces IP addresses with the supplied set of IP AddressesAssetGroup

            Args:
                ips (str): IPv4 Address comma seperated list

        """
        call = '/api/2.0/fo/asset/group/'
        parameters = {'action': 'edit', 'id': self.id, 'set_ips': ips}
        conn.request(call, parameters)

    def __repr__(self):
        return f"qualys_id: {self.id}, title: {self.title}"


class ReportTemplate(object):
    def __init__(self, isGlobal, id, last_update, template_type, title, type, user):
        """Qualys Report Template Object


        Args:
           isGlobal (int): 0 for falase and 1 for true
           id (int): Qualys assigned ID number
           last_update (str): Last updated format is 2018-10-22T00:09:09Z
           template_type (str): Template type
           title (str): Template title
           type (str): Manual, Auto, etc
           user (str): Owner of scan
        """
        self.isGlobal = int(isGlobal)
        self.id = int(id)
        self.last_update = str(last_update).replace('T', ' ').replace('Z', '').split(' ')
        self.template_type = template_type
        self.title = title
        self.type = type
        self.user = user

    def __repr__(self):
        return f"qualys_id: {self.id}, title: {self.title}"


class Report(object):
    def __init__(self, expiration_datetime, id, launch_datetime, output_format, size, status, type, user_login,
                 title=''):
        """Qualys Report Object


        Args:
            expiration_datetime (str): Date this report will be removed
                                       Format is 2018-10-22T00:09:09Z)
            id (int): Qualys assigned ID number
            launch_datetime (str): Date and time report was generated format is 2018-10-22T00:09:09Z
            output_format (str): Report format (PDF, CSV, etc)
            size (str): Size of the report/file
            status (str): State of report (e.g. Finished)
            type (str): Report type
            user_login (str): User login ID who generated the report
            title (str): Title of the report
        """
        self.expiration_datetime = str(expiration_datetime).replace('T', ' ').replace('Z', '').split(' ')
        self.id = int(id)
        self.launch_datetime = str(launch_datetime).replace('T', ' ').replace('Z', '').split(' ')
        self.output_format = output_format
        self.size = size
        self.status = status
        self.type = type
        self.user_login = user_login
        self.title = title

    def __repr__(self):
        return f"qualys_id: {self.id}, title: {self.title}"

    def download(self, conn):
        call = '/api/2.0/fo/report'
        parameters = {'action': 'fetch', 'id': self.id}
        if self.status == 'Finished':
            return conn.request(call, parameters)


class Scan(object):
    def __init__(self, assetgroups, duration, launch_datetime, option_profile, processed, ref, status, target, title,
                 type, user_login):
        """Qualys Scan Object


        Args:
            assetgroups (????): ????
            duration (str): Time scan has been running or ran for if Finished
            launch_datetime (str): Date and time report was generated format is 2018-10-22T00:09:09Z
            option_profile (str): Which option profile was used
            processed (int): ????
            ref (str): Qualys Assigned Identifier
            status (str): State of scan (e.g. Finished)
            title (str): Title of the Scan
            type (str): Scan Type
            user_login (str): User login ID who generated the report
        """
        self.assetgroups = assetgroups
        self.duration = str(duration)
        launch_datetime = str(launch_datetime).replace('T', ' ').replace('Z', '').split(' ')
        date = launch_datetime[0].split('-')
        time = launch_datetime[1].split(':')
        self.launch_datetime = datetime.datetime(int(date[0]),
                                                 int(date[1]),
                                                 int(date[2]),
                                                 int(time[0]),
                                                 int(time[1]),
                                                 int(time[2]))
        self.option_profile = str(option_profile)
        self.processed = int(processed)
        self.ref = str(ref)
        self.status = str(status)
        self.target = str(target).split(', ')
        self.title = str(title)
        self.type = str(type)
        self.user_login = str(user_login)

    def __repr__(self):
        return f"qualys_ref: {self.ref}, title: {self.title}, option_profile: {self.option_profile}"

    def cancel(self, conn):
        cancelled_statuses = ['Cancelled', 'Finished', 'Error']
        if any(self.status in s for s in cancelled_statuses):
            raise ValueError("Scan cannot be cancelled because its status is " + self.status)
        else:
            call = '/api/2.0/fo/scan/'
            parameters = {'action': 'cancel', 'scan_ref': self.ref}
            conn.request(call, parameters)

            parameters = {'action': 'list', 'scan_ref': self.ref, 'show_status': 1}
            self.status = objectify.fromstring(
                conn.request(call, parameters).encode('utf-8')).RESPONSE.SCAN_LIST.SCAN.STATUS.STATE

    def pause(self, conn):
        if self.status != "Running":
            raise ValueError("Scan cannot be paused because its status is " + self.status)
        else:
            call = '/api/2.0/fo/scan/'
            parameters = {'action': 'pause', 'scan_ref': self.ref}
            conn.request(call, parameters)

            parameters = {'action': 'list', 'scan_ref': self.ref, 'show_status': 1}
            self.status = objectify.fromstring(
                conn.request(call, parameters).encode('utf-8')).RESPONSE.SCAN_LIST.SCAN.STATUS.STATE

    def resume(self, conn):
        if self.status != "Paused":
            raise ValueError("Scan cannot be resumed because its status is " + self.status)
        else:
            call = '/api/2.0/fo/scan/'
            parameters = {'action': 'resume', 'scan_ref': self.ref}
            conn.request(call, parameters)

            parameters = {'action': 'list', 'scan_ref': self.ref, 'show_status': 1}
            self.status = objectify.fromstring(
                conn.request(call, parameters).encode('utf-8')).RESPONSE.SCAN_LIST.SCAN.STATUS.STATE
