"""
 Author: Jeremy Cornett
   Date: 10/23/2017
Purpose: Populate a file with sensitive data contained in environment variables so said secrets aren't
         committed to source code control. http://jinja.pocoo.org/docs/2.9/api/

https://marclop.svbtle.com/creating-an-automated-centos-7-install-via-kickstart-file
http://jinja.pocoo.org/docs/2.9/api/

ASSUMPTIONS: This is run on windows and linux. passlib is not linux specific.
"""

import os
from passlib.hash import sha512_crypt
from jinja2 import Environment, FileSystemLoader


def encrypt_string_sha512(a_string):
    """Encrypt a given string with SHA512. Useful for encrypting passwords.
    :param a_string: The string to encrypt.
    :return: The encrypted string.
    """
    return sha512_crypt.hash(a_string)


def main():
    """The main function.
    :return: None
    """
    env = Environment(loader=FileSystemLoader('templates'))

    template_ks_cfg = env.get_template("ks.cfg")

    path_floppy = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "floppy"))
    if not os.path.exists(path_floppy):
        os.makedirs(path_floppy)

    artifactory_dns = None
    if "PACKER_ARTIFACTORY_DNS" in os.environ and os.environ["PACKER_ARTIFACTORY_DNS"] != "":
        artifactory_dns = os.environ["PACKER_ARTIFACTORY_DNS"]

    with open(os.path.join(path_floppy, "ks.cfg"), "w", newline='\n') as file_ks_cfg:
        file_ks_cfg.write(template_ks_cfg.render(hostname=os.environ["PACKER_HOST_NAME"],
                                                 root_password=encrypt_string_sha512(
                                                     os.environ["PACKER_CENTOS7_ROOT_PASSWORD"]),
                                                 timezone=os.environ["PACKER_TIMEZONE"],
                                                 user_name=os.environ["PACKER_CENTOS7_USER_NAME"],
                                                 user_password=encrypt_string_sha512(
                                                     os.environ["PACKER_CENTOS7_USER_PASSWORD"]),
                                                 ssh_pub=os.environ["PACKER_SSH_PUB"],
                                                 artifactory=artifactory_dns))


if __name__ == "__main__":
    main()
