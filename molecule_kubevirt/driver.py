#  Copyright (c) 2015-2018 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
"""Kubevirt Driver Module."""

from __future__ import absolute_import

from molecule import logger, util
from molecule.api import Driver

log = logger.get_logger(__name__)


class KubeVirt(Driver):
    """
    Kubevirt Driver Class.
    ! Very alpha version - All configuration fields and behaviours may be subject to breaking changes !

    The class responsible for managing `Docker`_ containers.  `Docker`_ is
    the default driver used in Molecule.

    Molecule leverages Ansible's `kubevirt_vm`_ module, by mapping
    variables from ``molecule.yml`` into ``create.yml`` and ``destroy.yml``.

    .. _`kubevirt_vm`: https://docs.ansible.com/ansible/latest/collections/community/general/kubevirt_vm_module.html
    .. _`k8s`: https://docs.ansible.com/ansible/latest/collections/community/kubernetes/k8s_module.html

    .. code-block:: yaml

        driver:
          name: molecule-kubevirt
        platforms:
          - name: instance
            namespace: default
            wait_timeout: 300
            terminationGracePeriodSeconds: 0
            memory: 2Gi
            runStrategy: Always
            image: quay.io/kubevirt/fedora-cloud-container-disk-demo:latest

            annotations: (omit)

            cpu_cores: (omit)
            machine_type: q35
            cpu_model: (omit)

            autoattachGraphicsDevice: (omit)

            memory_request: memory
            cpu_request: (omit)
            memory_limit: memory
            cpu_limit: (omit)

            ssh_service:
                type: ClusterIP
                clusterIP: {}
                nodePort: {}
                nodePort_host: localhost

            volumes: []
            networks: []

            domain: {}
            user_data: {}

            hostname: (omit)
            livenessProbe: (omit)
            nodeSelector: (omit)
            readinessProbe: (omit)
            subdomain: (omit)
            tolerations: (omit)



    .. note:: Default ssh access point to VM Pod IP

    .. code-block:: bash

        $ python3 -m pip install molecule[kubevirt]

    Provide a list of files Molecule will preserve, relative to the scenario
    ephemeral directory, after any ``destroy`` subcommand execution.

    .. code-block:: yaml

        driver:
          name: kubevirt

    .. _`Kubevirt`: https://kubevirt.io/
    """  # noqa

    def __init__(self, config=None):
        """Construct Kubevirt."""
        super(KubeVirt, self).__init__(config)
        self._name = "molecule-kubevirt"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    # IMPORTANT : use NodePort for ssh ok (or port-forward ? => option)
    # https://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud-2009.qcow2
    @property
    def default_safe_files(self):
        return (
            []
        )  # FIXME : should ssh-keys generated by create.yml playbook be set as safe_file ?

    @property
    def login_cmd_template(self):
        connection_options = " ".join(self.ssh_connection_options)

        return (
            "ssh {{address}} "
            "-l {{user}} "
            "-p {{port}} "
            "-i {{identity_file}} "
            "{}"
        ).format(connection_options)

    @property
    def default_ssh_connection_options(self):
        return self._get_ssh_connection_options()

    def _get_instance_config(self, instance_name):
        instance_config_dict = util.safe_load_file(self._config.driver.instance_config)

        return next(
            item for item in instance_config_dict if item["instance"] == instance_name
        )

    def login_options(self, instance_name):
        d = {"instance": instance_name}

        return util.merge_dicts(d, self._get_instance_config(instance_name))

    def ansible_connection_options(self, instance_name):
        try:
            d = self._get_instance_config(instance_name)

            return {
                "ansible_user": d["user"],
                "ansible_host": d["address"],
                "ansible_port": d["port"],
                "ansible_private_key_file": d["identity_file"],
                "connection": "ssh",
                "ansible_ssh_common_args": " ".join(self.ssh_connection_options),
            }
        except StopIteration:
            return {}
        except IOError:
            # Instance has yet to be provisioned , therefore the
            # instance_config is not on disk.
            return {}

    def sanity_checks(self):
        # FIXME : What kind of sanity should be done ?
        # => testing connection to kubernetes ? testing kubevirt is OK ?
        """Implement some (?) driver sanity checks."""
        log.info("Sanity checks: '{}'".format(self._name))

    def reset(self):
        # FIXME : Kubevirt VMs are already destroyed if failed via destroy.yml
        # => what "reset could be implemented" ?
        log.info("Stopping (fake)")
