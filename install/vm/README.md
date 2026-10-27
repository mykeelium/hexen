# VM development and SSH access

Use QEMU/KVM through libvirt. Virt-manager provides the graphical console;
`virsh` manages the same VMs from a terminal. SSH is the normal interface for
commands, source inspection, and provisioning inside the guest.

Run the host commands below on the development computer, not inside the VM.
An agent's sandbox may require a separate approval to access libvirt's socket
or the guest network. That does not mean libvirt itself is broken.

## VM definition

The current disposable VM is `hexen-archinstall` on `qemu:///system`:

- UEFI/OVMF, Secure Boot disabled.
- Four virtual CPUs, 8 GiB RAM.
- A new 64 GiB QCOW2 disk, with no host block devices attached.
- Official Arch installation ISO attached as a read-only CD-ROM.
- Virtio networking on libvirt's `default` NAT network.
- SPICE graphical console listening on the host loopback address.

To reproduce it on a prepared host, first download and verify the ISO from the
[official download page](https://archlinux.org/download/). Copy that ISO into
libvirt-accessible storage. Substitute the actual downloaded filename:

```sh
ARCH_ISO="$HOME/Downloads/archlinux-YYYY.MM.DD-x86_64.iso"
sudo install -d -m 0755 /var/lib/libvirt/images
sudo install -m 0644 "$ARCH_ISO" /var/lib/libvirt/images/hexen-archinstall.iso
```

Then create the VM **once**. Do not reuse the disk path for an existing VM or
rerun this as a reset procedure:

```sh
sudo /usr/bin/python /usr/bin/virt-install \
  --connect qemu:///system \
  --name hexen-archinstall \
  --virt-type kvm \
  --machine q35 \
  --memory 8192 \
  --vcpus 4 \
  --cpu host-passthrough \
  --osinfo archlinux \
  --boot uefi,firmware.feature0.name=secure-boot,firmware.feature0.enabled=no \
  --disk path=/var/lib/libvirt/images/hexen-archinstall.qcow2,size=64,format=qcow2,bus=virtio \
  --cdrom /var/lib/libvirt/images/hexen-archinstall.iso \
  --network network=default,model=virtio \
  --graphics spice,listen=127.0.0.1 \
  --video virtio \
  --noautoconsole
```

The explicit system Python avoids accidentally using another interpreter from
PATH that lacks virt-install's system dependencies. The command was used to
create this VM; the resulting firmware, devices, and live boot were inspected.
It does not install Arch onto the virtual disk.

## Open the graphical console

From a host desktop terminal:

```sh
virt-manager --connect qemu:///system --show-domain-console hexen-archinstall
```

Alternatively, open virt-manager, select the QEMU/KVM **system** connection,
and double-click `hexen-archinstall`. This displays the guest's screen. The
ISO should eventually show a `root@archiso` shell.

`virsh console` is a serial terminal, not the SPICE graphical display. A serial
device alone does not guarantee that the guest exposes its shell there.

## Bootstrap SSH

Create a dedicated key on the host if one does not already exist:

```sh
ssh-keygen -t ed25519 -f "$HOME/.ssh/hexen-vm" -C hexen-development-vm
cat "$HOME/.ssh/hexen-vm.pub"
```

Keep the private key on the host. Copy only the public key into the live guest.
In the guest console, substitute the complete public key on one line:

```sh
install -d -m 0700 /root/.ssh
printf '%s\n' 'PASTE_PUBLIC_KEY_HERE' >> /root/.ssh/authorized_keys
chmod 0600 /root/.ssh/authorized_keys
systemctl start sshd
ip -br address
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

From the host, substitute the guest address:

```sh
ssh -i "$HOME/.ssh/hexen-vm" -o IdentitiesOnly=yes root@GUEST_IP
```

Compare the initial host-key fingerprint with the fingerprint shown in the
guest console before trusting it. Rebooting the live ISO can regenerate its
SSH host keys; verify replacements rather than disabling host-key checking.

### Bootstrap through the guest agent

The inspected ISO runs QEMU's guest agent, and this VM has its virtio channel.
When those conditions hold, the host can inspect addresses without logging in:

```sh
virsh --connect qemu:///system domifaddr hexen-archinstall --source agent
virsh --connect qemu:///system qemu-agent-command hexen-archinstall \
  '{"execute":"guest-info"}'
```

The guest-agent `guest-ssh-add-authorized-keys` command can authorize the public
key for `root`; `guest-exec` can retrieve the guest's SSH public host key for
verification. This route was successfully used on 2026-10-25. Availability is
ISO-dependent, so retain the graphical-console instructions as a fallback.

## Check networking before installation

On the host:

```sh
virsh --connect qemu:///system net-list --all
virsh --connect qemu:///system domifaddr hexen-archinstall --source lease
virsh --connect qemu:///system domifaddr hexen-archinstall --source agent
```

Inside the guest:

```sh
ip -br address
ip route
networkctl status enp1s0 --no-pager
getent ahostsv4 archlinux.org
curl --head --max-time 15 https://archlinux.org/
timedatectl show -p NTPSynchronized
```

Use the actual interface name if it differs. An empty lease list does not prove
the guest is powered off, and a successful ping does not prove DNS or HTTPS work.
If DHCP fails, inspect host-side dnsmasq logs and firewall rules before making
permanent changes:

```sh
sudo journalctl -b _COMM=dnsmasq -n 30 --no-pager
sudo nft list ruleset
```

Do not disable the host firewall as a general workaround. See the dated
[investigation record](../archinstall/observations-2026-10-25.md) for the current
temporary networking state and unresolved checks.

### UFW with libvirt's nftables backend

The development host's inspected ruleset has both UFW's iptables-nft chains and
libvirt's native nftables chains. UFW drops DHCP requests to the host, DNS to the
bridge gateway, and new forwarded guest connections. An accept in libvirt's
separate base chain does not override a drop in UFW's chain. This explains why
ping and host-initiated SSH can work while DHCP and HTTPS fail.

For the inspected `default` network, bridge `virbr0`, subnet
`192.168.122.0/24`, gateway `192.168.122.1`, and uplink `wlan0`, the proposed
host rules are:

```sh
sudo ufw allow in on virbr0 proto udp from any port 68 to any port 67 comment 'libvirt DHCP'
sudo ufw allow in on virbr0 proto udp from 192.168.122.0/24 to 192.168.122.1 port 53 comment 'libvirt DNS UDP'
sudo ufw allow in on virbr0 proto tcp from 192.168.122.0/24 to 192.168.122.1 port 53 comment 'libvirt DNS TCP'
sudo ufw route allow in on virbr0 out on wlan0 from 192.168.122.0/24 to any comment 'libvirt guest egress'
sudo ufw status numbered
```

These persist in UFW's configuration and apply immediately when UFW is enabled.
They are development-host configuration, not packages or services to add to the
target workstation. Verify the subnet and uplink on another host before adapting
them. Guest egress includes destinations reachable through that uplink, including
the LAN; the route rule does not permit new connections in the reverse direction.
The DHCP rule deliberately allows source `0.0.0.0`, since a new DHCP client has
no address yet. DNS access to other host interfaces remains outside these rules.

After applying them, renew DHCP in the live guest and repeat the networking
checks above. Remove the temporary static address, default route, and per-link
DNS override only after confirming that DHCP supplied usable replacements. A
DHCP address change can end SSH; rediscover the address through the guest agent.

To remove these exact rules later, use the same arguments with `delete` after
`ufw` (or `ufw route delete allow ...` for the forwarding rule). Keep other UFW,
Docker, and libvirt rules intact.

The local UFW parser accepted all four rules. After the owner applied them on
2026-10-25, the guest obtained a DHCP lease, resolved DNS through the bridge
gateway, fetched HTTPS headers from Arch's site, and reported synchronized time.
The temporary static address, route, and DNS override were removed and the same
checks passed again. See
[libvirt's firewall documentation](https://libvirt.org/firewall.html) for the
distinction between guest-to-host services and forwarded/NAT traffic.

## Inspect Archinstall through SSH

Use an interactive SSH terminal for its text menus:

```sh
ssh -t -i "$HOME/.ssh/hexen-vm" -o IdentitiesOnly=yes root@GUEST_IP \
  'TERM=xterm-256color archinstall --dry-run'
```

`--dry-run` generates configuration and exits instead of installing. Exported
configuration may still contain machine-specific paths, and credential exports
remain sensitive. Inspect files before copying any non-secret choices into the
repo. Do not use `--silent` for the supported interactive installation path.

For offline menu research only, the inspected version also supports
`--offline --skip-ntp --skip-version-check`. Those options do not validate package
availability, mirrors, time synchronization, or an actual installation.

Use the graphical console to verify firmware, the bootloader, encryption
prompts, and eventually Hyprland. Before the first disk boot, remove the ISO
from the virtual CD-ROM or choose the disk in the firmware boot menu; verify
that the VM actually booted the installed system.

SSH authorization and temporary networking in the live ISO disappear on reboot.
SSH access to the installed system is a separate decision; it is not a required
permanent service on the work laptop.

### Share the installer terminal with the owner

The inspected ISO includes tmux. Start the dry-run in a named session inside
the guest, then attach to the same session from SSH or the guest console:

```sh
# Inside the live guest, create once:
tmux new-session -d -s hexen-install -x 120 -y 40 \
  'env TERM=xterm-256color archinstall --dry-run --skip-version-check'

# Inside the live guest, attach:
tmux attach -t hexen-install

# From the host, attach through SSH instead:
ssh -t -i "$HOME/.ssh/hexen-vm" -o IdentitiesOnly=yes root@GUEST_IP \
  'tmux attach -t hexen-install'
```

Detach with **Ctrl-b**, then **d**. The installer continues to hold its menu
state inside the VM. Do not start another installer when this session exists.

An agent can use `tmux send-keys` and `tmux capture-pane -p` over SSH for text
menu research, without rendering screenshots. Hand terminal control to the
owner for encryption and account passwords, and do not capture or drive that
terminal during credential entry. Return to the main menu before handing
control back. Do not read or copy credential exports into the repository.

Finishing the dry-run saves configuration; it does not install Arch. The real
installation still requires interactive disk review, credentials, and final
confirmation. An incomplete research export without encryption is not a
reusable install profile.

### Transition to the real VM installation

The dated [investigation record](../archinstall/observations-2026-10-25.md)
tracks whether `hexen-install` currently contains a dry-run or the real
installer. Check the process arguments before sending Install/confirmation
keystrokes; the session name alone does not distinguish them.

After the owner enters credentials, exports needed to carry the state into
the real installer belong in a private runtime directory **inside the live
VM**, not in the repository:

```sh
install -d -m 0700 /run/hexen-install
# Save configuration/credentials here using Archinstall's Save menu.
chmod 0600 /run/hexen-install/user_configuration.json \
  /run/hexen-install/user_credentials.json
```

Do not display or copy the credential file. The live ISO's `/run` is temporary;
delete the runtime credential export after a successful installation, before
leaving the ISO. Ordinary installed account password hashes are a separate,
expected part of the installed system.

For the development VM, the prepared runtime configuration adds `git`,
`openssh`, and `qemu-guest-agent` from official repositories, enables the two
remote-access services, and places the dedicated **public** key in the regular
user's `authorized_keys`. This enables post-boot provisioning without copying
a private key or enabling root SSH access. These additions are specific to the
VM; do not silently carry them into the work-laptop package/service choices.

Review the non-secret configuration, especially the encryption target and
device, before loading it into a real interactive installer. Do not use
`--silent`. Stop at the final configuration confirmation for the owner to
review and confirm the disposable disk. After installation, inspect boot files
before rebooting, and verify the installed system's new SSH host key through
the console or guest agent.

References: [virt-install](https://github.com/virt-manager/virt-manager/blob/main/man/virt-install.rst),
[QEMU guest-agent protocol](https://www.qemu.org/docs/master/interop/qemu-ga-ref.html),
[Arch SSH installation](https://wiki.archlinux.org/title/Install_Arch_Linux_via_SSH).
