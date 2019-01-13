import logging
import subprocess
from collections import namedtuple

from uroute.config import Config


Program = namedtuple('Program', ('name', 'command'))

log = logging.getLogger(__name__)


class Uroute:
    def __init__(self, url, verbose=False):
        self.url = url
        self.verbose = verbose
        self.default_program = None

        # Load config
        self.config = Config()
        self._init_logging()
        self.programs = self._load_config_programs()

    def _init_logging(self):
        logging_config = {
            'level': 'DEBUG',
            'format': '%(levelname)s %(message)s',
        }

        if 'logging' in self.config:
            logging_config.update(dict(self.config['logging']))

        logging.basicConfig(**logging_config)

    def _load_config_programs(self):
        programs = {}
        for section_name in self.config.sections():
            if not section_name.startswith('program:'):
                continue

            prog_id = section_name[len('program:'):]
            if prog_id in programs:
                log.warn('Duplicate config for program %s', prog_id)
            section = self.config[section_name]

            programs[prog_id] = Program(
                name=section['name'],
                command=section['command'],
            )

        if 'uroute' in self.config:
            section = self.config['uroute']

            if 'default_program' in section:
                self.default_program = section['default_program']

        return programs

    def get_program(self, prog_id=None):
        if not self.programs:
            raise ValueError('No programs configured')

        if prog_id is None:
            prog_id = self.default_program

        if not prog_id:
            return self.programs[self.programs.keys()[0]]

        if prog_id not in self.programs:
            raise ValueError('Unknown program ID: {}'.format(prog_id))
        return self.programs[prog_id]

    def get_command(self, program):
        if not isinstance(program, Program):
            program = self.get_program(program)
        return program.command

    def run_with_url(self, command):
        if self.verbose > 0:
            log.debug('Routing URL %s to command: %s', self.url, command)

        run_args = [
            arg == '@URL' and self.url or arg for arg in command.split()
        ]

        if self.url not in run_args:
            run_args.append(self.url)

        log.info(repr(run_args))
        subprocess.run(run_args)