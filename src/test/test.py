#!/usr/bin/env python

# Copyright 2007 Albert Strasheim <fullung@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import random
import sys
import time
import unittest

if not(len(sys.argv) == 2 and sys.argv[1] == 'release'):
    topdir = os.path.join(os.path.dirname(__file__), '..', '..')
    topdir = os.path.abspath(topdir)
    from distutils.util import get_platform
    if get_platform() == 'win32':
        sys.path.insert(0, os.path.join(topdir, 'win_build', 'debug'))
    else:
        plat_specifier = ".%s-%s" % (get_platform(), sys.version[0:3])
        build_base = os.path.join(topdir, 'build')
        build_platlib = os.path.join(build_base, 'lib' + plat_specifier)
        sys.path.insert(0, build_platlib)

import pyactivemq
print pyactivemq

class test_pyactivemq(unittest.TestCase):
    def test_dir(self):
        names = [
            'AcknowledgeMode',
            'ActiveMQConnectionFactory',
            'BytesMessage',
            'CMSException',
            'Closeable',
            'Connection',
            'ConnectionFactory',
            'DeliveryMode',
            'Destination',
            'DestinationType',
            'ExceptionListener',
            'MapMessage',
            'Message',
            'MessageConsumer',
            'MessageListener',
            'MessageProducer',
            'Queue',
            'Session',
            'Startable',
            'Stoppable',
            'TemporaryQueue',
            'TemporaryTopic',
            'TextMessage',
            'Topic'
            ]
        for name in names:
            self.assert_(name in dir(pyactivemq))

class test_AcknowledgeMode(unittest.TestCase):
    def test_values(self):
        from pyactivemq import AcknowledgeMode
        self.assertEqual(0, int(AcknowledgeMode.AUTO_ACKNOWLEDGE))
        self.assertEqual(1, int(AcknowledgeMode.DUPS_OK_ACKNOWLEDGE))
        self.assertEqual(2, int(AcknowledgeMode.CLIENT_ACKNOWLEDGE))
        self.assertEqual(3, int(AcknowledgeMode.SESSION_TRANSACTED))

class test_DeliveryMode(unittest.TestCase):
    def test_values(self):
        from pyactivemq import DeliveryMode
        self.assertEqual(0, DeliveryMode.PERSISTENT)
        self.assertEqual(1, DeliveryMode.NON_PERSISTENT)

class test_ActiveMQConnectionFactory(unittest.TestCase):
    def test_properties(self):
        from pyactivemq import ActiveMQConnectionFactory
        f1 = ActiveMQConnectionFactory()
        f2 = ActiveMQConnectionFactory('url')
        self.assertEqual('url', f2.brokerURL)
        f3 = ActiveMQConnectionFactory('url', 'user')
        self.assertEqual('url', f3.brokerURL)
        self.assertEqual('user', f3.username)
        f4 = ActiveMQConnectionFactory('url', 'user', 'pass')
        self.assertEqual('url', f4.brokerURL)
        self.assertEqual('user', f4.username)
        self.assertEqual('pass', f4.password)

class test_DestinationType(unittest.TestCase):
    def test_values(self):
        from pyactivemq import DestinationType
        self.assertEqual(0, DestinationType.TOPIC)
        self.assertEqual(1, DestinationType.QUEUE)
        self.assertEqual(2, DestinationType.TEMPORARY_TOPIC)
        self.assertEqual(3, DestinationType.TEMPORARY_QUEUE)

def random_topic(self, session):
    rand = random.Random()
    random_id = "%08x" % rand.randrange(0, 2**31)
    return session.createTopic("topic-%s" % random_id)

class _test_any_protocol:
    random_topic = random_topic

    def test_Connection(self):
        conn = self.conn
        self.assert_(conn.exceptionListener is None)
        self.assert_(isinstance(conn, pyactivemq.Closeable))
        self.assert_(isinstance(conn, pyactivemq.Connection))
        from pyactivemq import AcknowledgeMode
        self.conn.createSession(AcknowledgeMode.AUTO_ACKNOWLEDGE)
        self.conn.createSession(AcknowledgeMode.DUPS_OK_ACKNOWLEDGE)
        self.conn.createSession(AcknowledgeMode.CLIENT_ACKNOWLEDGE)
        self.conn.createSession(AcknowledgeMode.SESSION_TRANSACTED)
        conn.close()

    def test_Session(self):
        session = self.conn.createSession()
        self.assert_(isinstance(session, pyactivemq.Closeable))
        self.assert_(isinstance(session, pyactivemq.Session))
        self.assert_(not session.transacted)
        from pyactivemq import AcknowledgeMode
        ackmode = AcknowledgeMode.AUTO_ACKNOWLEDGE
        self.assertEqual(ackmode, session.acknowledgeMode)
        try:
            # check that attribute is read-only
            session.acknowledgeMode = ackmode
            self.assert_(False, 'Expected AttributeError exception to be raised')
        except AttributeError:
            pass
        session.close()

    def test_Topic_and_Queue(self):
        session = self.conn.createSession()
        topic = session.createTopic("topic")
        self.assertEqual("topic", topic.name)
        self.assert_(isinstance(topic, pyactivemq.Destination))
        topic2 = session.createTopic("topic2")
        queue = session.createQueue("queue")
        self.assertEqual("queue", queue.name)
        self.assert_(isinstance(queue, pyactivemq.Destination))
        queue2 = session.createQueue("queue2")
        self.assertEqual(topic, topic)
        self.assertNotEqual(topic, topic2)
        self.assertEqual(topic.destinationType, topic2.destinationType)
        self.assertNotEqual(topic, queue)
        self.assertEqual(queue, queue)
        self.assertNotEqual(queue, queue2)
        self.assertEqual(queue.destinationType, queue2.destinationType)
        self.assertNotEqual(queue, topic)

    def test_MessageConsumer(self):
        session = self.conn.createSession()
        topic = session.createTopic("topic")
        consumer1 = session.createConsumer(topic)
        self.assert_(isinstance(consumer1, pyactivemq.Closeable))
        self.assert_(isinstance(consumer1, pyactivemq.MessageConsumer))
        consumer2 = session.createConsumer(topic, "select1")
        self.assertEqual('select1', consumer2.messageSelector)
        try:
            consumer2.messageSelector = 'select2'
            # can't set message selector after consumer creation
            self.assert_(False, 'Expected AttributeError exception to be raised')
        except AttributeError:
            pass
        consumer3 = session.createConsumer(topic, "", True)

    def test_MessageProducer(self):
        session = self.conn.createSession()
        topic = session.createTopic("topic")
        producer = session.createProducer(topic)
        from pyactivemq import DeliveryMode
        self.assertEqual(DeliveryMode.PERSISTENT, producer.deliveryMode)
        producer.deliveryMode = DeliveryMode.PERSISTENT
        self.assertEqual(DeliveryMode.PERSISTENT, producer.deliveryMode)
        self.assertEqual(False, producer.disableMessageID)
        producer.disableMessageID = True
        self.assertEqual(True, producer.disableMessageID)
        self.assertEqual(False, producer.disableMessageTimeStamp)
        producer.disableMessageTimeStamp = True
        self.assertEqual(True, producer.disableMessageTimeStamp)
        # time to live of 0 means message never expires
        self.assertEqual(0, producer.timeToLive)
        # unit of time to live is milliseconds
        producer.timeToLive = 60
        self.assertEqual(60, producer.timeToLive)

    def xtest_durable_consumer(self):
        # TODO test durable subscription
        #session = self.conn.createSession()
        #subscriptionName = "mysub"
        #f = session.createDurableConsumer
        #consumer3 = f(topic, subscriptionName, "selector", False)
        #session.unsubscribe(subscriptionName)
        pass

    def test_TextMessage(self):
        session = self.conn.createSession()
        textMessage = session.createTextMessage()
        self.assert_(isinstance(textMessage, pyactivemq.Message))
        self.assert_(isinstance(textMessage, pyactivemq.TextMessage))
        textMessage.text = "bye"
        self.assertEqual("bye", textMessage.text)
        textMessage = session.createTextMessage("hello")
        self.assertEqual("hello", textMessage.text)

        textMessage.setIntProperty('int1', 123)
        self.assertEqual(1, len(textMessage.propertyNames))
        self.assertEqual('int1', textMessage.propertyNames[0])
        self.assert_(textMessage.destination is None)
        self.assert_(textMessage.replyTo is None)
        queue = session.createQueue("queue")
        textMessage.replyTo = queue
        self.assertEqual(queue, textMessage.replyTo)

    def test_BytesMessage(self):
        session = self.conn.createSession()
        bytesMessage = session.createBytesMessage()
        self.assert_(isinstance(bytesMessage, pyactivemq.Message))
        self.assert_(isinstance(bytesMessage, pyactivemq.BytesMessage))
        self.assertEqual(0, bytesMessage.bodyLength)
        bytesMessage.bodyBytes = 'hello123'
        self.assertEqual('hello123', bytesMessage.bodyBytes)
        self.assert_(bytesMessage.replyTo is None)
        queue = session.createQueue("queue")
        bytesMessage.replyTo = queue
        self.assertEqual(queue, bytesMessage.replyTo)

    def test_send_TextMessage(self):
        session = self.conn.createSession()

        textMessage = session.createTextMessage()
        queue = session.createQueue("queue")
        textMessage.replyTo = queue

        topic = self.random_topic(session)
        consumer = session.createConsumer(topic)
        self.assert_(consumer.messageListener is None)
        consumer2 = session.createConsumer(topic)
        # XXX doesn't work yet
        #consumer2.messageListener = MessageListener()
        producer = session.createProducer(topic)

        self.conn.start()
        producer.send(textMessage)
        msg = consumer.receive(1000)

        self.assert_(msg is not None)
        self.assertEqual(str(msg.destination), str(topic))
        self.assertEqual(topic, msg.destination)
        self.assertEqual(str(queue), str(msg.replyTo))
        self.assertEqual(queue, msg.replyTo)
        self.assert_(isinstance(msg, pyactivemq.Message))
        self.assert_(isinstance(msg, pyactivemq.TextMessage))

        msg = consumer.receive(50)
        self.assert_(msg is None)

    def test_send_BytesMessage(self):
        session = self.conn.createSession()
        topic = self.random_topic(session)
        consumer = session.createConsumer(topic)
        producer = session.createProducer(topic)
        bytesMessage = session.createBytesMessage()
        bytesMessage.bodyBytes = 'hello123'
        bytesMessage.replyTo = topic

        self.conn.start()
        producer.send(bytesMessage)
        msg = consumer.receive(1000)

        self.assert_(msg is not None)
        self.assertEqual('hello123', msg.bodyBytes)
        self.assertEqual(topic, msg.destination)
        self.assertEqual(str(topic), str(msg.destination))
        self.assertEqual(str(topic), str(msg.replyTo))
        self.assertEqual(topic, msg.replyTo)
        self.assert_(isinstance(msg, pyactivemq.Message))
        self.assert_(isinstance(msg, pyactivemq.BytesMessage))

        bytesMessage = session.createBytesMessage()
        bytesMessage.writeBytes('hello123')
        producer.send(bytesMessage)
        msg = consumer.receive(1000)
        self.assert_(msg is not None)
        # XXX this doesn't return anything yet
        #self.assertEqual('hello123', msg.readBytes())
        self.assertEqual('', msg.readBytes())

        msg = consumer.receive(50)
        self.assert_(msg is None)

    def test_BytesMessage_bodyBytes(self):
        session = self.conn.createSession()
        topic = self.random_topic(session)
        consumer = session.createConsumer(topic)
        producer = session.createProducer(topic)
        bytesMessage = session.createBytesMessage()
        bytesMessage.bodyBytes = '\x00\x00\x00'
        self.assertEqual(3, bytesMessage.bodyLength)

        self.conn.start()
        producer.send(bytesMessage)
        msg = consumer.receive(1000)

        self.assert_(msg is not None)
        self.assert_(isinstance(msg, pyactivemq.Message))
        self.assert_(isinstance(msg, pyactivemq.BytesMessage))
        self.assertEqual(3, msg.bodyLength)
        self.assertEqual('\x00\x00\x00', msg.bodyBytes)

        bytesMessage = session.createBytesMessage()
        bytesMessage.bodyBytes = '\x01\x02\x03'
        self.assertEqual(3, bytesMessage.bodyLength)
        producer.send(bytesMessage)
        msg = consumer.receive(1000)
        self.assert_(msg is not None)
        self.assert_(isinstance(msg, pyactivemq.Message))
        self.assert_(isinstance(msg, pyactivemq.BytesMessage))
        self.assertEqual(3, msg.bodyLength)
        self.assertEqual('\x01\x02\x03', msg.bodyBytes)

    def test_transaction(self):
        from pyactivemq import AcknowledgeMode
        session = self.conn.createSession(AcknowledgeMode.SESSION_TRANSACTED)
        self.assert_(session.transacted)
        topic = self.random_topic(session)
        consumer = session.createConsumer(topic)
        producer = session.createProducer(topic)
        textMessage = session.createTextMessage()
        textMessage.text = 'hello123'
        producer.send(textMessage)
        producer.send(textMessage)
        session.rollback()
        producer.send(textMessage)
        session.commit()
        msg = consumer.receive(1000)
        self.assert_(msg is not None)
        self.assertEqual('hello123', msg.text)
        # two sends were rolled back, so expect only one message
        msg = consumer.receive(500)
        self.assert_(msg is None)
        # roll session back so message is available again
        session.rollback()
        msg = consumer.receive(1000)
        self.assertEqual('hello123', msg.text)
        self.assert_(msg is not None)
        msg = consumer.receive(500)
        self.assert_(msg is None)

class test_stomp(_test_any_protocol, unittest.TestCase):
    def setUp(self):
        self.url = 'tcp://localhost:61613?wireFormat=stomp'
        from pyactivemq import ActiveMQConnectionFactory
        f = ActiveMQConnectionFactory(self.url)
        self.conn = f.createConnection()

    def tearDown(self):
        self.conn.close()
        del self.conn

    def test_temporary_topic(self):
        session = self.conn.createSession()
        # not implemented for stomp
        # XXX UserWarning says: caught unknown exception
        self.assertRaises(UserWarning, session.createTemporaryTopic)

    def test_temporary_queue(self):
        session = self.conn.createSession()
        # not implemented for stomp
        self.assertRaises(UserWarning, session.createTemporaryQueue)

    def test_MapMessage(self):
        session = self.conn.createSession()
        # not implemented for stomp
        self.assertRaises(UserWarning, session.createMapMessage)

class test_openwire(_test_any_protocol, unittest.TestCase):
    def setUp(self):
        self.url = 'tcp://localhost:61616?wireFormat=openwire'
        from pyactivemq import ActiveMQConnectionFactory
        f = ActiveMQConnectionFactory(self.url)
        self.conn = f.createConnection()

    def tearDown(self):
        self.conn.close()
        del self.conn

    def test_temporary_topic(self):
        session = self.conn.createSession()
        temptopic = session.createTemporaryTopic()
        self.assert_(len(temptopic.name) > 0)
        self.assert_(isinstance(temptopic, pyactivemq.Destination))
        self.assert_(not isinstance(temptopic, pyactivemq.Topic))

    def test_temporary_queue(self):
        session = self.conn.createSession()
        tempqueue = session.createTemporaryQueue()
        self.assert_(len(tempqueue.name) > 0)
        self.assert_(isinstance(tempqueue, pyactivemq.Destination))
        self.assert_(not isinstance(tempqueue, pyactivemq.Queue))

    def test_MapMessage(self):
        session = self.conn.createSession()
        mapMessage = session.createMapMessage()
        self.assert_(isinstance(mapMessage, pyactivemq.Message))
        self.assert_(isinstance(mapMessage, pyactivemq.MapMessage))
        mapMessage.setInt('int1', 123)
        self.assertEqual(123, mapMessage.getInt('int1'))
        self.assertEqual(1, len(mapMessage.mapNames))
        self.assert_('int1' in mapMessage.mapNames)

    def test_nolocal(self):
        # TODO this test might also apply to Stomp, but noLocal
        # doesn't seem to work when using Stomp at present
        session = self.conn.createSession()
        textMessage = session.createTextMessage()
        topic = self.random_topic(session)
        # consumer with empty selector
        consumer1 = session.createConsumer(topic, "")
        # consumer with empty selector and nolocal set
        consumer2 = session.createConsumer(topic, "", True)
        producer = session.createProducer(topic)
        self.conn.start()
        producer.send(textMessage)
        msg = consumer1.receive(2000)
        self.assert_(msg is not None)
        # nolocal consumer shouldn't receive the message
        msg = consumer2.receive(500)
        self.assert_(msg is None)

class _test_async:
    random_topic = random_topic

    class MessageListener(pyactivemq.MessageListener):
        def __init__(self, queue):
            pyactivemq.MessageListener.__init__(self)
            self.queue = queue

        def onMessage(self, message):
            # XXX TODO allow messages to be put into the queue. This
            # isn't currently possible because messages are always
            # deallocated after this method is called.
            self.queue.put(True)

    def test_multiple_sessions(self):
        nmessages = 100
        nconsumers = 3

        # create a single producer
        producer_session = self.conn.createSession()
        topic = self.random_topic(producer_session)
        producer = producer_session.createProducer(topic)

        # create infinite queue that is shared by consumers
        import Queue
        queue = Queue.Queue(0)

        # create multiple consumers in separate sessions
        # keep consumers in a list, because if we don't hold a
        # reference to the consumer, it is closed
        consumers = []
        for i in xrange(nconsumers):
            session = self.conn.createSession()
            consumer = session.createConsumer(topic)
            listener = self.MessageListener(queue)
            consumer.messageListener = listener
            consumers.append(consumer)

        self.conn.start()
        textMessage = producer_session.createTextMessage()
        for i in xrange(nmessages):
            textMessage.text = 'hello%d' % (i,)
            producer.send(textMessage)

        qsize = nmessages * nconsumers
        try:
            for i in xrange(qsize):
                queue.get(block=True, timeout=5)
        except Queue.Empty:
            self.assert_(False, 'Expected %d messages in queue' % qsize)
        self.assert_(queue.empty())

class test_stomp_async(_test_async, unittest.TestCase):
    def setUp(self):
        self.url = 'tcp://localhost:61613?wireFormat=stomp'
        from pyactivemq import ActiveMQConnectionFactory
        f = ActiveMQConnectionFactory(self.url)
        self.conn = f.createConnection()

    def tearDown(self):
        self.conn.close()
        del self.conn

class test_openwire_async(_test_async, unittest.TestCase):
    def setUp(self):
        self.url = 'tcp://localhost:61616?wireFormat=openwire'
        from pyactivemq import ActiveMQConnectionFactory
        f = ActiveMQConnectionFactory(self.url)
        self.conn = f.createConnection()

    def tearDown(self):
        self.conn.close()
        del self.conn

# XXX Sleep, let exception listener fire and then do keyboard
# interrupt.  Leads to a crash while deleting Connection object, which
# looks similar to what is reported here:
# http://issues.apache.org/activemq/browse/AMQCPP-46
#time.sleep(100000)

if __name__ == '__main__':
    unittest.main(argv=sys.argv)