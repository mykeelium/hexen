# Remote access to the Hexen desktop

Hexen's remote desktop is an on-demand view of the **currently logged-in
Hyprland session**. It lets another computer control that session and use the
desktop machine's files and resources. It does not start a second desktop
session. Open applications and workspaces in the current session are visible to
the remote viewer.

Remote desktop support is retained in this repository for possible later use,
but it is **disabled by default**. A normal workstation install does not install
OpenSSH or WayVNC for this feature, or link its helper or user service. To opt
in on a specific machine later, set
`desktop_remote_access_enabled: true` in the ignored
`ansible/group_vars/all/local.yml`. This also installs OpenSSH and WayVNC from
Arch's official repositories. WayVNC comes from the signed
[`extra/wayvnc`](https://archlinux.org/packages/extra/x86_64/wayvnc/) package
when opted in. Its user service is deliberately not enabled at login.
`hexen-remote start` starts it for the active graphical session;
`hexen-remote stop` stops it. The VNC listener binds only to
`127.0.0.1:5900`, so VNC traffic must travel through an SSH tunnel. Do not
change the bind address to `0.0.0.0` or add port 5900 to the firewall. This
follows [WayVNC's SSH-tunnel guidance](https://github.com/any1/wayvnc#running).

## One-time SSH setup on the desktop

SSH is an opt-in network service. The optional package does not enable `sshd`
or open the firewall. A public key is recommended, but it is not
required: the server can also accept the desktop account's login password.
Never put private keys, passwords, or recovery codes in this repository.

1. For key authentication, create a key on the client if you do not already
   have one:

   ```sh
   ssh-keygen -t ed25519
   ```

2. Transfer only the `.pub` file to the desktop using a method you trust. On
   the desktop, add it to the account that will run Hyprland. Skip this step if
   you intend to use password authentication only:

   ```sh
   install -d -m 0700 ~/.ssh
   cat /path/to/client-key.pub >> ~/.ssh/authorized_keys
   chmod 0600 ~/.ssh/authorized_keys
   ```

3. Configure SSH on the desktop. Replace `mcuomo` with the actual
   desktop account name:

   ```sh
   sudo install -d -m 0755 /etc/ssh/sshd_config.d
   printf '%s\n' \
     'PubkeyAuthentication yes' \
     'PasswordAuthentication yes' \
     'KbdInteractiveAuthentication no' \
     'PermitRootLogin no' \
     'AllowUsers mcuomo' \
     | sudo tee /etc/ssh/sshd_config.d/40-hexen-remote.conf
   sudo ssh-keygen -A
   sudo sshd -t
   ```

   Before starting SSH, print the desktop's host-key fingerprint at its local
   console and compare it with the fingerprint shown by the first SSH
   connection:

   ```sh
   sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
   ```

4. Start SSH. The Hexen firewall still blocks inbound connections at this
   point:

   ```sh
   sudo systemctl enable --now sshd
   ```

5. Permit SSH from only the client computer's current IP address. Replace the
   sample address with the **source address seen by the desktop**. Start with a
   runtime-only rule so it disappears after a firewall reload or reboot:

   ```sh
   sudo firewall-cmd --zone=drop \
     --add-rich-rule='rule family="ipv4" source address="192.168.1.25/32" service name="ssh" accept'
   ```

   From the client, verify login (using the key or account password) and compare the host-key fingerprint
   before accepting it:

   ```sh
   ssh mcuomo@<desktop-address>
   ```

   After that succeeds, make the same source-restricted rule persistent by
   adding `--permanent` to the `firewall-cmd` command and running
   `sudo firewall-cmd --reload`. To preserve the exception when Ansible reapplies
   Hexen's managed zone, set `base_firewall_ssh_sources` in the ignored
   `ansible/group_vars/all/local.yml` file to a list containing this client
   address, such as:

   ```yaml
   base_firewall_ssh_sources:
     - 192.168.1.25/32
   ```

   Its default is empty, so no SSH access is opened on other machines. If the
   client's address changes, update the rule.
   For access across networks, use a VPN and restrict SSH to the VPN client's
   address or subnet; do not expose SSH or VNC to the public internet.

## One-command desktop connection

From the client computer, run the repository helper with the desktop's SSH
destination (an IP address or an alias from `~/.ssh/config`). Run it from a
Hexen repository checkout, or copy `config/bin/hexen-remote-client` to the
client:

```sh
./config/bin/hexen-remote-client mcuomo@<desktop-address>
```

The helper uses SSH to start WayVNC on the desktop, opens a loopback-only SSH
tunnel, and launches `remote-viewer` on the client. Close the viewer to stop the
WayVNC service and SSH tunnel. The client needs Bash, OpenSSH, Python 3, and
`remote-viewer` (Arch package `virt-viewer`). If using another viewer, set
`HEXEN_REMOTE_VIEWER` to its executable before running the helper. An optional
`HEXEN_SSH_CONFIG` environment variable selects a specific SSH config file.
If the repository has `.local/remote-ssh.conf`, the helper uses it automatically
for the destination alias and client key settings. That machine-local file is
ignored by Git.

For the current rehearsal VM, the host checkout already has an ignored alias
and a verified host-key pin. Run:

```sh
./config/bin/hexen-remote-client hexen-rehearsal
```

The helper uses the existing `~/.ssh/hexen-vm` key. You do not need to type the
desktop account password when that key is available; password login is enabled
as a fallback. The password prompt, if needed, is for the `mcuomo` Linux login,
not the disk-encryption passphrase.

To stop remote access manually on the desktop, run `hexen-remote stop`. Check
service state or logs there with:

```sh
hexen-remote status
journalctl --user -u hexen-remote.service --since today
```

The SSH server and firewall setup above is still required once. A plain
`ssh user@desktop` opens a shell; it cannot display the desktop. The one-command
helper invokes SSH and the local VNC viewer for you.

This grants the client the same practical control as someone at the desktop:
remote keyboard and pointer input can interact with the unlocked session and
its files. Start it only when needed, stop it afterward, and protect the SSH
private key. If the desktop session is locked, the remote viewer may display
the lock screen; keep the normal lock-screen password enabled.

## Current validation status

The rehearsal VM proved that WayVNC can capture a Hyprland output, accept remote
keyboard and pointer input, and be reached through an SSH tunnel while bound
to loopback. The new `--desktop` command also started in the VM on loopback and
completed an RFB handshake that reported the active 1280x800 output. A separate
Hyprland session launched over SSH did not work in the VM because it could not
acquire a seat or initialize a usable display. A full viewer check of rendered
frames, input, and multi-monitor layout through the managed service remains
open. On 2026-10-29 the rehearsal VM was configured for key and password SSH;
root login is disabled, and firewalld permits SSH only from the host's
`192.168.122.1/32` VM-network address. The persistent user service and helper
are linked to the VM checkout. An ignored host alias pins the VM host key and
uses the existing host keypair. The one-command helper was exercised end to end
with a protocol test viewer: it authenticated, started the service, established
the tunnel, completed a 1280x800 RFB handshake, sent pointer input, and stopped
the service and tunnel when the viewer exited. The separate real viewer
connection also accepted remote pointer input, and stopping the service closed
it. The rendered image, lock-screen workflow, and multi-monitor behavior have
not been visually accepted.
