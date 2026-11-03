# XPS 14 hybrid graphics

Implement the explicitly requested opt-in hardware profile for the owner's XPS
14 9440: Intel 8086:7d55 and NVIDIA 10de:28a1. Secure Boot remains deferred.
The existing generic/VM path and software profiles remain unchanged.

Approaches considered: automatic driver detection, an explicit inventory-validated hardware
profile, or manual driver setup. Use the explicit profile discussed with the
owner: it bounds support to the supplied inventory and makes updates repeatable.
Automatic guesses and manual-only setup would weaken installation readiness.

A read-only sysfs preflight rejects another model/GPU set, missing UEFI, enabled
or unreadable Secure Boot before package changes. Expose it independently for
Mint/live-media inventory. First boot and provisioning accept --hardware
xps-14-9440; provisioning persists selection so hexen config apply/update keep it.
The installer accepts the same selection and checks it before disk selection.

Install Arch's matched nvidia-open/nvidia-utils stack with Intel Mesa/Vulkan/media
support. Preserve the audited kernel/initramfs/boot format. Stable udev DRM links
and an opt-in UWSM environment fragment prefer Intel and include NVIDIA without
assuming card numbers. Do not hardcode Mint's XRandR monitor names, replace local
monitor settings, switch firmware modes, or enable Secure Boot. Changes require
a reboot before hardware acceptance, not live GPU rebinding.

Verification: sysfs fixtures for valid hardware and refusal cases, real wrapper
argument/persistence tests, isolated Ansible hardware tasks and idempotence,
full existing suite, syntax checks, and VM regression. Physical MST, KVM switching,
Zoom screen sharing, suspend/resume, and backup restore remain owner acceptance
steps. Software verification cannot certify the physical machine.
