import importlib.util
import inspect
import logging
import pathlib
import re
from importlib.machinery import ModuleSpec
from inspect import BoundArguments
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Tuple
from weakref import ref

from router.command import Command
from router.component import Component
from router.error.component import (ComponentAccessError, ComponentError,
                                    InvalidInitializerError)
from router.error.handler import (HandlerAccessError, HandlerError,
                                  HandlerExecutionError, HandlerLoadError,
                                  HandlerLookupError, HandlerPrefixError)
from router.package import Package
from router.registration import Registration

logging.info('TOP LEVEL STATEMENT!')

class Entry():

    @property
    def package(self) -> str:
        return self._package
    
    @property
    def component(self) -> str:
        return self._component
    
    @property
    def command(self) -> str:
        return self._command

    def __init__(self, package: str, component: str, command: str) -> None:
        self._package: str = package
        self._component: str = component
        self._command: str = command

class Handler():

    @property
    def features(self) -> Dict[str, str]:
        return {
            'HDKI': 'Hyphen Delimited Keyword Injection',
            'SDDMI': 'Single Directory Dynamic Module Import',
        }

    @property
    def registry(self) -> Dict[str, Entry]:
        return self._registry

    def __init__(self):
        """"""

        # initialize the registry
        self._registry: Dict[str, Entry] = dict()
        # initialize the package dictionary
        self._packages: Dict[str, Package] = dict()
        

    def load(self, directory: Path, extension: str = 'py'):
        """"""

        # resolve the provided directory path
        directory: Path = directory.resolve()
        logging.debug('Resolved provided directory to %s', str(directory))

        # if the provided directory doesn't exist
        if not directory.exists():
            raise HandlerLoadError(directory, f'\'{directory.name}\' does not exist at path {directory.parent}')

        # get all paths for files in the provided directory
        pattern: str = f'*.{extension}'
        references: List[Path] = [reference for reference in directory.glob(pattern) if reference.is_file()]
        logging.debug('Found %s %s files in %s', len(references), extension, str(directory))

        for reference in references:
            try:
                package: Package = Package(reference)
                for component in package.components.values():
                    for command in component.commands.values():
                        self._registry[command.name] = Entry(package.name, component.name, command.name)
            except ImportError as error:
                logging.warn('Package assembly failed for file %s: %s', reference.name, error)
            except Exception as error:
                logging.error(error)
                raise
            else:
                self._packages[package.name] = package
                


    def unused_function(self):
        # for each python file path
        for file_reference in references:
            try:
                # get the module from the file
                module: ModuleType = self.import_module(file_reference)
                # package the module into a list of components
                components: List[Component] = self.unpack_module(module)

                # for each obtained component
                for component in components:
                    # add the component
                    self.add(component)

            # if an error occurs with component initialization
            except HandlerLoadError as handlerLoadError:
                logging.error(handlerLoadError)

            # if the component's initializer is not supported
            except InvalidInitializerError as invalidInitializerError:
                logging.error(invalidInitializerError)

    def import_module(self, reference: pathlib.Path) -> ModuleType:
        """
        Import a module given the containing file's path.

        Notes:
            - Module spec is obtained via `importlib.util.spec_from_file_location`
            - Module is generated from spec via `importlib.util.module_from_spec`
        """

        logging.info('%s module: found at %s', reference.stem, str(reference))

        # get module spec from module name and path
        spec: ModuleSpec = importlib.util.spec_from_file_location(reference.stem, reference.resolve())
        logging.debug('%s module: obtained spec', spec.name)

        # create the module from the spec
        module: ModuleType = importlib.util.module_from_spec(spec)
        logging.debug('%s module: assembled from spec', spec.name)

        try:
            logging.debug('%s module: executing...', spec.name)
            # execute the created module
            spec.loader.exec_module(module)
            logging.debug('%s module: execution complete', spec.name)

        # if the module tries to import a module that hasn't been installed
        except (ImportError, ModuleNotFoundError) as error:
            # raise exception
            raise HandlerLoadError(reference, str(error), error)
        
        # return the module
        return module

    def unpack_module(self, module: ModuleType) -> List[Component]:
        """
        Unpack a list of components from a module.
        """

        logging.debug('%s module: beginning component search', module.__name__)

        # get each type member in the module instance
        members: List[Tuple[str, type]] = [member for member in inspect.getmembers(module, inspect.isclass)]
        logging.debug('%s module: found %s available members', module.__name__, len(members))

        logging.debug('%s module: beginning component initialization process', module.__name__)
        # initialize component from each member (excluding classes imported from other modules)
        components: List[Component] = [Component(class_name, class_object) for class_name, class_object in members if class_object.__module__ == module.__name__]
        logging.info('%s module: initialized %s components', module.__name__, len(components))
        
        # return component list
        return components

    def add(self, component: Component):
        """
        """

        for command in component.commands:
            # generate a command registration
            registration: Registration = Registration(component, command)
            # add registration to registrations list
            self._registrations.append(registration)

    def get(self, command_name: str) -> Registration:
        """
        """

        # get all registrations containing a command with a matching name
        registrations: List[Registration] = [registration for registration in self._registrations if registration.command.name == command_name]
        # if exactly one registration was found
        if len(registrations) == 1:
            # return the registration's command         
            return registrations[0]
        # if zero or many registrations were found
        else:
            # raise lookup error
            raise HandlerLookupError(command_name, f'{len(registrations)} registrations found for \'{command_name}\'')



        """
        Get a component instance from the components dict

        Raises:
            ComponentLookupError - upon failure to get the component name given the command name from the commands dict
            ComponentAccessError - upon failure to get the component instance given the component name from the components dict
        """
        try:
            component_name = self._commands[command_name]
        except KeyError:
            raise HandlerLookupError(command_name, Exception(f'Command \'{command_name}\' could not be found.'))
        try:
            component: Component = self._components[component_name]
        except KeyError:
            raise HandlerAccessError(component_name, Exception(f'Component \'{component_name}\' could not be found.'))
        return component

    async def process(self, prefix: str, message: str, *, optionals: Dict[str, object]=dict()):
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
                raise HandlerPrefixError(prefix, ValueError('Message to process does not begin with expected prefix.'))
            # get the prefixed command string from the match
            prefixed_command: str = command_match.group()
            # remove prefix from command
            command_name: str = re.sub(rf'^{command_prefix}', '', prefixed_command)

            parameter_prefix = '-'
            # compile regex for parameter/argument pairs
            parameter_argument_pair: re.Pattern = re.compile(rf'{parameter_prefix}[\w]+[\s]+(?:(?!\s\-).)*\b')
            ##parameter_argument_pair: re.Pattern = re.compile(rf'{parameter_prefix}[\w]+[\s]+[\w\d\s<!@>?\#\=\:\/\.]+\b')
            prefixed_parameter: re.Pattern = re.compile(rf'^{parameter_prefix}')

            # find all substrings that start with the parameter prefix and have arguments
            parameter_matches: List[str] = re.findall(parameter_argument_pair, message)
            # strip the parameter prefix from each parameter/argument combo
            parameter_matches: List[str] = [re.sub(prefixed_parameter, '', parameter_match) for parameter_match in parameter_matches]

            ### TODO: Factor out Discord-specific parameter manipulation
            ###
            # strip any user mention strings down to the author's id
            parameter_matches: List[str] = [re.sub(r'<@!', '', parameter_match) for parameter_match in parameter_matches]
            # strip any user mention strings down to the author's id (mobile)
            parameter_matches: List[str] = [re.sub(r'<@', '', parameter_match) for parameter_match in parameter_matches]
            # strip any voice channel mention strings down to the channel's id
            parameter_matches: List[str] = [re.sub(r'<#', '', parameter_match) for parameter_match in parameter_matches]
            ###
            ###

            # split the argument/parameter combo into tuple(parameter, argument)
            arguments: List[str] = [tuple(parameter_match.split(maxsplit=1)) for parameter_match in parameter_matches]
            # convert list of tuples to dictionary
            kwargs: Dict[str, str] = { argument[0] : argument[1] for argument in arguments }

            # create args list
            args: List = list()
            # run the command
            await self.run(command_name, args, kwargs, optionals)

        # if the message doesn't start with a prefix
        except HandlerPrefixError:
            return
        except (HandlerError, ComponentError):
            raise

    async def run(self, command_name: str, args: List[Any], kwargs: Dict[str, str], optionals: Dict[str, Any] = dict()):
        """
        Run a command given its name, args and kwargs, as well as any optional objects the command requires.

        Raises:
            CommandAccessError - upon failure to get command signature from component
            ComponentAccessError - upon failure to get component from components dict
            HandlerRunError - upon failure to bind args and kwargs to command signature
        """

        try:
            entry: Entry = self._registry[command_name]
            package: Package = self._packages[entry.package]
            component: Component = package.components[entry.component]
            command: Command = component.commands[entry.command]
        except KeyError:
            logging.warn('Could not find command %s', command_name)
            raise
        
        # for each optional keyvalue pair passed in through contructor
        for optional_key, optional_value in optionals.items():
            # if the command's signature contains a parameter matching the optional key
            if optional_key in command.signature.parameters.keys():
                # add the correlated optional value to kwargs
                kwargs[optional_key] = optional_value

        try:
            # bind the processed arguments to the command signature
            bound_arguments: BoundArguments = command.signature.bind(*args, **kwargs)
            # run the command with the assembled signature
            await command.run(bound_arguments)
        except TypeError as typeError:
            raise HandlerExecutionError(command_name, typeError)
