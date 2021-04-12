#!/usr/bin/python3

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

import openstack
from progress.bar import Bar
from progress.spinner import Spinner
import sh
import requests
from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type
import time

DOCUMENTATION = r'''
---
module: my_test

short_description: This is my test module

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: This is my longer description explaining my test module.

options:
    name:
        description: This is the message to send to the test module.
        required: true
        type: str
    new:
        description:
            - Control to demo if the result of this module is changed or not.
            - Parameter description can be a list as well.
        required: false
        type: bool
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - my_namespace.my_collection.my_doc_fragment_name

author:
    - Your Name (@yourGitHubHandle)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  my_namespace.my_collection.my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_namespace.my_collection.my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_namespace.my_collection.my_test:
    name: fail me
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(type='str', required=True),
        file=dict(type='str', required=False, default=""),
        url=dict(type='str', required=False, default=""),
        retries_num=dict(type='int', required=False, default=5),
        id=dict(type='str', required=False, default=""),
        protected=dict(type='bool', required=False, default=False),
        public=dict(type='bool', required=False, default=False),
        shared=dict(type='bool', required=False, default=False),
        private=dict(type='bool', required=False, default=False),
        community=dict(type='bool', required=False, default=False),
        container_format=dict(type='str', required=False, default=""),
        disk_format=dict(type='str', required=False, default=""),
        min_disk=dict(type='str', required=False, default=""),
        min_ram=dict(type='str', required=False, default=""),
        volume=dict(type='str', required=False, default=""),
        project=dict(type='str', required=False, default=""),
        project_domain=dict(type='str', required=False, default=""),
        properties=dict(type='dict', required=False, default=dict()),
        tags=dict(type='list', required=False, default=list())
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    name = module.params['name']
    file = module.params['file']
    url = module.params['url']
    retries_num = module.params['retries_num']
    id = module.params['id']
    protected = module.params['protected']
    public = module.params['public']
    private = module.params['private']
    community = module.params['community']
    shared = module.params['shared']
    container_format = module.params['container_format']
    disk_format = module.params['disk_format']
    min_disk = module.params['min_disk']
    min_ram = module.params['min_ram']
    volume = module.params['volume']
    properties = module.params['properties']
    tags = module.params['tags']
    project = module.params['project']
    project_domain = module.params['project_domain']


    # Build the image attributes
    image_attrs = {
        'name': name,
    }
    sources = 0
    if file != '':
        image_attrs['filename'] = file
        sources += 1
    if url != '':
        image_attrs['filename'] = r'/tmp/os_create_tmp/'+name+'/'+name
        sources += 1
    if volume != '':
        image_attrs['volume'] = volume
        sources += 1
    if sources != 1:
        module.fail_json(msg="Exact one source should be determined from the list below: file, url, volume", **result)

    if project_domain != "" and project == "":
        module.fail_json(msg="Project domain should be determined with project", **result)

    share_policy = 0
    if shared is True:
        image_attrs['shared'] = True
        share_policy += 1
    if public is True:
        image_attrs['public'] = True
        share_policy += 1
    if private is True:
        image_attrs['private'] = True
        share_policy += 1
    if community is True:
        image_attrs['community'] = True
        share_policy += 1
    if share_policy != 1:
        module.fail_json(msg="Exact one share policy should be determined from the list below: public, shared, private, community", **result)

    if id != '':
        image_attrs['id'] = id
    if protected != '':
        image_attrs['protected'] = protected
    if container_format != '':
        image_attrs['container_format'] = container_format
    if disk_format != '':
        image_attrs['disk_format'] = disk_format
    if min_disk != '':
        image_attrs['min_disk'] = min_disk
    if min_ram != '':
        image_attrs['min_ram'] = min_ram
    if disk_format != '':
        image_attrs['disk_format'] = disk_format
    if project != '':
        image_attrs['project'] = project
    if project_domain != '':
        image_attrs['project_domain'] = project_domain
    if module.params['properties'] != "":
        image_attrs['properties'] = module.params['properties']
    if module.params['tags'] != "":
        image_attrs['tags'] = module.params['tags']


    if url != "":

        try:
            sh.mkdir("/tmp/os_create_tmp/"+name, "-p")
        except sh.ErrorReturnCode_1:
            pass
        except sh.ErrorReturnCode:
            module.fail_json(msg="Failed to create tmp directory", **result)

        # Try getting header of remote image

        header_failed = True
        for i in range(retries_num):
            remote_image = requests.get(url, stream=True)
            if remote_image.ok:
                header_failed = False
                break
            time.sleep(1)

        if header_failed:
            module.fail_json(msg='Unable to get remote image in ' +
            str(retries_num) + ' attempts', **result)

        # Check we are the only instance
        grep_out = 0
        try:
            grep_out = sh.grep(sh.df(), "/tmp/os_create_tmp/"+name, "-c")
        except sh.ErrorReturnCode_1:
            grep_out = 1
        except:
            module.fail_json(
            msg="", **result)
        if grep_out == 0:
            module.fail_json(
            msg="Can't mount temporary filesystem: is there another instance of module with same image name?", **result)

        # Mounting temporary filesystem
        try:
            # with sh.contrib.sudo:
            sh.mount("tmpfs", "/tmp/os_create_tmp/"+name, t="tmpfs",
                    o="size="+str(1000000 + int(remote_image.headers['Content-length'])))
            # Downloading image
            with open(r'/tmp/os_create_tmp/'+name+'/'+name, "wb") as local_image:
                with Bar('Downloading', max=int(remote_image.headers['Content-length']), suffix='%(percent).1f%% - %(eta)ds') as bar:
                    for chunk in remote_image.iter_content(chunk_size=1000):
                        bar.next(n=len(chunk))
                        local_image.write(chunk)
            # Establishing connection to OpenStack
            try:
                conn = openstack.connection.from_config(cloud="openstack")
            except:
                sh.umount("/tmp/os_create_tmp/"+name)
                module.fail_json(msg='Unable to connect to OpenStack', **result)

            # Upload the image.
            with Spinner("Uploading to OpenStack... "):
                try:
                    conn.image.create_image(**image_attrs)
                except Exception as e:
                    sh.umount(r"/tmp/os_create_tmp/"+name)
                    module.fail_json(msg='Unable to create image: '+str(e), **result)
            # with sh.contrib.sudo:
        except sh.ErrorReturnCode:
            sh.umount(r"/tmp/os_create_tmp/"+name)
            module.fail_json(msg="Failed to mount temporary filesystem", **result)
    else:
        with Spinner("Uploading to OpenStack... "):
            try:
                conn.image.create_image(**image_attrs)
            except Exception as e:
                module.fail_json(msg='Unable to create image: ' + str(e), **result)

    # result['original_message'] = module.params['url']
    result['message'] = 'Successfully uploaded an image'

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    # if module.params['new']:
    result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result

    # if module.params['name'] == 'fail me':
    # module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
