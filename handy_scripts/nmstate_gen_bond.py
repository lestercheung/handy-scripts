"""
Generate nmstate configuration from a given network configuration."""

import argparse
import json
import yaml
import sys
import subprocess

from pprint import pprint as pp


def parse_args(args=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bond", help="Bond interface name")
    ap.add_argument("--bond-mode", default="802.3ad", help="Bond mode")
    ap.add_argument("--xmit-hash-policy", default="layer3+4",
                    help="Xmit hash policy")
    ap.add_argument(
        "--bond-slaves",
        type=lambda s: s.split(","),
        help="Bond slaves (comma-separated)",
    )
    ap.add_argument("--ip4", help="IPv4 address with prefix length")
    # ap.add_argument('--vlans', type=lambda s: [int(v) for v in s.split(',')],
    #                 help='VLAN trunks (comma-separated)')

    return ap.parse_args(args)


def get_max_ring_tweaks(eth):
    try:
        cmd = f"/usr/bin/ethtool --json -g {eth}".split()
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        stdout, _ = p.communicate()
        ethtool = json.loads(stdout)[0]
        ring = {}
        if "rx" in ethtool:
            ring["rx"] = ethtool["rx"]
        if "rx-max" in ethtool:
            ring["rx-max"] = ethtool["rx-max"]
        if "tx" in ethtool:
            ring["tx"] = ethtool["tx"]
        if "tx-max" in ethtool:
            ring["tx-max"] = ethtool["tx-max"]
        return ring
    except Exception as e:
        print(f"Error getting ethtool info for {eth}: {e}")
        return None


def main():
    cfg = parse_args()
    pp(cfg)

    interfaces = []
    for eth in cfg.bond_slaves:
        iface = {
            "name": eth,
            "type": "ethernet",
            "state": "up",
        }
        maxring = get_max_ring_tweaks(eth)
        if maxring:
            iface["ethtool"] = {"ring": maxring}

        interfaces.append(iface)

    interfaces.append(
        {
            "name": cfg.bond,
            "type": "bond",
            "state": "up",
            "link-aggregation": {
                "mode": cfg.bond_mode,
                "port": cfg.bond_slaves,
                "options": {
                    "xmit-hash-policy": cfg.xmit_hash_policy,
                    "downdelay": 0,
                    "updelay": 0,
                    "miimon": 100,
                    "use_carrier": True,
                },
            },
            "ipv4": {
                "enabled": True,
                "address": [cfg.ip4.split("/")[0]],
                "prefix-length": int(cfg.ip4.split("/")[1]),
            },
        }
    )

    yaml.dump(dict(interfaces=interfaces), sys.stdout, default_flow_style=False)


if __name__ == "__main__":
    main()
