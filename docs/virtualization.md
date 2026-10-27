# VPN and virtual machine host

The base role installs Arch's signed `openvpn` package. The desktop role adds
the signed `networkmanager-openvpn` plugin and `nm-connection-editor` so OpenVPN
profiles can be imported and managed through NetworkManager's GUI. These are
official Arch packages. No VPN provider, profile, credential, or private key is
included in the repository. Obtain a profile from the VPN administrator/provider
and keep it in the user's private NetworkManager connection storage.

For a profile supplied as an `.ovpn` file, import it as the desktop user from
`nm-connection-editor` or with:

```sh
nmcli connection import type openvpn file /path/to/profile.ovpn
nmcli connection up PROFILE_NAME
```

NetworkManager stores imported profiles as protected system connection files;
the source file may also contain certificates or authentication details, so keep
it private and out of the repository.

NetworkManager imports common single-file `.ovpn` profiles. Some providers give
separate certificate/key files or an external `auth-user-pass` file, which may
need provider-specific conversion or direct use with OpenVPN. Keep all supplied
files together with private permissions and follow the provider's Linux
instructions; do not paste credentials into shell history.

The desktop role also installs the Arch repository packages for the local
QEMU/KVM system connection used by virt-manager:

| Package | Purpose |
| --- | --- |
| `qemu-desktop` | x86 QEMU emulator and desktop display/audio backends |
| `libvirt` | system VM, network, and storage management |
| `virt-manager` | graphical VM manager |
| `virt-install` | command-line VM creation tool; pulled by virt-manager |
| `virt-viewer` | guest console viewer |
| `edk2-ovmf` | UEFI firmware for guests |
| `swtpm` | emulated TPM 2.0 for Windows 11 guests |
| `dnsmasq` | DHCP/DNS service for libvirt virtual networks |

The current host also has `qemu-full`; the reusable setup selects `qemu-desktop`
for the x86 guest workload rather than installing emulators for every QEMU
architecture.

The role enables the modular `virtqemud`, `virtnetworkd`, and `virtstoraged`
sockets. It preserves any existing `default` network definition, creates the
packaged default definition only when missing, and starts/autostarts that NAT
network. It also creates and starts/autostarts the `default` directory storage
pool at `/var/lib/libvirt/images`, matching the current development host. If that
pool already points elsewhere, provisioning stops and asks you to specify the
intended path; it does not replace existing network or pool definitions. This
sets up the `qemu:///system` workflow without importing machine-specific VM
definitions or disk images.

When provisioning from inside a VM, check whether its uplink overlaps the
default NAT subnet (`192.168.122.0/24`). In the development guest,
`enp1s0` already uses that subnet, so starting a nested `default` network fails.
Pass `-e desktop_libvirt_manage_default_network=false` for that VM run to leave
the nested network inactive; the default remains enabled for a normal
workstation install. The role still configures libvirt sockets and the storage
pool.

## Authorization and lab network safety

The desktop role does not add the user to the `libvirt` group. That group grants
passwordless access to libvirt's read/write system socket, which can manage
system VMs with privileges comparable to root. Use the desktop Polkit agent and
the normal administrator authentication prompt for system VM management. Do not
change libvirt socket permissions or enable remote TCP access for convenience.

Treat the Active Directory lab as untrusted. Keep its guest network on a
dedicated libvirt NAT or isolated virtual network; do not bridge vulnerable
guests onto the work or home LAN. NAT allows guests outbound access and lets
guests on the same network communicate. Use a network with no forwarding when
the lab does not need internet access. Review the existing GOAD/libvirt network
and Vagrant provider settings before importing them; this role installs the
host packages and standard network only. It does not download GOAD, Windows
images, licenses, Vagrant plugins, or provider-specific configuration.

Windows guests may need VirtIO drivers when using VirtIO storage or network
devices. The upstream driver project publishes Windows 10+ binaries with a
Microsoft attestation signature; they are not WHQL signed. These drivers are
distributed separately from the Arch packages; obtain the driver ISO from the
[upstream project](https://github.com/virtio-win/kvm-guest-drivers-windows),
which directs users to Fedora's stable builds, and attach it during Windows
setup. Do not add an unreviewed AUR driver package to
the unattended role. SATA storage and emulated Intel networking are alternatives
when a lab definition does not include the driver ISO.

## Capacity

The current development computer reports 32 GiB RAM and about 1.3 TiB free disk
space. GOAD's current documentation estimates at least 20 GB RAM for GOAD-Light,
24 GB for the full lab, and about 115 GB disk. The full lab can leave little
memory for the Arch desktop. Close other VMs and applications or use the smaller
lab profile if the host starts swapping. Check requirements for the exact GOAD
version and local configuration before starting all guests.

References: [Arch libvirt guide](https://wiki.archlinux.org/title/Libvirt),
[virt-manager guide](https://wiki.archlinux.org/title/Virt-manager),
[Arch OpenVPN package](https://archlinux.org/packages/extra/x86_64/openvpn/),
[NetworkManager OpenVPN package](https://security.archlinux.org/package/networkmanager-openvpn),
[NetworkManager connection editor](https://archlinux.org/packages/extra/x86_64/nm-connection-editor/),
[libvirt system daemons](https://libvirt.org/daemons.html), and
[GOAD installation requirements](https://github.com/Orange-Cyberdefense/GOAD/blob/main/docs/mkdocs/docs/installation/windows.md).
