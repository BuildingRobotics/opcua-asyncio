
import asyncio
import logging
from opcua import Client

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('opcua')


class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """
    def event_notification(self, event):
        print("New event recived: ", event)


async def task(loop):
    # url = "opc.tcp://commsvr.com:51234/UA/CAS_UA_Server"
    url = "opc.tcp://localhost:4840/freeopcua/server/"
    # url = "opc.tcp://admin@localhost:4840/freeopcua/server/"  #connect using a user
    try:
        async with Client(url=url) as client:
            # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
            root = client.get_root_node()
            _logger.info("Objects node is: %r", root)

            # Now getting a variable node using its browse path
            obj = await root.get_child(["0:Objects", "2:MyObject"])
            _logger.info("MyObject is: %r", obj)

            myevent = await root.get_child(["0:Types", "0:EventTypes", "0:BaseEventType", "2:MyFirstEvent"])
            _logger.info("MyFirstEventType is: %r", myevent)

            msclt = SubHandler()
            sub = await client.create_subscription(100, msclt)
            handle = await sub.subscribe_events(obj, myevent)
            await sub.unsubscribe(handle)
            await sub.delete()
    except Exception:
        _logger.exception('Error')
    loop.stop()


def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(task(loop))
    loop.close()


if __name__ == "__main__":
    main()
