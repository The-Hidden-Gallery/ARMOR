from configparser import ConfigParser
import pathlib
import os

# Config.ini file
_CONFIG_PATH = os.path.join(str(pathlib.Path(__file__).parent.resolve()),"config.ini")

class ParameterNotFoundError(Exception):
    """ The parameter indicated could not be found at the config.ini file. """

class Configuration:
    """ Controller class for configuration data access."""

    @staticmethod
    def set_config_param(section: str, param_key: str, param_value) -> None:
        """ Sets the parameter in the section at the configuration file path specified """
        try:
            # Creates the configParser
            cp = ConfigParser()
            # Reads the configuration file
            cp.read(_CONFIG_PATH)
            # Sets the new parameters
            try:
                # Sets the new parameter in the existing section
                cp[section][param_key] = param_value
            except KeyError:
                # Createsa new section with the new parameter
                cp[section] = {param_key: param_value}
            # Saves parameters in configuration file
            with open(_CONFIG_PATH, 'w') as configFile:
                cp.write(configFile)
        except:
            # Something went wrong
            print("[Configuration]:  Something went wrong while saving the configuration!")

    @staticmethod
    def get_config_param(section: str, param: str) -> str:
        """ Gets the parameter in the section at the configuration file path specified """
        try:
            # Creates the configParser
            cp = ConfigParser()
            # Reads the configuration file
            cp.read(_CONFIG_PATH)
            # Returns the parameter value 
            param_value = cp[section].get(param)
            if param_value is not None:
                # Returns the parameter read
                return param_value
            else:
                raise ParameterNotFoundError(section, param)
        except ParameterNotFoundError:
            print(f"[Error] Parameter {param} could not be found in Section{section}!")