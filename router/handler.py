import pathlib
import inspect
import importlib.util
import re
from typing import Dict, List
from router.error.component import ComponentLoadError
from router.component import Component, InvalidInitializerError, InvalidCommandError

class Handler():
    def __init__(self):        
        # map command names to component names
        self._commands: Dict[str, str] = dict()
        # map component names to components
        self._components: Dict[str, Component] = dict()

    def load(self, components_folder: pathlib.Path=None):
        try:
            # if the components folder path was not provided
            if not components_folder:
                raise TypeError('Could not determine components folder.')
            # generate and resolve path of components folder
            components_path = pathlib.Path(components_folder).resolve()
            # if the provided folder doesn't exist
            if not components_path.exists():
                # raise exception
                raise ValueError(f'Folder \'{components_path}\' does not exist at path {components_path.absolute().parent}.')
            print(f'Looking for components in {components_path}...')
        except (TypeError, ValueError):
            raise

        # get all python file paths in the components directory
        modules: List[pathlib.Path] = [module for module in components_path.glob('*.py') if module.is_file()]
        # for each python file path
        for module in modules:
            try:
                # generate ModuleInterface object from module path
                packaged_components: List[Component] = self.package(module)
                # for each packaged module in the list of packaged modules
                for packaged_component in packaged_components:
                    # add Component object to Handler's tracked components
                    self.add(packaged_component)
            # if an error occurs with component initialization
            except ComponentLoadError as componentLoadError:
                print(componentLoadError)
            # if the component's initializer is not supported
            except InvalidInitializerError as invalidInitializerError:
                print(invalidInitializerError)
            
    def package(self, module: pathlib.Path) -> List[Component]:
        # get module spec from module name and path
        spec = importlib.util.spec_from_file_location(module.stem, module.resolve())
        # create the module from the spec
        created_module = importlib.util.module_from_spec(spec)
        try:
            # execute the created module
            spec.loader.exec_module(created_module)
        # if the module tries to import a module that hasn't been installed
        except ModuleNotFoundError as moduleNotFoundError:
            # raise exception
            raise ComponentLoadError(module.stem, moduleNotFoundError)
        # get each class member in the module (excluding classes imported from other modules)
        members = [member for member in inspect.getmembers(created_module, inspect.isclass) if member[1].__module__ == created_module.__name__]
        # initialize Component object for each class in module
        components: List[Component] = [Component(component_name, component_class) for component_name, component_class in members]
        return components

    def add(self, component: Component):
        # for each command's name in the component
        for command_name in component.commands.keys():
            # TODO: command_name not guaranteed to be unique across components, overwriting is possible here
            # add the command-to-component mapping
            self._commands[command_name] = component.name
        # add the component-name-to-component mapping
        self._components[component.name] = component

    def get(self, command_name: str) -> Component:
        try:
            component_name = self._commands[command_name]
        except KeyError:
            raise CommandLookupError(command_name)
        try:
            component: Component = self._components[component_name]
        except KeyError:
            raise ComponentLookupError(component_name)
        return component

    async def process(self, prefix: str, message: str, *, optionals: Dict=dict()):
        # filter non-string message parameters
        if not isinstance(message, str):
            raise TypeError(f'Cannot process object that is not of type {type(str)}')
        # try to parse a command from the message
        try:
            command_prefix: str = prefix

            # get command from message
            command_match: re.Match = re.match(rf'^{command_prefix}[\w]+', message)
            # if the prefixed command could not be found at the beginning of the message
            if not command_match:
                raise TypeError(f'Message does not begin with prefix ({command_prefix})')
            # get the prefixed command string from the match
            prefixed_command: str = command_match.group()
            # remove prefix from command
            command_name: str = re.sub(rf'^{command_prefix}', '', prefixed_command)

            parameter_prefix = '-'
            # compile regex for parameter/argument pairs
            parameter_argument_pair: re.Pattern = re.compile(rf'{parameter_prefix}[\w]+[\s]+[\w\d\s<!@>]+\b')
            prefixed_parameter: re.Pattern = re.compile(rf'^{parameter_prefix}')

            # find all substrings that start with the parameter prefix and have arguments
            parameter_matches = re.findall(parameter_argument_pair, message)
            # strip the parameter prefix from each parameter/argument combo
            parameter_matches = [re.sub(prefixed_parameter, '', parameter_match) for parameter_match in parameter_matches]
            # strip any mention strings down to the author's id
            parameter_matches = [re.sub(r'<@!', '', parameter_match) for parameter_match in parameter_matches]
            # split the argument/parameter combo into tuple(parameter, argument)
            arguments = [tuple(parameter_match.split(maxsplit=1)) for parameter_match in parameter_matches]
            # convert list of tuples to dictionary
            kwargs = { argument[0] : argument[1] for argument in arguments }

            # create args list
            args = list()

            try:
                # try to get the relevant component
                component = self.get(command_name)
                # get the command's command signature
                command_signature = component.get_command_signature(command_name)
                
                # for each optional keyvalue pair passed in through contructor
                for optional_key, optional_value in optionals.items():
                    # if the command's signature contains a parameter matching the optional key
                    if optional_key in command_signature.parameters.keys():
                        # add the correlated optional value to kwargs
                        kwargs[optional_key] = optional_value

                # bind the processed arguments to the command signature
                bound_arguments = command_signature.bind(*args, **kwargs)
                # run the command with the assembled signature
                await component.run_command(command_name, bound_arguments)

            except HandlerError as handlerError:
                raise handlerError

            except TypeError as typeError:
                raise CommandHandlingError(command_name, typeError)

            except InvalidCommandError as invalidCommandError:
                raise invalidCommandError
        
        # if a valid command could not be parsed from the message
        except TypeError:
            # do nothing
            pass
            

class HandlerError(Exception):
    """Base exception class for the Handler class."""
    pass

class LookupError(HandlerError):
    """Base exception class for command lookup-related errors."""
    pass

class CommandHandlingError(HandlerError):
    """Raised when an exception occurs during the handling of a command."""

    def __init__(self, command_name: str, typeError: TypeError):
        self.command_name = command_name
        self.typeError = typeError

    def __str__(self):
        return f'Error in {self.command_name} command: {self.typeError}'

class CommandLookupError(LookupError):
    """Raised when the commands dict returns a KeyError when looking up a command name."""

    def __init__(self, command_name):
        self.command_name = command_name

    def __str__(self):
        return f'Could not find specified command: {self.command_name}.'

class ComponentLookupError(LookupError):
    """Raised when the components dict returns a KeyError when looking up a component name."""

    def __init__(self, component_name):
        self.component_name = component_name

    def __str__(self):
        return f'Could not find specified component: {self.component_name}.'