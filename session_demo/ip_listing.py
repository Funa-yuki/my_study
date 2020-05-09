# read a log file, fetch ip_list, and return list
import re
def ip_listing(path, domain):
    dns_patturn = re.compile(r'.*? %s from .*?' % domain)
    log = open(path, "r")
    ip_list = []
    for line in log:
        if dns_patturn.findall(line):
            result = re.findall(r'[0-9]+\.[0-9]+\.[0-9]+', line)
            ip_list.extend(result)
            return ip_list

ip_listing("./dns-masq/dnsmasq.log", "hoge.com")
