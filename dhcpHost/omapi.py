# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from django.conf import settings
import struct
from pypureomapi import Omapi, OmapiMessage, OmapiError, OMAPI_OP_UPDATE,OMAPI_OP_STATUS, pack_mac, OmapiErrorNotFound

class NacOmapi(Omapi):

    instance = None

    def add_group(self, name, gateway):
        msg = OmapiMessage.open(b"group")
        msg.message.append((b"create", struct.pack("!I", 1)))
        msg.obj.append((b"name", str(name)))
        msg.obj.append((b"statements", b"option routers %s;" % str(gateway)))
        response = self.query_server(msg)
        if response.opcode != OMAPI_OP_UPDATE:
           raise OmapiError("add group failed")

    def del_group(self, name):
        msg = OmapiMessage.open(b"group")
        msg.obj.append((b"name", str(name)))
        response = self.query_server(msg)
        if response.opcode != OMAPI_OP_UPDATE:
            raise OmapiErrorNotFound()
        if response.handle == 0:
            raise OmapiError("received invalid handle from server")
        response = self.query_server(OmapiMessage.delete(response.handle))
        if response.opcode != OMAPI_OP_STATUS:
            raise OmapiError("delete failed")

    def add_host_with_group(self, mac, groupname):
        """Create a host object with given mac address and group.
        @type mac: str
        @type groupname: str
        @raises ValueError:
        @raises OmapiError:
        @raises socket.error:
        """
        msg = OmapiMessage.open(b"host")
        msg.message.append((b"create", struct.pack("!I", 1)))
        msg.message.append((b"exclusive", struct.pack("!I", 1)))
        msg.obj.append((b"hardware-address", pack_mac(mac)))
        msg.obj.append((b"hardware-type", struct.pack("!I", 1)))
        msg.obj.append((b"group", str(groupname)))
        response = self.query_server(msg)
        if response.opcode != OMAPI_OP_UPDATE:
            raise OmapiError("Adding host '%s' failed" % mac)

    @staticmethod
    def get_instance():
        if NacOmapi.instance is None:
            try:
                NacOmapi.instance = NacOmapi(settings.OMAPI_IP, settings.OMAPI_PORT, settings.OMAPI_KEYNAME, settings.OMAPI_KEY)
            except OmapiError, err:
                print "an error occured: %r" % (err,)
        return NacOmapi.instance

    def close(self):
        NacOmapi.instance = None
        Omapi.close(self)
