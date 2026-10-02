from channels.generic.websocket import AsyncJsonWebsocketConsumer


class FormReportConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        print("CONNECT")

        self.form_id = self.scope["url_route"]["kwargs"]["form_id"]
        self.group_name = f"form_report_{self.form_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

        print("ACCEPTED")

    async def disconnect(self, close_code):
        print("DISCONNECT:", close_code)

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    async def receive_json(self, content, **kwargs):
        print("RECEIVED:", content)

    async def report_update(self, event):
        print("REPORT UPDATE:", event)

        await self.send_json(
            {
                "type": "report.update",
                "data": event["data"],
            }
        )
