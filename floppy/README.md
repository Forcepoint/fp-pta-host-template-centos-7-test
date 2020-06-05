# floppy

This folder is mounted into the VM as a floppy disk and is accessible from the kickstart file.
Infact, the kickstart file is made available via the floppy drive. So don't delete this folder,
even if you don't add an certs to it.

I found the most useful thing to do here is to put any root or intermediate certificates
that you know you'll need across most of your PTA VMs, then they're available to be copied
and installed in the trust store during the kickstart. See cfg/templates/ks.cfg for a few
commented lines on how to do this.

I've seen many packer processes and kickstart processes that cram a ton of stuff into the 
floppy drive and execute them during the kickstart. I found trying to debug these
types of setups to very painful because of how long the unattended install takes to run,
not to mention you get very limited output as to what's going on.
My 2 cents is to install the bare minimum to get a successful ansible connection to the
machine. Save the crazy stuff for your ansible roles you execute after you've Terraformed, 
and if you must do something crazy during the packer setup, 
do it with a packer provisioners instead of during the kickstart.