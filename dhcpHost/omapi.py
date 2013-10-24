# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from django.conf import settings
import struct
from pypureomapi import Omapi, OmapiMessage, OmapiError, OMAPI_OP_UPDATE, pack_mac

class NacOmapi(Omapi):

    instance = None

    def add_host_with_gateway(self, mac, gateway):
        """Create a host object with given mac address and gateway (router).
        @type mac: str
        @type gateway: str
        @raises ValueError:
        @raises OmapiError:
        @raises socket.error:
        """
        msg = OmapiMessage.open(b"host")
        msg.message.append((b"create", struct.pack("!I", 1)))
        msg.message.append((b"exclusive", struct.pack("!I", 1)))
        msg.obj.append((b"hardware-address", pack_mac(mac)))
        msg.obj.append((b"hardware-type", struct.pack("!I", 1)))
        msg.obj.append(("statements", "supersede routers %s;" % gateway))
        response = self.query_server(msg)
        if response.opcode != OMAPI_OP_UPDATE:
            raise OmapiError("Adding host '%s' failed" % mac)

    @staticmethod
    def get_instance():
        if not NacOmapi.instance:
            try:
                NacOmapi.instance = NacOmapi(settings.OMAPI_IP, settings.OMAPI_PORT, settings.OMAPI_KEYNAME, settings.OMAPI_KEY)
            except OmapiError, err:
                print "an error occured: %r" % (err,)
        return NacOmapi.instance

    def close(self):
        NacOmapi.instance = None
        Omapi.close(self)
