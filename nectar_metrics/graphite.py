import socket
import logging
import pickle
import struct
import time


logger = logging.getLogger(__name__)


class BaseSender(object):
    message_fmt = '%s %0.2f %d\n'

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def flush(self):
        pass

    def format_metric(self, metric, value, now):
        return self.message_fmt % (metric, value, now)

    def send_metric(self, metric, value, now):
        raise NotImplemented()

    def send_by_az(self, az, metric, value, time):
        return self.send_metric("az.%s.%s" % (az, metric), value, time)

    def send_by_az_by_domain(self, az, domain, metric, value, time):
        return self.send_metric("az.%s.domain.%s.%s"
                                % (az, domain, metric),
                                value, time)

    def send_by_tenant(self, tenant, metric, value, time):
        return self.send_metric("tenant.%s.%s"
                                % (tenant, metric),
                                value, time)

    def send_by_az_by_tenant(self, az, tenant, metric, value, time):
        return self.send_metric("az.%s.tenant.%s.%s"
                                % (az, tenant, metric),
                                value, time)


class DummySender(BaseSender):

    def send_metric(self, metric, value, now):
        message = self.format_metric(metric, value, now)
        print message
        return message


class SocketMetricSender(BaseSender):
    sock = None
    reconnect_at = 100
    flooding_at = 10000

    def __init__(self, host, port):
        super(SocketMetricSender, self).__init__()
        self.host = host
        self.port = port
        self.connect()
        self.count = 0

    def connect(self):
        if self.sock:
            self.sock.close()
            self.log.info("Reconnecting, %s sent so far." % self.count)
        else:
            self.log.info("Connecting")
        self.sock = socket.socket()
        self.sock.connect((self.host, self.port))
        self.log.info("Connected")

    def reconnect(self):
        self.connect()

    def send_metric(self, metric, value, now):
        message = self.format_metric(metric, value, now)
        self.count += 1
        if self.count % self.reconnect_at == 0:
            self.reconnect()
        if self.count % self.flooding_at == 0:
            self.log.info("Flooding the server, sleeping for 60.")
            time.sleep(60)
        self.sock.sendall(message)
        return message


class PickleSocketMetricSender(SocketMetricSender):
    sock = None
    reconnect_at = 500

    def __init__(self, host, port):
        super(PickleSocketMetricSender, self).__init__(host, port)
        self.buffered_metrics = []

    def send_metric(self, metric, value, now):
        self.count += 1
        self.buffered_metrics.append((metric, (now, float(value))))
        if self.count % self.reconnect_at == 0:
            self.flush()
            self.reconnect()
        if self.count % self.flooding_at == 0:
            self.log.info("Flooding the server, sleeping for 60.")
            time.sleep(60)
        return (metric, (now, float(value)))

    def flush(self):
        payload = pickle.dumps(self.buffered_metrics)
        header = struct.pack("!L", len(payload))
        message = header + payload
        self.sock.sendall(message)
        self.buffered_metrics = []
