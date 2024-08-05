from typing import List, Any


class Command:
    name: str
    args: List[str]
    subcommand: Any


def parse_args(args: List[str]) -> Command:
    cmd = Command()
    current_cmd = None
    for a in args:
        if not a.startswith('-'):
            if not current_cmd:
                current_cmd = cmd
                current_cmd.name = a
            else:
                current_cmd.subcommand = Command()
                current_cmd = current_cmd.subcommand
                current_cmd.name = a
        else:
            if not current_cmd:
                raise Exception("Unable to parse command")
            else:
                current_cmd.args.append(a)
                # todo. how to determine if next value is an option to the arg or a subcommand

    return cmd