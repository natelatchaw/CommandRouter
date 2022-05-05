from inspect import BoundArguments, Signature
from router.command import Command
from router.component import Component


class Registration():
    """
    """

    @property
    def key(self) -> str:
        return '.'.join(self._component.name, self._command.name)

    @property
    def component(self) -> Component:
        return self._component

    @property
    def command(self) -> Command:
        return self._command

    @property
    def signature(self) -> Signature:
        return self.command.signature


    def __init__(self, component: Component, command: Command):
        self._component = component
        self._command = command


    async def run(self, arguments: BoundArguments):
        """
        Runs the command from the scope of the component.
        The executed command is awaited if it is asynchronous.
        """
        
        # run the command provided the command details
        await self._component.run_command(self._command.name, arguments)