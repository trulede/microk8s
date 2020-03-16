import string
import random

import pytest
import os
import subprocess
from os import path

from validators import (
    validate_dns_dashboard,
)
from utils import (
    microk8s_enable,
    wait_for_pod_state,
    microk8s_disable,
    microk8s_reset,
    microk8s_clustering_capable
)



class VM:

    def __init__(self, attach_vm=None):
        rnd_leters = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
        channel_to_test = os.environ.get('CHANNEL_TO_TEST', 'edge/test-dqlite')
        self.backend = "none"
        self.vm_name = "vm-{}".format(rnd_leters)
        if attach_vm:
            self.vm_name = attach_vm

        if path.exists('/snap/bin/multipass'):
            print('Creating mulitpass VM')
            self.backend = "multipass"
            if not attach_vm:
                subprocess.check_call('/snap/bin/multipass launch 18.04 -n {} -m 2G'.format(self.vm_name).split())
                subprocess.check_call('/snap/bin/multipass exec {}  -- sudo '
                                      'snap install microk8s --classic --channel {}'.format(self.vm_name, channel_to_test)
                                      .split())
            else:
                subprocess.check_call('/snap/bin/multipass exec {}  -- sudo '
                                      'snap refresh microk8s --channel {}'.format(self.vm_name, channel_to_test)
                                      .split())

        elif path.exists('/snap/bin/lxc'):
            print('Creating lxc container')
            self.backend = "lxc"
            if not attach_vm:
                try:
                    subprocess.check_call('/snap/bin/lxc profile show microk8s'.split())
                except subprocess.CalledProcessError:
                    subprocess.check_call('/snap/bin/lxc profile show microk8s'.split())
                    with open('lxc/microk8s.profile', "r+") as fp:
                        profile_string = fp.read()
                        process = subprocess.Popen('/snap/bin/lxc profile edit microk8s',
                                                   stdin=subprocess.PIPE,
                                                   stdout=subprocess.PIPE)
                        process.stdin.write(profile_string)
                        process.stdin.close()

                subprocess.check_call('/snap/bin/lxc launch -p default -p microk8s ubuntu:18.04 {}'
                                      .format(self.vm_name).split())
            else:
                subprocess.check_call('/snap/bin/lxc exec {}  -- sudo '
                                      'snap refresh microk8s --channel {}'.format(self.vm_name, channel_to_test)
                                      .split())

        else:
            raise Exception("Need to install multipass of lxc")

    def run(self, cmd):
        if self.backend == "multipass":
            output = subprocess.check_output('/snap/bin/multipass exec {}  -- sudo '
                                             '{}'.format(self.vm_name, cmd)
                                             .split())
            return output
        elif self.backend == "lxc":
            output = subprocess.check_output('/snap/bin/multipass exec {}  -- sudo '
                                             '{}'.format(self.vm_name, cmd)
                                             .split())
            return output
        else:
            raise Exception("Not implemented for backend {}".format(self.backend))

    def release(self):
        print("Destroying VM in {}".format(self.backend))
        if self.backend == "multipass":
            subprocess.check_call('/snap/bin/multipass stop {}'.format(self.vm_name).split())
            subprocess.check_call('/snap/bin/multipass delete {}'.format(self.vm_name).split())
        elif self.backend == "lxc":
            subprocess.check_call('/snap/bin/lxc stop {}'.format(self.vm_name).split())
            subprocess.check_call('/snap/bin/lxc delete {}'.format(self.vm_name).split())


class TestCluster(object):

    @pytest.fixture(autouse=True, scope="module")
    def setup_cluster(self):
        print("Setting up cluster")
        self.VM = []
        '''
        size = 3
        for i in range(0, size):
            self.VM.append(VM())
        '''
        self.VM.append(VM('vm-ldzcjb'))
        self.VM.append(VM('vm-nfpgea'))
        self.VM.append(VM('vm-pkgbtw'))
        yield
        print("Cleanup up cluster")
        for vm in self.VM:
            print("VM {} in {}".format(vm.vm_name, vm.backend))
            #vm.release()

    def test_basic(self):
        """
        Sets up and tests dashboard, dns in a two node cluster.

        """

        print("Testing cluster")

    def test_advance(self):
        """
        Sets up and tests dashboard, dns in a two node cluster.

        """
        print("Advance testing cluster")
