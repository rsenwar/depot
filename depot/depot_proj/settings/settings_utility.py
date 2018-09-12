"""Utility for settings."""

import requests

AWS_METADATA_URL = 'http://169.254.170.2/v2/metadata'


def get_ec2_private_ip():
    """Get Private EC2 IP."""
    ec2_ip = None
    try:
        resp = requests.get(AWS_METADATA_URL, timeout=0.10)
        data = resp.json()
        # print(data)

        container_meta = data['Containers'][0]
        ec2_ip = container_meta['Networks'][0]['IPv4Addresses'][0]
    except Exception:
        # silently fail as we may not be in an ECS environment
        pass
    return ec2_ip


x = '''
import requests
import pycurl
from io import BytesIO


CHECKIP_URL = 'checkip.amazonaws.com'


def get_host_by_checkip_aws():
    # Determine Public IP address of EC2 instance
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'checkip.amazonaws.com')
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    # Body is a byte string, encoded. Decode it first.
    host_ip = buffer.getvalue().decode('iso-8859-1').strip()
    return host_ip

'''
