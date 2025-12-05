"""
Send command to terminal session via gRPC.

Usage:
    poetry run python manage.py terminal_send --list
    poetry run python manage.py terminal_send --all "ls -la"
    poetry run python manage.py terminal_send --all "How are you?"
    poetry run python manage.py terminal_send abc123 "echo hello"

Sends text + Enter automatically. Works with interactive apps like Claude Code.
"""

import asyncio
import grpc
from django.core.management.base import BaseCommand

from apps.terminal.models import TerminalSession


class Command(BaseCommand):
    help = 'Send command to terminal session via gRPC'

    def add_arguments(self, parser):
        parser.add_argument(
            'session_id',
            nargs='?',
            help='Session ID (first 8 chars is enough)'
        )
        parser.add_argument(
            'command',
            nargs='?',
            help='Command to send'
        )
        parser.add_argument(
            '--list', '-l',
            action='store_true',
            help='List active terminal sessions'
        )
        parser.add_argument(
            '--all', '-a',
            type=str,
            metavar='COMMAND',
            help='Send COMMAND to ALL active sessions'
        )
        parser.add_argument(
            '--host',
            default='localhost',
            help='gRPC server host (default: localhost)'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=50051,
            help='gRPC server port (default: 50051)'
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_sessions()
            return

        all_command = options['all']
        if all_command:
            asyncio.run(self.send_to_all(all_command, options['host'], options['port']))
            return

        session_id = options['session_id']
        command = options['command']

        if not session_id:
            self.stderr.write(self.style.ERROR('Session ID required'))
            self.list_sessions()
            return

        if not command:
            self.stderr.write(self.style.ERROR('Command required'))
            return

        asyncio.run(self.send_command(session_id, command, options['host'], options['port']))

    def list_sessions(self):
        """List all active terminal sessions."""
        from django.utils import timezone
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(seconds=60)
        sessions = TerminalSession.objects.filter(
            status=TerminalSession.Status.CONNECTED,
            last_heartbeat_at__gte=cutoff
        ).order_by('-connected_at')

        if not sessions.exists():
            self.stdout.write(self.style.WARNING('No active sessions'))
            return

        self.stdout.write(self.style.SUCCESS('\nActive Terminal Sessions:'))
        self.stdout.write('-' * 70)

        for session in sessions:
            age = int(session.heartbeat_age_seconds)
            self.stdout.write(
                f"  {str(session.id)[:8]}  "
                f"{session.electron_hostname or 'unknown':20}  "
                f"{session.shell:12}  "
                f"heartbeat: {age}s ago"
            )

        self.stdout.write('')

    async def send_command(self, session_id: str, command: str, host: str, port: int):
        """Send command to terminal via gRPC."""
        try:
            if len(session_id) < 36:
                session = await TerminalSession.objects.filter(
                    id__startswith=session_id,
                    status=TerminalSession.Status.CONNECTED
                ).afirst()
            else:
                session = await TerminalSession.objects.aget(id=session_id)
        except TerminalSession.DoesNotExist:
            session = None

        if not session:
            self.stderr.write(self.style.ERROR(f'Session not found: {session_id}'))
            return

        await self._send_to_session(session, command, host, port)

    async def send_to_all(self, command: str, host: str, port: int):
        """Send command to all active sessions."""
        from django.utils import timezone
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(seconds=60)
        sessions = [s async for s in TerminalSession.objects.filter(
            status=TerminalSession.Status.CONNECTED,
            last_heartbeat_at__gte=cutoff
        )]

        if not sessions:
            self.stderr.write(self.style.WARNING('No active sessions'))
            return

        self.stdout.write(self.style.SUCCESS(f'\nSending to {len(sessions)} session(s):'))
        self.stdout.write(f'Command: {repr(command)}')
        self.stdout.write('-' * 70)

        success_count = 0
        for session in sessions:
            ok = await self._send_to_session(session, command, host, port)
            if ok:
                success_count += 1

        self.stdout.write('-' * 70)
        self.stdout.write(f'Done: {success_count}/{len(sessions)} success')

    async def _send_to_session(self, session, command: str, host: str, port: int) -> bool:
        """Send to single session. Returns True on success."""
        try:
            from apps.terminal.grpc.services.generated import terminal_streaming_service_pb2 as pb2
            from apps.terminal.grpc.services.generated import terminal_streaming_service_pb2_grpc as pb2_grpc
        except ImportError:
            self.stderr.write(self.style.ERROR('Proto files not generated'))
            return False

        session_id = str(session.id)
        target = f"{host}:{port}"

        try:
            async with grpc.aio.insecure_channel(target) as channel:
                stub = pb2_grpc.TerminalStreamingServiceStub(channel)

                # Send text (all at once)
                if command:
                    data = command.encode('utf-8')
                    request = pb2.SendInputRequest(session_id=session_id, data=data)
                    response = await stub.SendInput(request)
                    if not response.success:
                        return False

                # Small delay before Enter (let app process the text)
                await asyncio.sleep(0.01)

                # Send Enter (\r = 0x0d)
                request = pb2.SendInputRequest(session_id=session_id, data=b'\r')
                response = await stub.SendInput(request)

                age = int(session.heartbeat_age_seconds)
                hostname = session.electron_hostname or 'unknown'

                if response.success:
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✅ {session_id[:8]}  {hostname:20}  heartbeat: {age}s'
                    ))
                    return True
                else:
                    self.stdout.write(self.style.ERROR(
                        f'  ❌ {session_id[:8]}  {hostname:20}  {response.error}'
                    ))
                    return False

        except grpc.aio.AioRpcError as e:
            self.stderr.write(self.style.ERROR(f'gRPC error: {e.code()}: {e.details()}'))
            return False
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))
            return False
