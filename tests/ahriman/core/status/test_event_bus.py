import pytest

from ahriman.core.status.event_bus import EventBus
from ahriman.models.event import EventType
from ahriman.models.package import Package


async def test_broadcast(event_bus: EventBus, package_ahriman: Package) -> None:
    """
    must broadcast event to all subscribers
    """
    _, queue = await event_bus.subscribe()
    await event_bus.broadcast(EventType.PackageUpdated, package_ahriman.base, version=package_ahriman.version)

    message = queue.get_nowait()
    assert message == (
        EventType.PackageUpdated,
        {"object_id": package_ahriman.base, "version": package_ahriman.version},
    )


async def test_broadcast_with_topics(event_bus: EventBus, package_ahriman: Package) -> None:
    """
    must broadcast event to subscribers with matching topics
    """
    _, queue = await event_bus.subscribe([EventType.PackageUpdated])
    await event_bus.broadcast(EventType.PackageUpdated, package_ahriman.base)
    assert not queue.empty()


async def test_broadcast_topic_isolation(event_bus: EventBus, package_ahriman: Package) -> None:
    """
    must not broadcast event to subscribers with non-matching topics
    """
    _, queue = await event_bus.subscribe([EventType.BuildLog])
    await event_bus.broadcast(EventType.PackageUpdated, package_ahriman.base)
    assert queue.empty()


async def test_broadcast_queue_full(event_bus: EventBus, package_ahriman: Package) -> None:
    """
    must discard message to slow subscriber
    """
    event_bus.max_size = 1
    _, queue = await event_bus.subscribe()

    await event_bus.broadcast(EventType.PackageUpdated, package_ahriman.base)
    await event_bus.broadcast(EventType.PackageRemoved, package_ahriman.base)
    assert queue.qsize() == 1


async def test_shutdown(event_bus: EventBus) -> None:
    """
    must send sentinel to all subscribers on shutdown
    """
    _, queue = await event_bus.subscribe()

    await event_bus.shutdown()
    message = queue.get_nowait()
    assert message is None


async def test_shutdown_queue_full(event_bus: EventBus, package_ahriman: Package) -> None:
    """
    must handle shutdown when queue is full
    """
    event_bus.max_size = 1
    _, queue = await event_bus.subscribe()

    await event_bus.broadcast(EventType.PackageUpdated, package_ahriman.base)
    await event_bus.shutdown()


async def test_subscribe(event_bus: EventBus) -> None:
    """
    must register new subscriber
    """
    subscriber_id, queue = await event_bus.subscribe()

    assert subscriber_id
    assert queue.empty()
    assert subscriber_id in event_bus._subscribers


async def test_subscribe_with_topics(event_bus: EventBus) -> None:
    """
    must register subscriber with topic filter
    """
    subscriber_id, _ = await event_bus.subscribe([EventType.BuildLog])
    topics, _ = event_bus._subscribers[subscriber_id]
    assert topics == [EventType.BuildLog]


async def test_unsubscribe(event_bus: EventBus) -> None:
    """
    must remove subscriber
    """
    subscriber_id, _ = await event_bus.subscribe()
    await event_bus.unsubscribe(subscriber_id)
    assert subscriber_id not in event_bus._subscribers


async def test_unsubscribe_unknown(event_bus: EventBus) -> None:
    """
    must not fail on unknown subscriber removal
    """
    await event_bus.unsubscribe("unknown")
