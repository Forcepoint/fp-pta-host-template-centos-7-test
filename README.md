# template-centos-7-test

This is a Packer process which creates a VM on a vSphere host.

For information about PTA and how to use it please visit https://github.com/Forcepoint/fp-pta-overview/blob/master/README.md

## Setup

Runs on either Windows of Linux.

Modify centos7.json so it has the appropriate values for your vsphere instance.

### Linux

You can use the Ansible roles 'packer' and 'vmware-workstation' to setup your environment, 
or just install things by hand.

### Windows

1. Install VMWare Workstation Pro.
   * Tested with version 14.
   * Ensure ovftool.exe is on the path.
1. Install Packer.
   * Tested with version 1.0.4
   * Ensure the executable is on the path.
1. Install Python 3.7

## Execution

### First Time

The first time you run this, you're going to have to run it on your own machine
because you need to create the template before you can create any PTA systems from it.

1. Create an SSH keypair. This keypair will be used to authenticate with your VMs via ansible.

        ssh-keygen -b 4096

1. Copy the contents of the id_rsa.pub file, and in the Jenkinsfile, replace the value of PACKER_SSH_PUB
with it. 
1. Put both the id_rsa and id_rsa.pub files in a secure location, like a password manager program.
I personally recommend KeePass.
1. Look at the Jenkinsfile. Set every environment variable it sets, and execute the commands listed.
If you're running on windows, you should be able to easily extrapolate what commands to run.

### Jenkins

Once you've got your pta-controller Jenkins system setup, you'll want to run this job through
Jenkins itself. 

* Be sure you create all of the credential objects referred to in the Jenkinsfile.

* At the bottom of the Jenkinsfile, ensure you change the email address to your PTA 
administrator's address so they get failure notifications.

* The last stage in the Jenkinsfile runs another job TestSystems. The idea is that this
job sets up test systems based upon this template. With the automatic reprovisioning
by Terraform, you're ensured to catch any issues early on that would appear from
conflicts between your ansible roles, terraform setup within VMware, and the base operating system packages.
When you're in the middle of recreating a production VM with PTA, the last thing
you want is to find out that your base template is borked somehow. This is one of the
best things about PTA - recreating your test applications weekly and detecting issues early.

* Also, once you have an Artifactory server setup and the yum repos that CentOS added as remotes,
you should modify the Jenkinsfile to set the default value of the PACKER_ARTIFACTORY_DNS parameter
to your Artifactory instance.

## Notes

* You may notice that I run Packer with the vmware-iso builder here, and not the vsphere-iso builder.
I do this because I found that the vsphere-iso builder wouldn't work with vSphere 6.0 or 6.5.
I could only get it to work with 6.7. Your experience may vary. Anyways, I wanted to include
a Packer example for using vmware-iso. If you want to convert this template process to use the
vsphere-iso builder instead, go for it! The template-windows-10-test example uses the 
vsphere-iso builder if you want something to follow during your conversion.

* The guest_os_type centos7-64 is not supported in ESXi 6.0 but it is available in ESXi 6.5.
I would really recommend not running this process against ESXi 6.0, but if you need to, you can.
  
* The default nic used by packer is e1000, which is not the recommended default by VMWare. 
Hard coding to vmxnet3 is preferable because Terraform will attempt to remove the e1000 nic and
add the vmxnet3 anyways, which is causing an error for some reason. This also caused issues
with the kickstart file, as the network had to be configured to ens192 instead of ens33 and
it had to be configured to start on boot. For whatever reason, ens192 via vmxnet3 wouldn't 
connect ipv4 after a reboot, while ens33 via e1000 would. Took me most of an entire day
to figure that out. 
https://www.lewan.com/blog/choosing-the-right-vmware-nic-should-you-replace-your-e1000-with-the-vmxnet3

* Also, in many packer examples, you'll see many ways to make files available to the install
process, including an http server that packer spins up dynamically. I found this to cause
me no end of trouble trying to get it to work consistently because I was running
packer from a VM itself, not on my own machine, which introduced networking difficulties.
After much headache trying to troubleshoot, I just switched back to the floppy drive approach.
As long as the OS you're installing has the drivers for a floppy drive, you're golden... 
