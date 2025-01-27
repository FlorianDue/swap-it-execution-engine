
from asyncua import ua
from datetime import datetime



class CallbackEvents:

    def __init__(self, server_instance, server):
        self.server = server
        self.server_instance = server_instance
        self.service_started_event = server_instance.data_object.opcua_declarations.service_started_event
        self.service_finished_event = server_instance.data_object.opcua_declarations.service_finished_event
        self.task_started_event = server_instance.data_object.opcua_declarations.task_started_event
        self.task_finished_event = server_instance.data_object.opcua_declarations.task_finished_event
        print("self.service_started_event", self.service_started_event)
        print("self.service_finished_event", self.service_finished_event)
        print("self.task_started_event", self.task_started_event)
        print("self.task_finished_event", self.task_finished_event)
        self.server_node = self.server.get_node("ns=0;i=2253")

    async def fire_service_started_event(self, uuid, name):
        startedevent = await self.server.get_event_generator(self.service_started_event)
        startedevent.event.time = ua.Variant(str(datetime.now()), ua.VariantType.String)
        startedevent.event.service_name = ua.Variant(str(name), ua.VariantType.String)
        startedevent.event.service_uuid = ua.Variant(str(uuid), ua.VariantType.String)
        startedevent.event.ee_url = ua.Variant(str(self.server_instance.server_url), ua.VariantType.String)
        print(startedevent.event)
        await startedevent.trigger()

    async def fire_service_finished_event(self, uuid, name):
        finishedevent = await self.server.get_event_generator(self.service_finished_event)
        finishedevent.event.time = ua.Variant(str(datetime.now()), ua.VariantType.String)
        finishedevent.event.service_name = ua.Variant(str(name), ua.VariantType.String)
        finishedevent.event.service_uuid = ua.Variant(str(uuid), ua.VariantType.String)
        finishedevent.event.ee_url = ua.Variant(str(self.server_instance.server_url), ua.VariantType.String)
        print(finishedevent.event)
        await finishedevent.trigger()

    async def fire_task_started_event(self, uuid, name):
        startedevent = await self.server.get_event_generator(self.task_started_event)
        startedevent.event.time = ua.Variant(str(datetime.now()), ua.VariantType.String)
        startedevent.event.task_name = ua.Variant(str(name), ua.VariantType.String)
        startedevent.event.task_uuid = ua.Variant(str(uuid), ua.VariantType.String)
        startedevent.event.ee_url = ua.Variant(str(self.server_instance.server_url), ua.VariantType.String)
        print(startedevent.event)
        await startedevent.trigger()

    async def fire_task_finished_event(self, uuid, name):
        finishedevent = await self.server.get_event_generator(self.task_finished_event)
        finishedevent.event.time = ua.Variant(str(datetime.now()), ua.VariantType.String)
        finishedevent.event.task_name = ua.Variant(str(name), ua.VariantType.String)
        finishedevent.event.task_uuid = ua.Variant(str(uuid), ua.VariantType.String)
        finishedevent.event.ee_url = ua.Variant(str(self.server_instance.server_url), ua.VariantType.String)
        print(finishedevent.event)
        await finishedevent.trigger()



