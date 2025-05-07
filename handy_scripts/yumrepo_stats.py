#!/bin/python3
import xml.etree.ElementTree as ET
from collections import defaultdict
import requests
import argparse
import gzip

ns = {
    "repo": "http://linux.duke.edu/metadata/repo",
    "common": "http://linux.duke.edu/metadata/common",
    "rpm": "http://linux.duke.edu/metadata/rpm",
}


def parse_args(args=None):
    ap = argparse.ArgumentParser(description="Get stats on a yum repo")
    ap.add_argument("repo_url", help="URL of the yum repo")

    return ap.parse_args(args)


def find_primary_xml(repo_url):
    # get the repomd.xml file
    repomd_url = f"{repo_url}/repodata/repomd.xml"
    repomd_resp = requests.get(repomd_url, verify=False)
    repomd_resp.raise_for_status()

    # parse the repomd.xml file
    repomd = ET.fromstring(repomd_resp.content)
    data_primary = repomd.find(".//repo:data[@type='primary']", ns)
    # print(ET.tostring(data_primary, encoding='unicode'))
    loc = data_primary.find("repo:location", ns)
    primary_xml_url = f"{repo_url}/{loc.attrib.get('href')}"
    # print(primary_xml_url)

    # get the primary.xml.gz file
    primary_xml_gz_resp = requests.get(primary_xml_url, verify=False)
    primary_xml_gz_resp.raise_for_status()
    uncompressed_xml = gzip.decompress(primary_xml_gz_resp.content)
    return ET.fromstring(uncompressed_xml)


def main():
    cfg = parse_args()
    pkgs_cnt, tot_pkg_size = 0, 0
    pkg2vers = defaultdict(list)
    pkgs = []
    primary = find_primary_xml(cfg.repo_url)
    for pkg in primary.findall(".//common:package", ns):
        name = pkg.find("common:name", ns).text
        version = pkg.find("common:version", ns)
        ver = version.get("ver")
        size = pkg.find("common:size", ns)
        package_size = int(size.get("package", 0))
        pkgs.append({"name": name, "ver": ver, "size": package_size})
        pkgs_cnt += 1
        tot_pkg_size += int(package_size)
        pkg2vers[name].append(ver)
    print(f"Total packages: {pkgs_cnt}")
    print(f"Unique packages: {len(pkg2vers)}")
    print(f"Total package size: {tot_pkg_size:,} bytes")


if __name__ == "__main__":
    main()
