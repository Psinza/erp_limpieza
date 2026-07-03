import os
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

class LogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Seguridad: Solo superusuarios pueden ver logs en tiempo real
        if not self.scope["user"].is_authenticated or not self.scope["user"].is_superuser:
            await self.close()
            return
            
        await self.accept()
        self.log_path = os.path.join(settings.BASE_DIR, 'logs', 'erp.log')
        self.streaming = True
        self.stream_task = asyncio.create_task(self.stream_logs())

    async def disconnect(self, close_code):
        self.streaming = False
        if hasattr(self, 'stream_task'):
            self.stream_task.cancel()

    async def stream_logs(self):
        try:
            if not os.path.exists(self.log_path):
                await self.send(text_data="[SISTEMA] El archivo de log no existe.")
                return

            with open(self.log_path, 'r', encoding='utf-8') as f:
                # Ir al final del archivo para transmitir solo contenido nuevo
                f.seek(0, os.SEEK_END)
                
                while self.streaming:
                    line = f.readline()
                    if line:
                        await self.send(text_data=line.strip())
                    else:
                        # Pausa corta para no saturar el CPU
                        await asyncio.sleep(0.5)
        except Exception as e:
            await self.send(text_data=f"[ERROR] Stream interrumpido: {str(e)}")